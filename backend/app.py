from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from email_validator import validate_email, EmailNotValidError
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_session import Session
from flask_cors import CORS
import searchShorter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aditya'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
app.config['MONGO_URI'] = 'mongodb://localhost:27017/edvocate'
bcrypt = Bcrypt(app)
mongo = PyMongo(app)
Session(app)
CORS(app)

@app.route('/register', methods=['POST', 'GET'])
def registration():
    data = request.json
    print(data)

    if request.method == 'POST':
        if data['password'] == data['passwordb']:
            print(data)
            fullname = data['fullName']
            email = data['email']
            phone = data['phone']
            aadhar_number = data['aadhar']
            password = data['password']
            confirm_password = data['passwordb']
            user = mongo.db.users.find_one({'email': email})
            if user:
                return jsonify({'message': 'This email already exists'}), 401
            else:
                try:
                    validate_email(email)
                    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                    user_data = {
                        'fullname': fullname,
                        'email': email,
                        'phone': phone,
                        'aadhar_number': aadhar_number,
                        'password': password_hash,
                    }
                    mongo.db.users.insert_one(user_data)
                    return jsonify({'message': 'Successful registration'}), 201
                except EmailNotValidError as e:
                    return jsonify({'message': 'Invalid email format'}), 401
        else:
            return jsonify({'message': 'Your passwords do not match'}), 401
    else:
        return jsonify({'message': 'Invalid request method'}), 401
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    print("login routed")
    if request.method == 'POST':
        data=request.json
        print(data)
        password=data['password']
        user=mongo.db.users.find_one({'email':data['email']})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['email']=user['email']
            user_id=user['email'].split('@')[0]
            print(user_id)
            user_data={"user_id":user_id}
            return jsonify(user_data), 200
        else:
            return jsonify({"message":"Wrong method"}), 401
    else:
        return({'message':'wrong method'}), 401
    


@app.route('/signup_adv', methods=['POST','GET'])
def advSignup():
    if request.method=='POST':
        data=request.json
        email=data['email']
        user=mongo.db.advs.find_one({'email':email})
        if user:
            return jsonify({"message":"User already exists with this email"})
        else:
            password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            adv_data = {
                'fullname': data['fullname'],
                'email': email,
                'phone': data['phone'],
                'aadhar_number': data['aadhar_number'],      
                'state':data['State'],
                'city':data['City'],
                'cat1':data['cat1'],
                'cat2':data['cat2'],
                'cat3':data['cat3'],
                'court':'Civil',
                'password': password_hash,
                }

            mongo.db.advs.insert_one(adv_data)
            return jsonify({'message':"Sucessfully Registerd"}), 201
    
        print(data)
    return "wrong method "


@app.route('/search/adevocate', methods=['POST',"GET"])
def search():
    data=request.json
    search_result=[]
    advs=mongo.db.advs.find({'state':data['State']})
    results=searchShorter.shorter(advs)#we have to add searching algorithm
    for result in results:
        search_result.append(result)
    print(search_result)
    return jsonify(search_result)




if __name__ == '__main__':
    app.run(debug=True)
