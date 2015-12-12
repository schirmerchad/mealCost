import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#The following code creates the three main databases used in the Meal Cost app
class User(Base):
	__tablename__ = 'user'
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	email = Column(String(80), nullable = False)
	picture = Column(String(80))

class Meal(Base):
	__tablename__ = 'meal'
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	#adds functionality to send json objects in serialized format
	@property
	def serialize(self):
	    return {
	    	'name': self.name,
	    	'id': self.id,
	    }	

class Ingredient(Base):
	__tablename__ = 'menu_item'
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	amount = Column(String(80))
	price = Column(String(80))
	meal_id = Column(Integer, ForeignKey('meal.id'))
	meal = relationship(Meal)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	#adds functionality to send json objects in serialized format
	@property
	def serialize(self):
	    return {
	    	'name': self.name,
	    	'id': self.id,
	    	'amount': self.amount,
	    	'price': self.price,
	    }

engine = create_engine('sqlite:///meallist2.db')
Base.metadata.create_all(engine)