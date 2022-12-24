from flask import Flask, render_template, url_for, redirect, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user ,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FieldList, FormField, IntegerField, BooleanField, DateField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import sqlite3,json
import jwt, datetime
from flask_jwt_extended import(
    JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies, set_access_cookies
)
from flask import Response
from functools import wraps
import sqlalchemy.types as types
import os



class ChoiceType(types.TypeDecorator):

    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]
# make a response by status, message, and data
def get_response_body(status, message, data=None):
    if data == None:
        return {"status": status, "message": message}
    return {"status": status, "message": message, "data":data}

app = Flask(__name__)
pjdir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ \
    os.path.join(pjdir, 'database1.db')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'IMG')


app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config["JWT_COOKIE_SECURE"] = False
app.config['JWT_SECRET_KEY'] = 'thisisasecretkey'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("database1.db")
    except sqlite3.error as e:
        print(e)
    return conn


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__='User'
    userID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(20),)
    email    = db.Column(db.String(20), nullable=False,unique=True)
    password = db.Column(db.String(80),)
    phone    = db.Column(db.String(10),)

class Product(db.Model):
    __tablename__='Product'
    productID  = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name    = db.Column(db.String(20),)
    description = db.Column(db.String(100))
    picture = db.Column(db.String)
    available = db.Column(db.Boolean)
    price   = db.Column(db.Integer,)
    startAt = db.Column(db.Date)
    endAt   = db.Column(db.Date)
    sellerID = db.Column(db.Integer)
'''
class List(db.Model):
    __tablename__='List'
    id  = db.Column(db.Integer, primary_key=True)
    itemId = db.Column(db.Integer,)
    inventory = db.Column(db.Integer,)
    productId = db.Column(db.Integer,db.ForeignKey("Product.id", ondelete="CASCADE"))
    color_id  = db.Column(db.Integer,db.ForeignKey("Color.id", ondelete="CASCADE"))
    size_id   = db.Column(db.Integer,db.ForeignKey("Size.id", ondelete="CASCADE"))   
'''
class Color(db.Model):
    __tablename__='Color'
    colorID  = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(20))  

class Size(db.Model):
    __tablename__='Size'
    sizeID  = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(20))  

class Item(db.Model):
    __tablename__='Item'
    itemID  = db.Column(db.Integer, primary_key=True,autoincrement=True)
    productID    = db.Column(db.Integer,)
    colorID = db.Column(db.Integer)
    sizeID = db.Column(db.Integer)
    inventory=db.Column(db.Integer)

class Activity(db.Model):
    __tablename__='Activity'
    activityID  = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name    = db.Column(db.String(20),)
    scope = db.Column(db.String(10),ChoiceType({"STORE":"store","PRODUCT":"product"}))
    type = db.Column(db.String(10),ChoiceType({"MINUS":"minus","MULTIPLY":"multiply"}))
    value = db.Column(db.Float)
    available = db.Column(db.Boolean)
    productID   = db.Column(db.Integer,)
    startAt = db.Column(db.Date)
    endAt   = db.Column(db.Date)
    sellerID = db.Column(db.Integer)

class Coupon(db.Model):
    __tablename__='Coupon'
    couponID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name    = db.Column(db.String(20),)
    scope = db.Column(db.String(10),ChoiceType({"STORE":"store","PRODUCT":"product"}))
    type = db.Column(db.String(10),ChoiceType({"MINUS":"minus","MULTIPLY":"multiply"}))
    vale = db.Column(db.Float)
    available = db.Column(db.Boolean)
    amount   = db.Column(db.Integer,)
    startAt = db.Column(db.Date)
    endAt   = db.Column(db.Date)
    productID =db.Column(db.Integer)
    sellerID = db.Column(db.Integer)

class Coupon2(db.Model):
    __tablename__='Coupon2'
    coupon2ID  = db.Column(db.Integer, primary_key=True,autoincrement=True)
    couponID  = db.Column(db.Integer)
    buyerID = db.Column(db.Integer)
    available = db.Column(db.Boolean)

class Order(db.Model):
    __tablename__='Order'
    orderID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    status = db.Column(db.String(13),ChoiceType({"CHECKING": "checking", "ESTABLISHED": "established", "DEALING":"dealing", "SENDED": "sended","FINISHED": "finished","CANCELED":"canceled"}))
    buyerID = db.Column(db.Integer) #ForeignKey
    sellerID = db.Column(db.Integer)  #ForeignKey  
    activityID = db.Column(db.Integer)
    couponID = db.Column(db.Integer)
    createAt = db.Column(db.Date)
    updateAt = db.Column(db.Date)    

class Order2(db.Model):
    __tablename__='Order2'
    order2ID  = db.Column(db.Integer, primary_key=True,autoincrement=True)
    orderID  = db.Column(db.Integer)
    itemId = db.Column(db.Integer)
    amount = db.Column(db.Integer)              


@app.route('/users/signIn', methods=['GET', 'POST'])
def users_signIn():
    email, password = request.get_json()['email'], request.get_json()['password']
    queryset = User.query.filter(email==User.email)
    if queryset.count() == 0:
        return jsonify({"User not exists, check if your email is correct"})

    user_password = queryset[0].password 
    if password != user_password:
        return jsonify({"Password incorrect"})

    userID = queryset[0].userID
    name = queryset[0].name
    access_token = create_access_token(identity=userID)
    data = {"id": userID, "token":access_token, "user":name}
    return jsonify({
        "status": "200",
        "message": "Sign in succeeded. Welcome back",
        "data" : data})

@app.route('/users/me', methods=['GET', 'PATCH'])
@jwt_required()
def patch():
    current_user_id = get_jwt_identity()
    queryset = User.query.get(current_user_id)
    
    data = {"userID":queryset.userID,
            "name":queryset.name,
            "email":queryset.email, 
            "phone":queryset.phone}
    # GET
    if request.method == 'GET':
        return jsonify({
            "status":"200",
            "message":"Get me",
            "data":data
            })
    # Patch
    name, phone = request.get_json()['name'], request.get_json()['phone']
    queryset.name=name 
    queryset.phone=phone
    db.session.add(queryset)       
    db.session.commit()
    data = {"userID":queryset.userID,
            "name":queryset.name,
            "email":queryset.email, 
            "phone":queryset.phone}
    return jsonify({
            "status":"200",
            "message":"Data has been successfully patched",
            "data":data
            })

@app.route("/users/<int:userID>", methods=["GET"])
def userID(userID):
    count=User.query.filter(userID==User.userID)
    if count.count()== 0:
        return jsonify("User is unfound"),404
    user = User.query.get(userID)
    data = {"userID":user.userID,
            "name":user.name,
            "email":user.email, 
            "phone":user.phone}        
    return jsonify({
            "status":"200",
            "message":"Get User",
            "data":data
            })

@app.route('/users', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name= request.get_json()['name']
        email= request.get_json()['email']
        password=request.get_json()['password']
        phone=request.get_json()['phone']
        queryset = User.query.filter(email==User.email)
        if queryset.count() > 0:
            return {"msg": "User already exists"}
        con=sqlite3.connect("database1.db")
        cur=con.cursor()
        cur.execute("INSERT INTO User(name,email,phone,password)values(?,?,?,?)",(name,email,phone,password))
        con.commit()
        userID = User.query.filter(email==User.email).first()
        data = {
            "id":userID.userID, 
            "name":userID.name, 
            "email":userID.email,
            "phone":userID.phone
        }
    return  jsonify({"status":"201","message":"Create Successfully","data": data})

def get_data(product_obj: Product):
    colorID_name = {color_obj['pk']: color_obj['fields']['name'] for color_obj in json.loads(serializers.serialize("json", Color.objects.all()))}
    sizeID_name = {size_obj['pk']: size_obj['fields']['name'] for size_obj in json.loads(serializers.serialize("json", Size.objects.all()))}
    productID, name, description, picture, price, available, startAt, endAt, sellerID = product_obj.productID, product_obj.name, product_obj.description, product_obj.picture, product_obj.price, product_obj.available, product_obj.startAt, product_obj.endAt, product_obj.sellerID
    colorIDs = list(set([item.colorID for item in Item.objects.filter(productID=productID)]))
    sizeIDs = list(set([item.sizeID for item in Item.objects.filter(productID=productID)]))
    colors_dic, sizes_dic = [dict(colorID=colorID, name=colorID_name[colorID]) for colorID in colorIDs], [dict(sizeID=sizeID, name=sizeID_name[sizeID]) for sizeID in sizeIDs]
    inventories = []
    for inventory_obj in Item.objects.filter(productID=productID):
        colorID, sizeID, inventory = inventory_obj.colorID, inventory_obj.sizeID, inventory_obj.inventory
        inventories.append(dict(color=dict(id=colorID, name=colorID_name[colorID]), size=dict(id=sizeID, name=sizeID_name[sizeID]), inventory=inventory))
    return dict(productID=productID, name=name, description=description, picture=picture, colors=colors_dic, sizes=sizes_dic, price=price, available=available, inventories=inventories, startAt=startAt, endAt=endAt, sellerID=sellerID)



@app.route('/sellers/me/activities', methods=['GET', 'POST'])
@jwt_required()
def sellers_for_activities():
    name = request.get_json()['name']
    scope = request.get_json()['scope']
    type = request.get_json()['type']
    value = request.get_json()['value']
    available = request.get_json()['available']
    startAt= request.get_json()['startAt']
    endAt = request.data['endAt']
    scope_choice, type_choice = ("STORE", "PRODUCT"), ("MINUS", "MULTIPLY")
    
    if scope not in scope_choice:
        return jsonify("Scope has to be one of STORE, PRODUCT"),400
    if type not in type_choice:
        return jsonify("Type has to be one of MINUS, MULTIPLY"),400
    
    if scope == "STORE":
        productID = 0
    else:
        productID = request.get_json()['productId']
        product = Product.query.filter(productID==Product.productID)
        if product.count() == 0:
            return jsonify("Product doesn't exist"),404
    
    if request.method == "POST":
        current_user_id = get_jwt_identity()
        user_now = User.query.get(current_user_id)
        con=sqlite3.connect("database1.db")
        cur=con.cursor()
        cur.execute("INSERT INTO Activity(name,scope,type,value,available,startAt,endAt,sellerID,productID)values(?,?,?,?,?,?,?,?,?)",(name,scope,type,value,available,startAt,endAt,user_now.id,productID))
        con.commit()
        activityID =  Activity.query.filter(name==Activity.name).first()
        data = {
            "activityID":activityID.activityID, 
            "name":activityID.name, 
            "scope":activityID.scope,
            "type":activityID.type,
            "value":activityID.value,
            "available":activityID.available,
            "startAt":activityID.startAt,
            "endAt":activityID.endAt,
            "productID":activityID.productID,
            "sellerID":user_now.id
        }
        return  jsonify({"status":"201","message":"Create activity Successfully","data": data})      

    # GET
    queryset = Activity.objects.filter(sellerID=id)
    if queryset.count() == 0:
        return Response(get_response_body(403, f"No product available"), status=403)
    data = [a_data['fields'] for a_data in json.loads(serializers.serialize("json", queryset))]
    return Response(get_response_body(200, f"List all activities of seller {id}", data), status=200)

if __name__ == "__main__":
    app.run(debug=True)
