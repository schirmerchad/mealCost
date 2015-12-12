#Flask framework imports
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
#SQLalchemy and database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Meal, Ingredient, User
#Flask login imports
from flask import session as login_session
import random, string
#Gconnect imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

#Gconnect functionality
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Web client 1"

engine = create_engine('sqlite:///meallist2.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Home page. Will eventually have more info, overview of app, subscribe box, and large button directing to login page
@app.route('/')
def homePlace():
	return render_template('home.html')

#Login page. Creates an anti-forgery token
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

#Google+ sign in functionality
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("Successfully logged in!")
    return redirect(url_for('mealList'))

#Disconnect from app. Revokes token and resets login_session
@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("Current user not connected")
        return redirect(url_for('mealList'))
    print 'In gdisconnect access token is %s', credentials
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully logged out!")
        return redirect(url_for('mealList'))
    else:	
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
        flash("Oops! Your logout attempt failed!")
    	return redirect(url_for('mealList'))

#Functions to create new local user. Not yet inclucded in app
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

#Main page once logged in. Queries all meals in database
@app.route('/meals/')
def mealList():
	meal = session.query(Meal).all()
	return render_template('meals.html', meal = meal)

#Allows a logged in user to create a new meal
@app.route('/meals/new/', methods = ['GET', 'POST'])
def newMeal():
    if 'username' not in login_session:
        flash("You must be logged in to do that!")
        return redirect('/login')
    else:
    	if request.method == 'POST':
            newMeal = Meal(name = request.form['name'], user_id = login_session['user_id'])
            session.add(newMeal)
            session.commit()
            flash("New meal created!")
            return redirect(url_for('mealList'))
    	else:
    		return render_template('newmeal.html')

#View meal details
@app.route('/meals/<int:meal_id>/')
def mealDetails(meal_id):
    meal = session.query(Meal).filter_by(id = meal_id).one()
    creator = getUserInfo(meal.user_id)
    ingredients = session.query(Ingredient).filter_by(meal_id = meal.id)
    return render_template('mealdetails.html', meal = meal, ingredients = ingredients, creator = creator)

#Allows a logged in user to delete a new meal
@app.route('/meals/<int:meal_id>/delete/', methods = ['GET', 'POST'])
def deleteMeal(meal_id):
    if 'username' not in login_session:
        flash("You must be logged in to do that!")
        return redirect('/login')
    else:
    	mealToDelete = session.query(Meal).filter_by(id = meal_id).one()
    	if request.method == 'POST':
            session.delete(mealToDelete)
            session.commit()
            flash("Meal deleted!")
            return redirect(url_for('mealList'))
    	else:
    		return render_template('deletemeal.html', meal_id = meal_id, i = mealToDelete)

#Allows a logged in user to add a new ingredient to a meal
@app.route('/meals/<int:meal_id>/new/', methods = ['GET', 'POST'])
def newMealIngredient(meal_id):
    if 'username' not in login_session:
        flash("You must be logged in to do that!")
        return redirect('/login')
    else:
    	if request.method == 'POST':
            newIngredient = Ingredient(name = request.form['name'], amount = request.form['amount'], price = request.form['price'], meal_id = meal_id, user_id = login_session['user_id'])
            session.add(newIngredient)
            session.commit()
            flash("New ingredient added!")
            return redirect(url_for('mealDetails', meal_id = meal_id))
    	else:
    		return render_template('newingredient.html', meal_id = meal_id)

#Allows a logged in user to edit a meal ingredient
@app.route('/meals/<int:meal_id>/<int:ingredient_id>/edit/', methods = ['GET', 'POST'])
def editMealIngredient(ingredient_id, meal_id):
    if 'username' not in login_session:
        flash("You must be logged in to do that!")
        return redirect('/login')
    else:
        editedIngredient = session.query(Ingredient).filter_by(id = ingredient_id).one()
    	if request.method == 'POST':
            editedIngredient.name = request.form['name']
            editedIngredient.amount = request.form['amount']
            editedIngredient.price = request.form['price']
            session.add(editedIngredient)
            session.commit()
            flash("Ingredient edited!")
            return redirect(url_for('mealDetails', meal_id = meal_id))
    	else:
    		return render_template('editingredient.html', ingredient_id = ingredient_id, meal_id = meal_id , i = editedIngredient) 

#Allows a logged in user to delete a meal ingredient
@app.route('/meals/<int:meal_id>/<int:ingredient_id>/delete/', methods = ['GET', 'POST'])
def deleteMealIngredient(ingredient_id, meal_id):
    if 'username' not in login_session:
        flash("You must be logged in to do that!")
        return redirect('/login')
    else:
    	ingredientToDelete = session.query(Ingredient).filter_by(id = ingredient_id).one()
    	if request.method == 'POST':
            session.delete(ingredientToDelete)
            session.commit()
            flash("Ingredient deleted!")
            return redirect(url_for('mealDetails', meal_id = meal_id))

#Json API endpoint for meals
@app.route('/meals/json')
def mealsJSON():
    meals = session.query(Meal).all()
    return jsonify(meals=[r.serialize for r in meals])

#Json API endpoint for the details of a meal
@app.route('/meals/<int:meal_id>/json')
def mealdetailsJSON(meal_id):
    meal = session.query(Meal).filter_by(id = meal_id).one()
    ingredients = session.query(Ingredient).filter_by(meal_id = meal_id).all()
    return jsonify(mealIngredients=[i.serialize for i in ingredients])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
