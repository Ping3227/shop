from flask import Flask, render_template, url_for, redirect, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user ,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FieldList, FormField, IntegerField, BooleanField, DateField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import sqlite3,json
import jwt
import datetime
from flask_jwt_extended import(
    JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies, set_access_cookies
)
from flask import Response
from functools import wraps
import sqlalchemy.types as types
import os
from itertools import chain


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

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=90)

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
    inventories = db.Column(db.Integer)
    available = db.Column(db.Boolean)
    colors = db.Column(db.String(20))
    sizes = db.Column(db.String(20))
    price   = db.Column(db.Integer,)
    startAt = db.Column(db.DateTime)
    endAt   = db.Column(db.DateTime)
    sellerID = db.Column(db.Integer)

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



@app.route("/sellers/me/products", methods=["GET","POST"])
@jwt_required()
def product():
    current_user_id = get_jwt_identity()
    

    if request.method == "POST":
        name, description, picture, colors, sizes, price, available, startAt, endAt = request.get_json()['name'], request.get_json()['description'], request.get_json()['picture'], request.get_json()['colors'], request.get_json()['sizes'], request.get_json()['price'],bool( request.get_json()['available']), request.get_json()['startAt'], request.get_json()['endAt']
        
        ##find product 
        queryset = Product.query.filter(name==Product.name)
        if queryset.count() == 0:
            ## build product
            new_product = Product(name=name,description=description,price=price,picture=picture,available=available,startAt= datetime.datetime.strptime(startAt, "%Y-%m-%d").date(),endAt= datetime.datetime.strptime(endAt, "%Y-%m-%d").date(),sellerID=current_user_id,inventories=0)
            db.session.add(new_product)
            db.session.commit()
        queryset = Product.query.filter(Product.name==name).first()      
        Colorquery=Color.query.filter(Color.name==colors)
        ##find if color exist 
        if Colorquery.count()==0:
            new_color=Color(name=colors)
            db.session.add(new_color)
            if queryset.sizes is None:
                queryset.colors=colors
            else:
                queryset.colors=queryset.colors+','+colors
            
            db.session.commit()
        Sizequery=Color.query.filter(Size.name==sizes)
        ##find if size exist 
        if Sizequery.count()==0:
            new_size=Size(name=sizes)
            db.session.add(new_size)
            if queryset.sizes is None:
                queryset.sizes=sizes
            else:
                queryset.sizes=queryset.sizes+','+sizes
            db.session.commit()

        ColorID=Color.query.filter(Color.name==colors).first().colorID
        SizeID=Size.query.filter(Size.name==sizes).first().sizeID
        ProductID=Product.query.filter(Product.name==name).first().productID 
        ##find item  
        queryitem= Item.query.filter(Item.colorID==ColorID,Item.sizeID==SizeID,Item.productID==ProductID)
        if queryitem.count()>0:
            return  jsonify("Product already exists"), 405
        else :
            new_item=Item(colorID=ColorID,sizeID=SizeID,productID=ProductID,inventory=1) 
            db.session.add(new_item)
            #update product
            queryset.inventories+=1
            db.session.add(queryset)
            db.session.commit()

            
        return  jsonify({"status":"201","message":"Create Product seccessfully"})

    if request.method == "GET":
        current_user_id = get_jwt_identity()
        
        c = sqlite3.connect('database1.db').cursor()
        c.execute("SELECT * FROM Product WHERE sellerID=?",(current_user_id,))
        rows = c.fetchall()
        columns = [col[0] for col in c.description]
        data=[dict(zip(columns,row)) for row in rows ]
        return jsonify ({
            "status":"200",
            "message":"Get Product",
            "data":data})

@app.route("/sellers/<int:sellerID>/products", methods=["GET"])
@jwt_required()
def sellerID_products(sellerID):
    queryset = Product.query.filter(sellerID==Product.sellerID)
    if queryset.count() == 0:
        return "Seller has no this product"

    current_user_id = get_jwt_identity()
    
    c = sqlite3.connect('database1.db').cursor()
    c.execute("SELECT * FROM Product WHERE sellerID=?", (current_user_id,))
    rows = c.fetchall()
    columns = [col[0] for col in c.description]
    data=[dict(zip(columns,row)) for row in rows ]
    return jsonify ({
            "status":"200",
            "message":"Get Product",
            "data":data})


@app.route("/products/<int:productID>", methods=["GET", "PATCH"])
@jwt_required()
def product_productID(productID):
    queryset = Product.query.filter(productID==Product.productID)
    if queryset.count() == 0:
        return "ProductID doesn't exist"
    if request.method == "PATCH":
        product=Product.query.get(productID)
        current_user_id = get_jwt_identity()
        
        if current_user_id != product.sellerID:
            return "This Product isn't yours" 
        name, description, picture, price, available, startAt, endAt = request.get_json()['name'], request.get_json()['description'], request.get_json()['picture'],  request.get_json()['price'],bool( request.get_json()['available']), request.get_json()['startAt'], request.get_json()['endAt']    
        ##change name description available startAt  endAt link name  price 
        product.name=name
        product.description=description
        product.picture=picture
        product.price=price
        product.startAt= datetime.datetime.strptime(startAt, "%Y-%m-%d").date()
        product.endAt= datetime.datetime.strptime(endAt, "%Y-%m-%d").date()
        product.available=available
        db.session.add(product)       
        db.session.commit()
        data = {
            "id": product.productID,
            "name": product.name,
            "description": product.description,
            "picture": product.picture,
            "colors": product.colors,
            "sizes": product.sizes,
            "price": product.price,
            "available": product.available,
            "inventories": product.inventories,
            "startAt": product.startAt,
            "endAt": product.endAt,
            "sellerId": product.sellerID
        }
        return jsonify ({
            "status":"200",
            "message":"Product has been successfully patched",
            "data":data}) 
    product=Product.query.get(productID)              
    message = "Get product"
    data = {
        "id": product.productID,
        "name": product.name,
        "description": product.description,
        "picture": product.picture,
        "colors": product.colors,
        "sizes": product.sizes,
        "price": product.price,
        "available": product.available,
        "inventories": product.inventories,
        "startAt": product.startAt,
        "endAt": product.endAt,
        "sellerId": product.sellerID
  }
    return jsonify ({
            "status":"200",
            "message": message,
            "data":data})                

@app.route("/products/<int:productID>/inventories", methods=["GET", "PATCH"])
@jwt_required()
def patch_inventories(productID):
    if request.method=='PATCH':
        queryset = Product.query.filter(productID==Product.productID)
        if queryset.count() == 0:
            return "Product isn't exists",403
        product=Product.query.get(productID)
        current_user_id = get_jwt_identity()
        
        if current_user_id != product.sellerID:
                return "This Product isn't yours"

        color, size, inventory = request.get_json()['color'], request.get_json()['size'], request.get_json()['inventory']
        color = Color.query.filter(color==Color.name)
        size =  Size.query.filter(size==Size.name)
        if color.count() ==0 and size.count() == 0:
            return "There's no product with colorID and sizeID ", 405
        colorID = color.first().colorID
        sizeID =  size.first().sizeID

        item=Item.query.filter(Item.colorID==colorID,Item.sizeID==sizeID)
        if item.count() ==0:
             return "There's no product with colorID and sizeID ", 405
        item= item.first()
       
        product.inventories=product.inventories-item.inventory
        item.inventory=inventory
        product.inventories=product.inventories+item.inventory
        
        db.session.add(product)   
        db.session.add(item)
        db.session.commit()
    product=Product.query.get(productID)
    message = "The inventory of product has been successfully patched"
    data = {
        "id": product.productID,
        "name": product.name,
        "description": product.description,
        "picture": product.picture,
        "colors": product.colors,
        "sizes": product.sizes,
        "price": product.price,
        "available": product.available,
        "inventories": product.inventories,
        "startAt": product.startAt,
        "endAt": product.endAt,
        "sellerId": product.sellerID
  }
    return jsonify ({
            "status":"200",
            "message": message,
            "data":data})   
        

"""
@app.route("/api/sellers/<int:SellerId>/products", methods=["GET"])  ## get seller's products
@login_required
def get_seller_product(SellerId):
    jwt = request.args.get('jwt')
    c = sqlite3.connect('database1.db').cursor()
    c.execute("SELECT id,name,available,price,startAt,endAt,sellerId FROM product WHERE sellerId=?", (SellerId,))
    rows = c.fetchall()
    columns = [col[0] for col in c.description]
    return render_template('product1.html', jwt=jwt,rows=rows, columns=columns)
@app.route("/api/products/<int:ProductId>", methods=["GET","PATCH"])  ## get the product. update the product 
@login_required
def get_product(ProductId):
    jwt = request.args.get('jwt')
    c = sqlite3.connect('database1.db').cursor()
    c.execute("SELECT id,name,description,colors,sizes,inventories,available,startAt,endAt,sellerId FROM product WHERE id=?", (ProductId,))
    rows = c.fetchall()
    columns = [col[0] for col in c.description]
    c.execute("SELECT picture FROM product WHERE id=?", (ProductId,))
    link = c.fetchone()
    return render_template('product2.html', jwt=jwt,rows=rows, columns=columns,link=link)
    
@app.route("/products/<int:ProductId>/invertories", methods=["GET","PATCH"]) ## update the products inventories 
@login_required
def update_product(ProductId):
    form=InventoriesForm()
    instance = Product.query.get(ProductId)
    jwt = request.args.get('jwt')
    if form.validate_on_submit():
           instance.inventories =form.inventories.data
           
           
           return redirect(url_for('update_product',jwt=jwt))
    return render_template('product3.html', jwt=jwt,)
### activity 
@app.route("/sellers/me/activities", methods=["GET","POST"]) ## create activity  ## get my activity 
@login_required
def my_activity():
    return 
@app.route("/sellers/<int:SellerId>/activities", methods=["GET","PATCH"])  ## get the product. update the product 
@login_required
def get_activity():
    return 
@app.route("//activities/<int:activityId>", methods=["PATCH"]) ## update the products inventories 
@login_required
def update_activity():
    return 
### coupon 
@app.route("/sellers/me/coupons", methods=["GET","POST"])   ## get and create 
@login_required
def my_seller_coupon():
    return 
@app.route("/sellers/<int:SellerId>/coupons", methods=["GET"]) ## get seller's coupon
@login_required
def get_coupons():
    return 
@app.route("/coupons/<int:CouponId>", methods=["PATCH"]) ##  update coupon
@login_required
def update_coupon():
    return 
@app.route("/buyers/me/coupons", methods=["GET"]) ## get my coupons
@login_required
def get_coupon():
    return 
@app.route("/buyers/me/coupons/<int:CouponId>", methods=["POST"]) ## create coupon 
@login_required
def my_buyer_coupon():
    return 
### orders
@app.route("/buyers/me/orders", methods=["POST","GET"]) 
@login_required
def my_buyer_order():
    return 
@app.route("/sellers/me/orders", methods=["GET"]) 
@login_required
def my_seller_order():
    return 
@app.route("/orders/<int:OrderId>", methods=["GET","PATCH"]) 
@login_required
def get_order():
    return 
"""

if __name__ == "__main__":
    app.run(debug=True)
