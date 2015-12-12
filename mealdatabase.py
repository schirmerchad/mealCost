from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Meal, Ingredient, User

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
engine = create_engine('sqlite:///meallist2.db')
Base.metadata.bind = engine
# A DBSession() instance establishes all conversations with the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

#User 1 details
user1 = User(name="Chad", email="chad@gmail.com")
session.add(user1)
session.commit()

# Meal 1 details
meal1 = Meal(name="Twice Baked Sweet Potato", user=user1)
session.add(meal1)
session.commit()

ingredient1 = Ingredient(name="Sweet Potatos", amount=2,
                     price=0.50, meal=meal1, user=user1)
session.add(ingredient1)
session.commit()

ingredient2 = Ingredient(name="Bacon", amount=1/2,
                     price=4.00, meal=meal1, user=user1)
session.add(ingredient2)
session.commit()

print "added meals and their items!"
