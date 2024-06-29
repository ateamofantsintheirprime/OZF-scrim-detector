from db import cache_engine
from sqlalchemy.orm import Session
from cache_models import OZFResponse

# Basic insertion and access methods
def get_response(key:str) -> OZFResponse:
	with Session(cache_engine) as session:
		return session.get(OZFResponse, key)
	
def insert_response(key:str, new_data:dict):
	with Session(cache_engine) as session:
		if session.get(OZFResponse, key) is None:
			# print("inserting new response")
			resp = OZFResponse(key=key,data=new_data)
			session.add(resp)
			session.commit()

def update_response(key:str, new_data:dict):
	with Session(cache_engine) as session:
		cached_response =  session.get(OZFResponse, key)
		assert cached_response != None
		cached_response.data = new_data
		session.commit()