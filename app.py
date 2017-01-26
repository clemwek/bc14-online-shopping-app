from flask import(Flask, render_template, flash, request, url_for, redirect, session)
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
	results = methods_get_all() 
	return render_template('index.html', results=results)

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		'''For restriction to login pgs'''
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('home_page'))
	return wrap

@app.route('/logout/')
@login_required
def logout():
	'''To log out'''
	session.clear()
	msg = 'you have been logged out'
	return redirect(url_for('home_page'))

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
					return redirect(url_for('home_page'))
	except Exception as e:
		return redirect(url_for('home_page'))

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
				new_user = con.execute("SELECT * FROM users WHERE username = '" + username + "'").fetchall()
				msg = "Record successfully added"
				# con.close()
				session['logged_in'] = True
				session['id'] = new_user[0][0]
				session['username'] = new_user[0][1]
				return redirect(url_for('owners'))
	except Exception as e:
		# con.rollback()
		con.close()
		return (str(e))# redirect(url_for('home_page'))


@app.route('/owners')
def owners():
	product_list = []
	stores = read_stores_for_owner(session['id'])
	for store in stores:
		product_list.append(read_products_for_store(store[0]))
	print product_list
	return render_template('owner.html', stores=stores, product_list=product_list)

@app.route('/addstore/', methods=['POST'])
def addstore():
	try:
		if request.method == 'POST':
			storeName = request.form['storeName']
			location = request.form['location']
			user_id = session['id']
			with sql.connect("database.db", timeout=1) as con:
				cur = con.cursor()
				query = "SELECT * FROM stores WHERE name = '"+storeName+"' AND location = '"+location+"'"
				store = cur.execute(query).fetchall()
				print (store)
				if len(store) > 0:
					'''This means that the username is already used'''
					msg= "Store name already used"
					return render_template('owner.html', msg=msg)
				cur.execute("INSERT INTO stores (u_id, name, location) VALUES (?, ?, ?)", (user_id, storeName, location))
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
			with sql.connect("database.db", timeout=1) as con:
				cur = con.cursor()
				query = "SELECT * FROM products "
				stores = cur.execute(query).fetchall()
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

# @app.route('/methods')
def methods_get_all():
	product_list = []
	stores = read_stores()
	for store in stores:
		products = read_products_for_store(store[0])
		product_list.append(products)
	result = [stores, product_list] 
	return result

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
				query = "SELECT * FROM products WHERE store_id = '" + str(id) + "' "
				products = cur.execute(query).fetchall()
			return products[0]
	except Exception as e:
		msg = 'Something went wrong'
		return (str(e))


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

def read_stores_for_owner(u_id):
	try:
		with sql.connect("database.db", timeout=1) as con:
			cur = con.cursor()
			query = "SELECT * FROM stores WHERE u_id = '"+str(u_id)+"'"
			stores = cur.execute(query).fetchall()
			return stores
	except Exception as e:
		msg = 'Something went wrong'
		return (str(e))


def share_link():
	return "shared"

@app.errorhandler(404)
def page_not_found(e):
	return('four oh four!!!')

app.run(debug=True)
