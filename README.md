# fullstack-project3

Project #3 for the Udacity Full Stack Nanodegree
This project uses Python and SQLite to develop a RESTful web application. The Python framework Flask is used as well as OAuth authentication.

<h1>Description</h1>
This app allows a logged in user to create/read/edit/delete meals and ingredients to a database through a simple interface
The finished app will calculate the cost of a single meal and the cost of a slate of meals

<h1>Built with</h1>
Python, Flask, SQLite, SQLalchemy, HTML, CSS, Bootstrap, and JavaScript

<h1>Get the Code</h1>
git clone https://github.com/schirmerchad/fullstack-project3

<h1>Dependencies</h1>
Python v2.7.6
oauth2client
Flask v0.10.1 and all Flask dependencies
SQLite 3
SQLalchemy v1.0
Boostrap 3

<h1>Run</h1>
Install Vagrant and Virtual Box
Launch Vagrant VM
Create the database by running 'python database_setup.py'
Populate the database with one meal and one user by running 'python mealdatabase.py'
Start webserver by running 'python project.py'

<h1>JSON enpoints</h1>
JSON enpoints are available. To access them, visit the following URLs.
'/meals/json' for simple details on all the meals in the database
'/meals/<int:meal_id>/json' for more detailed information on one meal
