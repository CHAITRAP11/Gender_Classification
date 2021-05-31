from flask import Flask , request , redirect , render_template , session
import views
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from datetime import datetime
import os
from PIL import Image
from util import pipeline_model 



UPLODAD_FOLDER = 'static/uploads'

app=Flask(__name__)

app.secret_key = "super secret key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'localhost'
app.config['MYSQL_PASSWORD'] = 'Chaitra@123'
app.config['MYSQL_DB'] = 'gender'
mysql = MySQL(app)

#session['email']=None

def getwidth(path):
	img = Image.open(path)
	size = img.size
	aspect = size[0]/size[1]
	w= 300 * aspect
	return (w)

@app.route("/gender",methods=['GET','POST'])
def gender():
	if request.method=="POST":
		f=request.files['image']
		filename = f.filename
		path=os.path.join(UPLODAD_FOLDER,filename)
		f.save(path)
		w=getwidth(path)
		#prediction (pass to pipeline model)
		text,male,female=pipeline_model(path,filename, color='bgr')
		return render_template('gender.html',fileupload=True, img_name=filename,w=w,text=text,male=male,female=female)		
	return render_template('gender.html',fileupload=False, img_name="img_girl.jpg",w="300")

app.add_url_rule('/','login',views.login, methods=['GET','POST'])
app.add_url_rule('/register','register',views.register, methods=['GET','POST'])
app.add_url_rule('/base','base',views.base)
#app.add_url_rule('/index','index',views.index)
#app.add_url_rule('/faceapp','faceapp',views.faceapp)
#app.add_url_rule('/faceapp/gender','gender',views.gender)
#app.add_url_rule('/faceapp/gender/predict','gender',views.gender)
#app.add_url_rule('/contact','contact',views.contact, methods=['GET','POST'])
#app.add_url_rule('/rate_us','rate_us',views.rate_us, methods=['GET','POST'])

@app.route('/faceapp',methods=["GET","POST"])
def faceapp():
	if  'email' in session:
		return render_template("faceapp.html")
	else:
		return render_template("login.html")


@app.route('/sreg',methods=["GET","POST"])
def sreg():
	if request.method == "POST":
		fullname=request.form['name']
		email=request.form['email']
		password=request.form['password']
		conpassword=request.form['conpassword']
		data=None
		str1=None
		str2=None
		flag1=False
		flag2=False

		cur=mysql.connection.cursor()
		cur.execute("SELECT email FROM register WHERE email=%s",(email,))
		data=cur.fetchone()
		#cur.close()
		# if data == None:
		# 	print("Data none:",data)
		#print("Data is none:",data)
		if(data != None):
			str1="Email is already used."
			print("Data:",data)
			return render_template("register.html",str1=str1, flag1=True)

		if(password != conpassword):
			print("not matching")
			str2="password is not matching."
			return render_template("register.html",str2=str2, flag2=True)

		cur.execute("INSERT INTO register(fullname, email,password) VALUES (%s, %s, %s)",(fullname,email, password))
		mysql.connection.commit()
		session['name']=fullname
		session['email']=email
		cur.close()
		return render_template("login.html")
	return 'DataBase error!!'


@app.route('/slog',methods=["GET","POST"])
def slog():
	if request.method == "POST":
		email=request.form['email']
		password = request.form['password']
		flag1=False

		cur=mysql.connection.cursor()
		cur.execute("SELECT email,password FROM register WHERE email=%s and password=%s",(email,password,) )
		data=cur.fetchone()
		
		if data != None:
			session['email']=email
			return render_template("index.html")
		else:
			str1="wrong emailid or password."
	return render_template("login.html",str1=str1,flag1=True)

@app.route('/contact/cform', methods=["GET","POST"])
def cform():
	if request.method == "POST":

		fullname=request.form['name']
		email=request.form['email']
		text=request.form['text']
		
		#time= datetime.utcnow
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO contact(fullname, email, text) VALUES (%s, %s, %s)", (fullname, email, text))
		mysql.connection.commit()
		cur.close()
		return index()
	return 'DataBase error!!'

@app.route('/rate_us/rating',methods=["GET","POST"])
def rating():
	if request.method == "POST":
		name=request.form['name']
		rate=request.form['rating']
		describe=request.form['text']

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO Rating(name,rate,describe_us) VALUES(%s, %s, %s)",(name,rate,describe))
		mysql.connection.commit()
		cur.close()
		return render_template("index.html")
	return 'DataBase error!!'

@app.route('/log_out',methods=["GET","POST"])
def log_out():
	if request.method == "GET":
		session.pop('email', None)
		return render_template("login.html")

@app.route('/rate_us',methods=["GET","POST"])
def rate_us():
	if  'email' in session:
		return render_template("rating.html")
	else:
		return render_template("login.html")

@app.route('/contact',methods=["GET","POST"])
def contact():
	if  'email' in session:
		return render_template("contact.html")
	else:
		return render_template("login.html")


@app.route('/index',methods=["GET","POST"])
def index():
	print(session)
	if  'email' in session:
		return render_template("index.html")
	else:
		return render_template("login.html")


if __name__ == '__main__':
	count=0
	count+=1
	print("====Hiii===")
	print(count)
	print(__name__)
	app.run(debug=True,port=5000)
