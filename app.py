from flask import Flask, render_template, request
# import pymysql
import jinja2
# from flask.ext import mysql
from werkzeug import generate_password_hash, check_password_hash
from db_interface import *

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = pymysql.connect(host = "127.0.0.1", user = "root", passwd = "lionell123", db = "smartbin", port = 3306)

app = Flask(__name__)
# api = Api(app)

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/showSignUp")
def showSignUp():
	return render_template('signup.html')
#
# @app.route("/leaderboard", methods = ["GET"])
# def someName():
# 	cursor = db.cursor()
# 	sql = "SELECT * FROM Users"
# 	cursor.execute(sql)
# 	results = cursor.fetchall()
# 	print(results)
# 	return render_template('leaderboard.html', results=results)
	# return render_template('leaderboard.html')

# @app.route("/signUp", methods=['POST'])
# def signUp():
	# return get_leaderboard()

# def signUp():
# 	try:
# 		if request.method == "POST":
# 			print("trying")
# 			_name = request.form['inputName']
# 			_email = request.form['inputEmail']
# 			_password = request.form['inputPassword']
#
# 			print(_name, _email, _password)
#
# 			# validate the received values
# 			if _name and _email and _password:
#
# 				# All Good, let's call MySQL
#
# 				conn = mysql.connect()
# 				cursor = conn.cursor()
# 				_hashed_password = generate_password_hash(_password)
# 				cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
# 				data = cursor.fetchall()
#
# 				if len(data) is 0:
# 					conn.commit()
# 					return json.dumps({'message':'User created successfully !'})
# 				else:
# 					return json.dumps({'error':str(data[0])})
# 			else:
# 				return json.dumps({'html':'<span>Enter the required fields</span>'})

	# except Exception as e:
	# 	return json.dumps({'error':str(e)})
	#
	# finally:
	# 	cursor.close()
	# 	conn.close()


if __name__ == "__main__":
	app.run()

