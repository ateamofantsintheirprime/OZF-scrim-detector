from league_models import League, Roster, Player, Log, PlayerLogTracker, Game, TeamInstance
from datetime import datetime, timedelta
from database.methods import league, tracker, log, roster, player, game
import requests, json
from database_helper import expunge_unicode
from typing import Union
from requests import Response
from time import sleep
from copy import deepcopy
from threading import Thread, Lock, Event
from concurrent.futures import ThreadPoolExecutor
from random import random
from debug import debug_print
import copy

class LogSearcher():
	"""This is designed to search for ALL logs of a set of targets
	ONLY FOR LOGS.TF API"""
	def __init__(self):

		# TODO: REPLACE GET TARGET_ID_64S WITH GET TARGET URLS
		# AND WE CAN JUST DEFINE HOW TO GET THE DESIRED URL FROM THE TARGET OBJECTS
		# IN THE SUBCLASSES LOOK AT HOW SIMILAR THE GET_TARGET_ID64 FUNCION IS WITH GET TARGET LOGS

		self.existing_logs: set[Log]= set()
		self.existing_player_logs : dict[int:set[Log]] = set()

		self.id_counter = 0

		self.job_queue = PriorityQueue()
		self.result_queue = PriorityQueue()

		self.awaiting_results:list[int] = []

		self.targets:Union[League,Roster,Player] = []
		self.targeted_id_64s: set[int] = set()

		# Synchronisation flag
		self.complete = Event()
		self.requester_waiting = Event()
		self.processor_waiting = Event()

		# Workers
		# Rename this shit lol
		self.threaded_requester = ThreadedRequester(self.job_queue, self.result_queue, self.requester_waiting, self.complete)
		self.requesting_thread = Thread(target=self.threaded_requester.start)
		self.processing_thread = Thread(target=self.process_result_queue)


	# def get_existing_logs_backgrounded(self):
	# 	self._e_t.start()


	def get_all_logs(self): # Merge this with get existing player logs and call it just "prep" in advance of merge with GameRequester
		# This should only get logs of the targets, its faster
		self.existing_logs = set(log.get_all_logs())

	def get_target_id64s(self):
		"""This requires all leagues, rosters and players are already in the database
		This needs to exclude players who's log trackers are already up to date"""
		assert len(self.targets) > 0
		self.targeted_id_64s.clear()
		while len(self.targets) > 0:
			target = self.targets.pop()
			if isinstance(target, League):
				self.targeted_id_64s.update(league.get_league_player_id_64s(target.id))
			elif isinstance(target, Roster):
				self.targeted_id_64s.update(roster.get_roster_player_ids(target.id))
			elif isinstance(target, Player):
				self.targeted_id_64s.add(target.id_64)
			elif isinstance(target, list):
				self.targets.extend(target)
			elif isinstance(target, set):
				self.targets.extend(list(target))
		
		# Filter out players whos log trackers 1) Exist 2) Are not out of date 
		filter_out_ids = set()
		for id_64 in self.targeted_id_64s:
			log_tracker = tracker.get_log_tracker(id_64)
			if not log_tracker is None and not tracker.expired(log_tracker):
				filter_out_ids.add(id_64)

		# Keep only targeted id_64s that arent filtered out 
		self.targeted_id_64s.difference_update(filter_out_ids)

	def get_existing_data(self):
		self.existing_player_logs.clear()
		self.existing_player_logs = player.get_existing_logs(self.targeted_id_64s)
		self.existing_logs.clear()
		self.existing_logs = log.get_all_logs()

	def search_url(self,id_64:int, offset:int) -> str:
		return f"http://logs.tf/api/v1/log?player={id_64}&offset={offset}"

	def get_initial_jobs(self):
		self.get_target_id64s()
		self.job_queue.clear()
		self.awaiting_results.clear()
		for id_64 in self.targeted_id_64s:
			url = self.search_url(id_64=id_64,offset=0)
			job = Job(self.id_counter,url)
			self.awaiting_results.append(job.id)
			self.job_queue.add_value(job)
			self.id_counter += 1

	def process_result_queue(self):
		while not self.complete.is_set():
			result:Result = self.result_queue.pop_value()
			if result is None:
				if len(self.awaiting_results) == 0:
					self.processor_waiting.set()
				sleep(1)
				continue
			if result.id in self.awaiting_results:
				# print("PROCESSOR: removed a result i was waiting for")
				self.process_result(result)
				self.awaiting_results.remove(result.id)
			else:
				raise Exception
			if len(self.awaiting_results) > 0:
				self.processor_waiting.clear()


	def process_result(self, result:'Result'):
		response=result.response
		# Step 1 parse response
		data = json.loads(expunge_unicode(response.text))
		id_64 = int(data['parameters']['player'])
		results = int(data['results'])
		total = int(data['total'])
		offset = int(data['parameters']['offset'])
		# Step 2 check for an existing log tracker
		player_log_tracker = tracker.get_log_tracker(id_64)
		# Step 2.5 either use the existing one or make a new one
		if player_log_tracker is None:
			tracker.insert_log_tracker(
				id_64=id_64,
				num_logs_total=total,
				num_logs_tracked=0,
				valid_until=datetime.today()+timedelta(days=3))
		else:
			tracker.update_log_tracker(id_64,new_total=total)	
		# We request it again to get the version with the updated total
		player_log_tracker = tracker.get_log_tracker(id_64)
		
		# Step 3 check if log tracker is tracking all player logs
		if player_log_tracker.num_logs_tracked == player_log_tracker.num_logs_total:
			# The log tracker is up to date -> no logs need to be added.
			return
		elif player_log_tracker.num_logs_tracked < player_log_tracker.num_logs_total:
			# Step 4 if not then add them
			logs_set = {
				Log(
					id=int(l['id']),
					date=datetime.fromtimestamp(l['date']),
					map_name=l['map']
					)
				for l in data['logs']
			}
			self.add_logs_to_database(logs_set, player_log_tracker)
			
			# Step 5 Check if more logs need to be downloaded for this person
			if offset+results < total and player_log_tracker.num_logs_tracked < total:
				# There are more logs to request for this guy!
				url = self.search_url(id_64=id_64,offset=offset+1000)
				new_job= Job(
					id=result.id, # Use the same id, it will be free
					url=url,
					priority=True
				)
				self.awaiting_results.append(new_job.id)
				self.job_queue.add_value(new_job)
			else:
				print(f"PROCESSOR: Remaining jobs: {len(self.awaiting_results)}")

		else:
			print("PROCESSOR: log tracker should never be tracking more logs than exist")
			raise Exception

	def add_logs_to_database(self, log_set:set[Log], player_log_tracker: PlayerLogTracker):

		# Set operations are very fast!
		existing_player_logs = self.existing_player_logs[player_log_tracker.id_64]

		# Remove the logs that the player is already recorded in
		add_player_to = log_set.difference(existing_player_logs)
		add_player_to_ids = [l.id for l in add_player_to]
		# Remove the logs that are already in the database
		add_to_database = log_set.difference(self.existing_logs)
		self.existing_logs.update(add_to_database)

		self.existing_player_logs[player_log_tracker.id_64].update(add_player_to)
		log.add_log_batch(copy.deepcopy(add_to_database))

		log.add_player_to_log_batch_id(player_log_tracker.id_64, add_player_to_ids)

		tracker.update_log_tracker(
			player_log_tracker.id_64,
			num_logs_tracked=player_log_tracker.num_logs_tracked + len(add_player_to)
		)

	def execute_task(self):
		self.get_initial_jobs()
		self.get_existing_data()

		print("ORGANISER: starting requester")
		self.requesting_thread.start()
		print("ORGANISER: starting processor")
		self.processing_thread.start()

		self.wait_until_threads_complete()

	def wait_until_threads_complete(self):
		while True:
			self.processor_waiting.wait()
			self.requester_waiting.wait()
			sleep(3)
			# We want a 3 second period where both threads are quiet
			if self.processor_waiting.is_set() and self.requester_waiting.is_set():
				# Both threads were silent for 3 seconds straight = done
				self.complete.set()
				self.processing_thread.join()
				self.requesting_thread.join()
				break
		print("threads complete")

class GameRequester(LogSearcher):
	"""This is designed to request information on a set of logs
	ONLY FOR LOGS.TF API"""
	def __init__(self):
		super().__init__()
		# self._e_t =  Thread(target=self.get_all_game_ids)
		self.existing_game_ids : set[Game] = set()
		self.existing_team_instances : set[TeamInstance] = set()
		self.target_logs : set[Log] = set()

	def get_target_logs(self):
		assert len(self.targets) > 0
		self.target_logs.clear()
		while len(self.targets) > 0:
			target = self.targets.pop()
			if isinstance(target, League):
				self.target_logs.update(league.get_league_logs(target.id))
			elif isinstance(target, Roster):
				self.target_logs.update(roster.get_roster_logs(target.id, 4))
			elif isinstance(target, Player):
				self.target_logs.update(player.get_player_logs(target.id_64))
			elif isinstance(target, list):
				self.targets.extend(target)
			elif isinstance(target, set):
				self.targets.extend(list(target))

		# Filter out logs that we already have the games of
		filter_out_logs = set()
		for log in self.target_logs:
			if log.id in self.existing_game_ids:
				filter_out_logs.add(log)
		
		self.target_logs.difference_update(filter_out_logs)

	# def get_all_game_ids_backgrounded(self):
	# 	self._e_t.start()

	def get_all_game_ids(self):
		self.existing_game_ids = game.get_all_game_ids()
	
	def get_all_team_instances(self):
		self.existing_team_instances = roster.get_all_team_instances()

	def request_url(self,log_id:int):
		return f"http://logs.tf/api/v1/log/{log_id}"

	def get_existing_data(self):
		self.existing_game_ids.clear()
		self.existing_team_instances.clear()
		self.get_all_game_ids()
		self.get_all_team_instances()

	def get_initial_jobs(self):
		self.get_target_logs()
		self.job_queue.clear()
		self.awaiting_results.clear()
		for log in self.target_logs:
			url = self.request_url(log.id)
			job = Job(self.id_counter,url)
			self.awaiting_results.append(job.id)
			self.job_queue.add_value(job)
			self.id_counter += 1
		print(self.job_queue)

	def process_result_queue(self):
		return super().process_result_queue()

	def process_result(self, result:'Result'):
		response=result.response
		# Step 1 parse response
		data = json.loads(expunge_unicode(response.text))
		red_score = data['teams']['Red']['score']
		blue_score = data['teams']['Blue']['score']
		red_player_ids : list[str]
		blue_players : list[str]
		print(f"PROCESSOR: Remaining jobs: {len(self.awaiting_results)}")

	# def execute_task(self):
	# 	self.get_initial_jobs()
	# 	self.get_existing_data()

	# 	print("ORGANISER: starting requester")
	# 	self.requesting_thread.start()
	# 	print("ORGANISER: starting processor")
	# 	self.processing_thread.start()
	# 	self.wait_until_threads_complete()


class Job():
	def __init__(self, id:int, url:str, priority:bool=False):
		self.id=id
		self.url=url
		self.priority=priority
	def execute(self) -> 'Result':
		return Result(
			id=self.id,
			response=requests.get(self.url),
			priority=self.priority)

class Result():
	def __init__(self, id:int, response:Response,priority:bool):
		self.id=id
		self.response=response
		self.priority=priority
	def status(self):
		return self.response.status_code

class PriorityQueue():
	def __init__(self):
		self.regular = []
		self.priority = []
		self.regular_lock = Lock()
		self.priority_lock = Lock()

	def clear(self):
		self.priority_lock.acquire(blocking=True)
		self.priority.clear()
		self.priority_lock.release()
		self.regular_lock.acquire(blocking=True)
		self.regular.clear()
		self.regular_lock.release()

	def add_value(self,value:Union[Job,Result]):
		if value.priority:
			self.priority_lock.acquire(blocking=True)
			self.priority.append(value)
			self.priority_lock.release()
		else:
			self.regular_lock.acquire(blocking=True)
			self.regular.append(value)
			self.regular_lock.release()

	def pop_value(self):
		if self.priority_lock.acquire(blocking=True):
			# If this blocks, that means priority jobs are being added
			if len(self.priority) > 0:
				value = self.priority.pop()
				self.priority_lock.release()
				return value
			else:
				self.priority_lock.release()
		if self.regular_lock.acquire(blocking=True):
			if len(self.regular) > 0:
				value = self.regular.pop()
				self.regular_lock.release()
				return value
			else:
				self.regular_lock.release()
		# print("both queues unlocked and empty")
		return None
	
	def __str__(self):
		return f"""Regular queue: {self.regular}\nPriority queue:{self.priority}"""
	def __len__(self):
		return len(self.priority) + len(self.regular)

class ThreadedRequester():
	def __init__(self, job_queue:PriorityQueue, result_queue:PriorityQueue, requester_waiting:Event, complete:Event):
		self.outer_job_queue = job_queue
		self.outer_result_queue = result_queue

		self.requester_waiting = requester_waiting
		self.complete = complete

		self.max_thread_count = 50

		self.inner_job_queue = PriorityQueue()
		self.inner_result_queue = PriorityQueue()

	def job_dispatcher(self):
		awaiting_values = []
		dispatcher_sleep_time = .1
		while not self.complete.is_set():
			# Put jobs on the inner queue
			job:Job = self.outer_job_queue.pop_value()
			if not job is None:
				# print(f"DISPATCHER: Adding a job to the inner queue (queue length:{len(self.inner_job_queue)})")
				self.requester_waiting.clear()
				awaiting_values.append(job.id)
				self.inner_job_queue.add_value(job)
			# Take results off the inner queue
			result:Result = self.inner_result_queue.pop_value()
			if not result is None:
				# print(f"DISPATCHER: taking a result off the inner queue, {len(awaiting_values)}")
				awaiting_values.remove(result.id) # This should never raise a value error
				self.outer_result_queue.add_value(result)
				dispatcher_sleep_time /= 3
			# Check if there are any jobs in progress
			if job is None and len(awaiting_values) == 0:
				# print("DISPATCHER: no jobs to execute and no in progress jobs")
				self.requester_waiting.set()
				sleep(1)
			# If there are jobs in progress but none to dispatch, then sleep for a bit
			elif job is None and result is None:
				# print(f"DISPATCHER: waiting for workers to complete requests {dispatcher_sleep_time}")
				sleep(dispatcher_sleep_time)
				dispatcher_sleep_time *= 1.5
				# Wait for one of the theads to finish their request

	def job_executor(self):
		sleep(random()*self.max_thread_count/2) # Give each worker a random offset to avoid synching up api spam
		sleep_time = 1.0
		backoff_rate = 1.7 # using prime numbers gives granualarity to sleep time.
		attack_rate = 1.3
		# print("WORKER: starting up worker")
		while not self.complete.is_set():
			# print("WORKER: worker about to grab a job")
			job:Job = self.inner_job_queue.pop_value()
			if job is None:
				sleep(1)
				# print("WORKER: waiting for a job to arrive")
				continue
			# print(f"WORKER: making a request, sleep_time: {sleep_time}")
			result = job.execute()
			if result.status() == 200:
				# Accelerate attack when OKed
				# print(f"WORKER: request success {sleep_time}")
				self.inner_result_queue.add_value(result)
				sleep_time /= attack_rate
			elif result.status() == 429:
				# Backoff requests when rate limited
				sleep_time *= backoff_rate
				print(f"WORKER: Backing off {sleep_time}")
				# Add job back to queue, this time prioritised
				job.priority=True
				self.inner_job_queue.add_value(job)
			else:
				# Crash when failed for unknown reason
				print("WORKER: ",result.response.json())
				raise Exception
			sleep(sleep_time)

	def start(self):
		dispatcher = Thread(target=self.job_dispatcher)
		# dispatcher.start()
		dispatcher.start()

		workers = [ 
			Thread(target=self.job_executor)
			for i in range(self.max_thread_count)
		]
		for w in workers:
			w.start()

		for w in workers:
			w.join()
		# # This should be adequate to make sure all threads are done. they have the same complete condition
		dispatcher.join()

