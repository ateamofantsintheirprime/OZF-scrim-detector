from __future__ import annotations
from typing import Optional
from sqlalchemy import Integer, String, Column, PickleType, DateTime
from sqlalchemy.orm import DeclarativeBase

# data models
class CacheBase(DeclarativeBase):
	pass

class OZFResponse(CacheBase):
	__tablename__ = "response"

	key = Column(String, primary_key=True)
	# Add an expiry date to this
	data = Column(PickleType)
