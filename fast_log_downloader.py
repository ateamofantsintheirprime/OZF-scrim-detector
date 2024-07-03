from league_models import League, Roster, Player, Log, PlayerLogTracker, Game, TeamInstance
from datetime import datetime, timedelta
from database.methods import league, tracker, log, roster, player, game
import requests, json
from database_helper import expunge_unicode
from typing import Union
from requests import Response
from requests.exceptions import ConnectionError
from time import sleep
from copy import deepcopy
from threading import Thread, Lock, Event, current_thread
from concurrent.futures import ThreadPoolExecutor
from random import random
from debug import debug_print
import copy


class RequestProcesser():
	""" Superclass that implements parallel network request execution and processing
	TODO write proper documentation for this"""
	def __init__(self):
		self.id_counter :int = 0
		self.job_queue = PriorityQueue()
		self.result_queue = PriorityQueue()

		self.awaiting_results:list[int] = [] # Result ids we are waiting to receive from mass requester
		self.targets:Union[League,Roster,Player] = []
		# Synchronisation flag
		self.complete = Event()
		self.requester_waiting = Event()
		self.processor_waiting = Event()

		self.sub_targets: set = set()

		# Workers
		# Rename this shit lol
		self.mass_requester = MassRequester(self.job_queue, self.result_queue, self.requester_waiting, self.complete)
		self.mass_requester_thread = Thread(target=self.mass_requester.start)
		self.serial_processer_thread = Thread(target=self.process_result_queue)


	def get_initial_jobs(self):
		self.get_sub_targets()
		self.job_queue.clear()
		self.awaiting_results.clear()
		for s_targ in self.sub_targets:
			job = self.make_job(s_targ)
			self.awaiting_results.append(job.id)
			self.job_queue.add_item(job)
			self.id_counter += 1

	def process_result_queue(self):
		while not self.complete.is_set():
			result:Result = self.result_queue.pop_item()
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


	def execute_task(self):
		self.get_initial_jobs()
		self.get_existing_data()
		if len(self.job_queue) == 0:
			print("no jobs")
			return

		print("ORGANISER: starting requester")
		self.mass_requester_thread.start()
		print("ORGANISER: starting processor")
		self.serial_processer_thread.start()

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
				self.serial_processer_thread.join()
				self.mass_requester_thread.join()
				break
		print("threads complete")

	def get_sub_targets(self):
		assert len(self.targets) > 0
		self.sub_targets.clear()
		while len(self.targets) > 0:
			target = self.targets.pop()
			if isinstance(target, list):
				self.targets.extend(target)
			elif isinstance(target, set):
				self.targets.extend(list(target))
			else:
				self.break_up_target(target)

		self.filter_out_subtargets()
			
	def break_up_target(self,target):
		"""turn a user defined target into a set of subtargets"""
		raise Exception

	def filter_check(self):
		"""Check if a subtarget should or shouldnt be there
		needs to be overridden"""
		raise Exception

	def filter_out_subtargets(self):
		"""remove subtargets that shouldnt be there"""
		self.get_job_filtration_data()
		
		filter_out = set()
		for sub_targ in self.sub_targets:
			if self.filter_check(sub_targ):
				filter_out.add(sub_targ)
		# print(f"filtering out {filter_out}")
		self.sub_targets.difference_update(filter_out)

	def get_existing_data(self):
		# raise Exception
		pass

	def get_job_filtration_data(self):
		pass

	def make_job(self):
		raise Exception

class LogSearcher(RequestProcesser):
	"""This is designed to search for ALL logs of a set of targets
	ONLY FOR LOGS.TF API"""
	def __init__(self):
		super().__init__()
		self.existing_logs: set[Log]= set()
		self.existing_player_logs : dict[int:set[Log]] = set()

	def break_up_target(self, target):
		if isinstance(target, League):
			self.sub_targets.update(league.get_league_player_id_64s(target.id))
		elif isinstance(target, Roster):
			self.sub_targets.update(roster.get_roster_player_ids(target.id))
		elif isinstance(target, Player):
			self.sub_targets.add(target.id_64)
		else:
			print("invalid target type")
			raise Exception
	
	def filter_check(self,id_64:int):
		assert isinstance(id_64,int)
		log_tracker = tracker.get_log_tracker(id_64)
		return not log_tracker is None and not tracker.expired(log_tracker)


	# def filter_out_subtargets(self):
	# 	filter_out_ids = set()
	# 	for id_64 in self.sub_targets:
	# 		log_tracker = tracker.get_log_tracker(id_64)
	# 		if not log_tracker is None and not tracker.expired(log_tracker):
	# 			filter_out_ids.add(id_64)
	# 	# Keep only targeted id_64s that arent filtered out 
	# 	self.sub_targets.difference_update(filter_out_ids)

	def get_existing_data(self):
		self.existing_logs.clear()
		self.existing_logs = log.get_all_logs()
	
	def get_job_filtration_data(self):
		self.existing_player_logs.clear()
		self.existing_player_logs = player.get_existing_logs(self.sub_targets)


	def make_job(self,id_64:int, offset:int=0) -> str:
		return Job(
			id=self.id_counter,
			url=f"http://logs.tf/api/v1/log?player={id_64}&offset={offset}")

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
				new_job = self.make_job(id_64=id_64,offset=offset+1000)
				new_job.id = result.id
				new_job.priority=True
				self.awaiting_results.append(new_job.id)
				self.job_queue.add_item(new_job)
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


class GameRequester(LogSearcher):
	"""This is designed to request information on a set of logs
	ONLY FOR LOGS.TF API"""
	def __init__(self):
		super().__init__()
		self.existing_game_ids : set[Game] = set()
		# self.existing_team_instances : set[TeamInstance] = set()
		self.sub_targets : set[Log] = set()

	def break_up_target(self, target):
		if isinstance(target, League):
			self.sub_targets.update(league.get_league_logs(target.id))
		elif isinstance(target, Roster):
			self.sub_targets.update(roster.get_roster_logs(target.id, 4))
		elif isinstance(target, Player):
			self.sub_targets.update(player.get_player_logs(target.id_64))
		else:
			print("invalid target type")
			raise Exception

	def filter_check(self, log:Log):
		assert isinstance(log,Log)
		# print(f"log id: {log.id}")
		# print(f"existing_game_ids: {self.existing_game_ids}")
		return log.id in self.existing_game_ids

	def make_job(self,log:Log):
		return Job(
			id=self.id_counter,
			url=f"http://logs.tf/api/v1/log/{log.id}",
			result_id=log.id)

	def get_job_filtration_data(self):
		self.existing_game_ids.clear()
		# self.existing_team_instances.clear()
		self.existing_game_ids = game.get_all_game_ids()
		# self.existing_team_instances = roster.get_all_team_instances()
		print()

	def process_result(self, result:'Result'):
		response=result.response
		# Step 1 parse response
		data = json.loads(expunge_unicode(response.text))
		red_player_ids : list[str] = []
		blue_players_ids : list[str] = []
		for id in data['players'].keys():
			if data['players'][id]['team'] == "Red":
				red_player_ids.append(id[1:-1])
			elif data['players'][id]['team'] == "Blue":
				blue_players_ids.append(id[1:-1])
			else:
				raise Exception
		# Add some check to see if its highlander

		game_data = {
			"red_score" :int(data['teams']['Red']['score']),
			"blue_score" :int(data['teams']['Blue']['score']),
			"red_player_ids" :red_player_ids,
			"blue_player_ids" :blue_players_ids,
			"map_name" :data['info']['map'],
			"duration" : int(data['length']),
			"date" :datetime.fromtimestamp(data['info']['date']),
			"id": result.result_id
		}
		game.update_game(game_data)

		# Make it so that it still makes the merc teams even if the game still exists


		print(f"PROCESSOR: Remaining jobs: {len(self.awaiting_results)}")
		


class DoublePriorityQueue():
	""" Designed to facilitate asyncronous enqueueing and dequeueing of mixed-priority
	tasks with almost no blocking for enqueuer and minimal blocking for dequeuer"""
	def __init__(self):
		self.outer_queue = PriorityQueue()

class Job():
	def __init__(self, id:int, url:str, priority:bool=False, result_id:int=-1):
		self.id=id
		self.url=url
		self.priority=priority
		self.result_id=result_id # The result of a log request doesnt contain the log id
	def execute(self) -> 'Result':
		return Result(
			id=self.id,
			response=requests.get(self.url),
			priority=self.priority,
			result_id=self.result_id)

class Result():
	def __init__(self, id:int, response:Response,priority:bool, result_id:int=-1):
		self.id=id
		self.response=response
		self.priority=priority
		self.result_id=result_id # The result of a log request doesnt contain the log id
	def status(self):
		return self.response.status_code

class PriorityQueue():
	def __init__(self):
		self.regular = []
		self.priority = []
		self.regular_queue_len = 0
		self.priority_queue_len = 0
		self.regular_lock = Lock()
		self.priority_lock = Lock()

	def clear(self):
		self.priority_lock.acquire(blocking=True)
		self.priority.clear()
		self.priority_queue_len = 0
		self.priority_lock.release()
		self.regular_lock.acquire(blocking=True)
		self.regular.clear()
		self.regular_queue_len = 0
		self.regular_lock.release()

	def add_item(self,item:Union[Job,Result]):
		if item.priority:
			self.priority_lock.acquire(blocking=True)
			self.priority.append(item)
			# self.priority_queue_len = len(self.priority)
			self.priority_queue_len += 1
			self.priority_lock.release()
		else:
			self.regular_lock.acquire(blocking=True)
			self.regular.append(item)
			# self.regular_queue_len = len(self.regular)
			self.regular_queue_len += 1
			self.regular_lock.release()

	def pop_item(self):
		if self.priority_queue_len > 0 and self.priority_lock.acquire(blocking=True):
			item = self.priority.pop()
			self.priority_queue_len -= 1
			self.priority_lock.release()
			return item
		if self.regular_queue_len > 0 and self.regular_lock.acquire(blocking=True):
			item = self.regular.pop()
			self.regular_queue_len -= 1
			self.regular_lock.release()
			return item
		return None
	
	def is_empty(self):
		return self.priority_queue_len + self.regular_queue_len > 0

	def __str__(self):
		return f"""Regular queue: {self.regular}\nPriority queue:{self.priority}"""
	def __len__(self):
		return self.priority_queue_len + self.regular_queue_len

class MassRequester():
	"""The mass requester uses multiple priority-queues to
	facilitate job and result enqueueing, dispatching, executing,
	and retreival, through a system of inner and outer job and
	result queues. 
	
	(Note: priority queues will always lock when accessed)

	- Jobs are added asyncronously to the outer job queue by a
	coordinating entity or user.

	- The job dispatcher thread will periodically move all jobs
	from the outer job queue to the inner job queue.

	- The worker threads will then each periodically take a single
	job off the inner job queue and attempt to execute it.
		+ This execution will yeild a result object (or exception)
		+ Successful results will be added to the inner result queue
		+ Unsuccessful results or exceptions will be discarded, with
			the job added back to the inner job queue.
	
	- The job dispatcher will periodically move all results from
	the inner result queue to the outer result queue.

	- The user / coordinating entity can then access these results
	from the outer result queue

	Note: The reason we have inner and outer queues is to minimise
	fighting over locks. If we used a single job queue and result queue
	we would have the user / coordinating entity fighting with workers
	to access the queue. This is not good because we presume the
	coordinating entity has better things to do.

	Using double queues the user/ coordinating entity only "fights"
	with the dispatcher, who works relatively quickly and sporadically. 


	"""
	def __init__(self, job_queue:PriorityQueue, result_queue:PriorityQueue, requester_waiting:Event, complete:Event):
		# Jobs are added to this by coordinating entity
		self.outer_job_queue = job_queue
		# Jobs moved to innner queue
		self.inner_job_queue = PriorityQueue()

		self.outer_result_queue = result_queue
		self.inner_result_queue = PriorityQueue()

		self.requester_waiting = requester_waiting
		self.complete = complete

		# self.worker_count:int = 0
		self.starting_worker_count = 20
		self.workers: list[Thread] = []

	def job_dispatcher(self):
		awaiting_values = []
		dispatcher_sleep_time = .1
		while not self.complete.is_set():
			# Put jobs on the inner queue
			job:Job = self.outer_job_queue.pop_item()
			if not job is None:
				# print(f"DISPATCHER: Adding a job to the inner queue (queue length:{len(self.inner_job_queue)})")
				self.requester_waiting.clear()
				awaiting_values.append(job.id)
				self.inner_job_queue.add_item(job)
			# Take results off the inner queue
			result:Result = self.inner_result_queue.pop_item()
			if not result is None:
				# print(f"DISPATCHER: taking a result off the inner queue, {len(awaiting_values)}")
				awaiting_values.remove(result.id) # This should never raise a value error
				self.outer_result_queue.add_item(result)
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
		sleep(random()*len(self.workers)/2) # Give each worker an offset to avoid synching up many api requests
		backoff_rate = 2.5 
		attack_rate = 1.3
		min_sleep_time = 0.1
		max_sleep_time = 7.0
		sleep_time = max_sleep_time/2
		# print("WORKER: starting up worker")
		while not self.complete.is_set():
			# print("WORKER: worker about to grab a job")
			job:Job = self.inner_job_queue.pop_item()
			if job is None:
				sleep(1) # Not sure if this should be a variable / random length sleep
				continue
			try:
				result = job.execute()
			except ConnectionError:
				# For now just add it back to the queue, i think this is logs.tf ddoss protection
				sleep_time = max_sleep_time-1
				print(f"WORKER: Omega backing off {sleep_time}")
				# Add job back to queue, this time prioritised
				job.priority=True
				self.inner_job_queue.add_item(job)
				continue
			if result.status() == 200:
				# Accelerate attack when OKed
				# print(f"WORKER: request success {sleep_time}")
				self.inner_result_queue.add_item(result)
				sleep_time /= attack_rate
			elif result.status() == 429:
				# Backoff requests when rate limited
				sleep_time *= backoff_rate
				print(f"WORKER: Backing off {sleep_time}")
				# Add job back to queue, this time prioritised
				job.priority=True
				self.inner_job_queue.add_item(job)
			else:
				# Crash when failed for unknown reason
				print("WORKER: ",result.response.json())
				raise Exception
			sleep(sleep_time)
			
			# If the sleep time is too low, that means the number of workers is too low
			# If the sleep time is too high, there are too many workers
			# Dynamically scale up / down the number of workers
			if sleep_time <= min_sleep_time:
				sleep_time *= backoff_rate # we are scaling up # of workers so we want to backoff a little bit to smooth out throughput spike
				new_worker = Thread(target=self.job_executor)
				self.workers.append(new_worker)
				new_worker.start()
				print("sleep time too low, adding new workers")
				print(f"number of workers: {len(self.workers)}")
				
			elif sleep_time >= max_sleep_time:
				print("sleep time too high, finishing worker")
				break

	def worker_pool_manager(self):
		while not self.complete.is_set():
			for i in range(len(self.workers)-1,-1,-1):
				if not self.workers[i].is_alive():
					print("dead worker, cleaning up")
					print(f"number of workers: {len(self.workers)}")
					self.workers.pop(i).join()
			sleep(1)

	def start_all_workers(self):
		# self.worker_count = len(self.workers)
		for w in self.workers:
			w.start()
	
	def join_all_workers(self):
		while len(self.workers) > 0:
			w = self.workers.pop()
			# self.worker_count = len(self.workers)
			w.join()
		

	def start(self):
		dispatcher = Thread(target=self.job_dispatcher)
		worker_manager = Thread(target=self.worker_pool_manager)
		dispatcher.start()

		self.workers = [ 
			Thread(target=self.job_executor)
			for i in range(self.starting_worker_count)
		]
		# self.worker_count = self.starting_worker_count
		self.start_all_workers()
		worker_manager.start()
		self.join_all_workers()
		# # This should be adequate to make sure all threads are done. they have the same complete condition
		worker_manager.join()
		dispatcher.join()
