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
<ul>Python v2.7.6</ul>
<ul>oauth2client</ul>
<ul>Flask v0.10.1 and all Flask dependencies</ul>
<ul>SQLite 3</ul>
<ul>SQLalchemy v1.0</ul>
<ul>Boostrap 3</ul>

<h1>Run</h1>
<ol>Install Vagrant and Virtual Box</ol>
<ol>Launch Vagrant VM</ol>
<ol>Create the database by running 'python database_setup.py'</ol>
<ol>Populate the database with one meal and one user by running 'python mealdatabase.py'</ol>
<ol>Start webserver by running 'python project.py'</ol>

<h1>JSON enpoints</h1>
JSON enpoints are available. To access them, visit the following URLs.
<ol>'/meals/json' for simple details on all the meals in the database</ol>
<ol>'/meals/<int:meal_id>/json' for more detailed information on one meal</ol>
