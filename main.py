from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime
import jsonify
import requests
import pickle
import sklearn
import joblib
from sklearn.preprocessing import StandardScaler
import numpy as np



with open('config.json','r') as c:
    params = json.load(c)["params"]

local_server=True
app = Flask(__name__)
model = pickle.load(open('random_forest_regression_model.pkl', 'rb'))
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]


db=SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=True)

@app.route("/")
def home():
    return render_template('index.html', params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/contact", methods=["GET","POST"])
def contact():
    if(request.method=="POST"):
        '''ADD ENTRY TO DATABASE'''
        name= request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry=Contacts(name = name,email = email,phone_num = phone,msg = message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender = email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone
                          )
    return render_template('contact.html', params=params)

@app.route("/post")
def post():
    return render_template('post.html', params=params)

@app.route("/car")
def car():
    return render_template('car.html',params=params)

@app.route("/auto")
def auto():
    return render_template('auto.html', params=params)
@app.route("/bike")
def bike():
    return render_template('bike.html', params=params)
@app.route("/bhubaneswar")
def bhubaneswar():
    return render_template('bhubaneswarhouse.html', params=params)
@app.route("/puri")
def puri():
    return render_template('purihouse.html', params=params)
@app.route("/cuttack")
def cuttack():
    return render_template('cuttackhouse.html', params=params)
standard_to = StandardScaler()
@app.route("/predict", methods=['POST'])
def predict():
    Fuel_Type_Diesel = 0
    if request.method == 'POST':
        Year = int(request.form['Year'])
        Present_Price = float(request.form['Present_Price'])
        Kms_Driven = int(request.form['Kms_Driven'])
        Kms_Driven2 = np.log(Kms_Driven)
        Owner = int(request.form['Owner'])
        Fuel_Type_Petrol = request.form['Fuel_Type_Petrol']
        if (Fuel_Type_Petrol == 'Petrol'):
            Fuel_Type_Petrol = 1
            Fuel_Type_Diesel = 0
        elif (Fuel_Type_Petrol == 'Diesel'):
            Fuel_Type_Petrol = 0
            Fuel_Type_Diesel = 1
        else:
            Fuel_Type_Petrol = 0
            Fuel_Type_Diesel = 0

        Year = 2020 - Year
        Seller_Type_Individual = request.form['Seller_Type_Individual']
        if (Seller_Type_Individual == 'Individual'):
            Seller_Type_Individual = 1
        else:
            Seller_Type_Individual = 0
        Transmission_Mannual = request.form['Transmission_Mannual']
        if (Transmission_Mannual == 'Mannual'):
            Transmission_Mannual = 1
        else:
            Transmission_Mannual = 0
        prediction = model.predict([[Present_Price, Kms_Driven2, Owner, Year, Fuel_Type_Diesel, Fuel_Type_Petrol,
                                     Seller_Type_Individual, Transmission_Mannual]])
        output = round(prediction[0], 2)
        if output < 0:
            return render_template('car.html', prediction_texts="Sorry you cannot sell this car", params=params)
        else:
            return render_template('car.html', prediction_text="You Can Sell The Car at {}".format(output),
                                   params=params)
    else:
            return render_template('car.html',params=params)

if __name__=="__main__":
    app.run(debug=True)
