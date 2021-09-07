from logging import error
from flask import Flask, config,render_template,request,redirect
from flask.templating import render_template_string
import pyrebase 
import json 
import requests
from cryptography.fernet import Fernet

hosting = "http://localhost:5000"

firebaseConfig = {
  "apiKey": "AIzaSyDfNxPHQGIRtxDhHYkuo-CJufhrtWWk2aM",
  "authDomain": "to-do-80e38.firebaseapp.com",
  "projectId": "to-do-80e38",
  "storageBucket": "to-do-80e38.appspot.com",
  "messagingSenderId": "1002597984018",
  "appId": "1:1002597984018:web:2507bef9113a5cf10135cb",
  "measurementId": "G-7588TXLL0W",
  "databaseURL":"https://to-do-80e38-default-rtdb.firebaseio.com/",

}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()


app = Flask(__name__)
key = b'd7HosJdo-_M4-igKIR3_xO-r2Nr7hXPDmFbQe2cyT4A='
f = Fernet(key)

def enc(string_for_enc):
    out = f.encrypt(string_for_enc.encode())
    return out.decode()

def dec(string_for_dec):
    out = f.decrypt(string_for_dec.encode())
    return out.decode() 

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/sign/in',methods=["POST","GET"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            auth.sign_in_with_email_and_password(email,password)
            return redirect(f"/home?email={enc(email)}&password={enc(password)}")

        except:
            return render_template("signin.html",error=True)
    msg = request.args.get("msg")
    if msg != None:
        email = dec(request.args.get('email'))
        return render_template("signin.html",msg=msg,newAcc=True,email=email)
    else:
        return render_template("signin.html")


@app.route('/sign/up',methods=["POST","GET"])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            auth.create_user_with_email_and_password(email,password)
            return redirect(f'/sign/in?msg=You registered to system you can login by typing in your info.&email={enc(email)}')
        except  Exception as err:

            return render_template("signup.html",error=True,exc=err)
    return render_template("signup.html")

"""Main stuff"""
@app.route('/home',methods=["POST","GET"])
def home():
    email = dec(request.args.get('email'))
    usernameSplitter = email.split('@')
    username = usernameSplitter[0]

    if request.method == "POST":
        
        data = {
            "todo":request.form.get('todo'),
            "username":username
        }
        db.child("todos").child(username).child("todos").push(data)

        return redirect(f"/home?email={request.args.get('email')}&password={request.args.get('password')}")
    return render_template("home.html",email=email,todos=json.loads(requests.get(f"{firebaseConfig['databaseURL']}/todos/{username}/todos.json").content),emailENC=request.args.get('email'),password=request.args.get('password'))


class Functions:
    @app.route('/open')
    def open():
        url = request.args.get('url')
        return render_template("open.html",url=url,hosting=hosting)

    @app.route('/save')
    def save():
        userAgentData = request.args.get('uad')
        ip_addr =  request.args.get("ip")
        import time
        data = {
            "userAgent":json.loads(userAgentData),
            "ip":ip_addr,
            "time":time.ctime(time.time()),
            "platform":request.args.get('platform'),
            "page":request.args.get("page")

        }
        db.child("Logs").push(data)


        return {"save":True}

@app.route('/delete')
def delete():
    email = request.args.get('email')
    password = request.args.get('password')
    usernameSplitter = dec(email).split('@')
    id = request.args.get('id')
    username  = usernameSplitter[0]
    db.child("todos").child(username).child("todos").child(id).remove()
    return redirect(f"/home?email={email}&password={password}")

app.run(debug=True)