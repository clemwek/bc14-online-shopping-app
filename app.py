from flask import (Flask, render_template, flash, request, url_for, 
             redirect, session)
from wtforms import Form, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

from flask import g
import sqlite3 as sql
import gc

app = Flask(__name__)
app.secret_key = "htffnafafiviufhvsdjo"

DATABASE = 'database.db'

@app.route('/')
def home_page():
	'''this load the index.html'''
	# flash("Flash test!!!")
	return render_template('index.html')

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		'''For restriction to login pgs'''
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			msg = 'You need to login first'
			return redirect(url_for('home_page', msg=msg))
	return wrap

@app.route('/logout/')
@login_required
def logout():
	'''To log out'''
	session.clear()
	msg = 'you have been logged out'
	return redirect(url_for('home_page'), msg=msg)

@app.route('/signin', methods=['POST', 'GET'])
def signin():
	'''To signin'''
	try:
		if request.method == 'POST':
			username = request.form['username']
			password = request.form['password']

			with sql.connect("database.db", timeout=1) as con:
				cur = con.cursor()

				query = "SELECT * FROM users WHERE username = '"+username+"'"

				user = cur.execute(query).fetchall()
				if username == user[0][1] and password == user[0][2]:
					session['logged_in'] = True
					session['id'] = user[0][0]
					session['username'] = user[0][1]
					return  redirect(url_for('owners'))
				else:
					return redirect(url_for('home_page'), msg="Username/password is not correct.")
	except Exception as e:
		msg="something went wrong!!!"
		return (str(e)) # redirect(url_for('home_page'))

@app.route('/signup/', methods=['POST'])
def signup():
	try:
		msg = 'Not assigned!!!!'

		if request.method == 'POST':
			username = request.form['username']
			password = request.form['password']
			confirm = request.form['confirm']
			name = request.form['name']
			phone = request.form['phone_number']
			email = request.form['email']


			with sql.connect("database.db", timeout=1) as con:
				cur = con.cursor()

				query = "SELECT * FROM users WHERE username = '"+username+"'"

				user = cur.execute(query).fetchall()
				if len(user) > 0:
					'''This means that the username is already used'''
					msg= "Username already used"
					return render_template('index.html', msg=msg)
				cur.execute("INSERT INTO users (username, password, name, phone, email, prev) VALUES (?, ?, ?, ?, ?, ?)", (username, password, name, phone, email, 'admin'))
				con.commit()
				msg = "Record successfully added"
				con.close()
				return redirect(url_for('owners'), msg=msg)
	except Exception as e:
		con.rollback()
		msg = "error in insert operation"
		con.close()
		return redirect(url_for('home_page'), msg=msg)


@app.route('/owners')
def owners():
	return render_template('owner.html')

@app.route('/addstore/', methods=['POST'])
def addstore():
	try:
		if request.method == 'POST':
			storeName = request.form['storeName']
			location = request.form['location']
			user_id = 2#session['id']
			with sql.connect("database.db", timeout=1) as con:
				cur = con.cursor()
				query = "SELECT * FROM stores WHERE name = '"+storeName+"' AND location = '"+location+"'"
				store = cur.execute(query).fetchall()
				print (store)
				if len(store) > 0:
					'''This means that the username is already used'''
					msg= "Store already used"
					return render_template('owner.html', msg=msg)
				cur.execute("INSERT INTO stores (u_id, name, location) VALUES (?, ?, ?)", (storeName, location, user_id))
				con.commit()
				msg = "Record successfully added"
				# con.close()
				return redirect(url_for('owners'))
	except Exception as e:
		print (str(e))
		# con.rollback()
		msg = "error in insert operation"
		con.close()
		return 'Not OK'#redirect(url_for('owners'))


@app.route('/addprod/', methods=['POST'])
def addprod():
	try:
		if request.method == 'POST':
			store_id = request.form['store_id']
			prodName = request.form['prodName']
			price = request.form['price']
			# return store_id
			print "HERE", request.form, request.form['store_id']
			with sql.connect("database.db", timeout=1) as con:
				cur = con.cursor()
				query = "SELECT * FROM products "
				stores = cur.execute(query).fetchall()
				print (stores)
				if prodName in stores:
					'''This means that the username is already used'''
					msg= "Store already used"
					return render_template('owner.html', msg=msg)
				cur.execute("INSERT INTO products (store_id, prod_name, price) VALUES (?, ?, ?)", (store_id, prodName, price))
				con.commit()
				msg = "Record successfully added"
				# con.close()
				return redirect(url_for('owners'))
	except Exception as e:

		# print (str(e))
		# con.rollback()
		msg = "error in insert operation"
		# con.close()
		return redirect(url_for('owners'))

@app.route('/methods')
def methods():
	id = 1
	stores = read_stores()
	products = read_products_for_store(id)
	return render_template('methods.html', stores=stores, products=products)

def read_stores():
	try:
		with sql.connect("database.db", timeout=1) as con:
			cur = con.cursor()
			query = "SELECT * FROM stores"
			stores = cur.execute(query).fetchall()
			return stores
	except Exception as e:
		msg = 'Something went wrong'
		return (msg)


def read_products_for_store(id):
	try:
		with sql.connect("database.db", timeout=1) as con:
			cur = con.cursor()
			if int(id):
				query = "SELECT * FROM products WHERE store_id = '"+id+"'"
				products = cur.execute(query).fetchall()
			return query
	except Exception as e:
		msg = 'Something went wrong'
		return (msg)


def read_products():
	try:
		with sql.connect("database.db", timeout=1) as con:
			cur = con.cursor()
			query = "SELECT * FROM products"
			products = cur.execute(query).fetchall()
			return products
	except Exception as e:
		msg = 'Something went wrong'
		return (msg)

def read_stores_for_owner():
	try:
		with sql.connect("database.db", timeout=1) as con:
			cur = con.cursor()
			query = "SELECT * FROM stores WHERE u_id -"+u_id
			stores = cur.execute(query).fetchall()
			return stores
	except Exception as e:
		msg = 'Something went wrong'
		return (msg)


def share_link():
	return "shared"

@app.errorhandler(404)
def page_not_found(e):
	return('four oh four!!!')

app.run(debug=True)
