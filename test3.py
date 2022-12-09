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
from functools import wraps

import os

jwt = JWTManager()

app = Flask(__name__)
pjdir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ \
    os.path.join(pjdir, 'database1.db')

jwt.init_app(app)
jwt=JWTManager(app)

app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config["JWT_COOKIE_SECURE"] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

db = SQLAlchemy(app)
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
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(20),)
    email    = db.Column(db.String(20), nullable=False,unique=True)
    password = db.Column(db.String(80),)
    phone    = db.Column(db.String(10),)
    type     = db.Column(db.String(10),)

class Product(db.Model):
    __tablename__='Product'
    id  = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name    = db.Column(db.String(20),)
    description = db.Column(db.String(20))
    picture = db.Column(db.String)
    colors = db.Column(db.String)
    sizes = db.Column(db.String)
    inventories = db.Column(db.Integer,)
    available = db.Column(db.Boolean)
    price   = db.Column(db.Integer,)
    startAt = db.Column(db.Date)
    endAt   = db.Column(db.Date)
    sellerId = db.Column(db.Integer,db.ForeignKey("User.id", ondelete="CASCADE"))
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
    id  = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String,db.ForeignKey("Product.colors", ondelete="CASCADE"))  
    color    = db.Column(db.String)

class Size(db.Model):
    __tablename__='Size'
    id  = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String,db.ForeignKey("Product.sizes", ondelete="CASCADE"))  
    size    = db.Column(db.String)


class RegisterForm(FlaskForm):
    name = StringField(validators=[
                           InputRequired(), Length(max=10)], render_kw={"placeholder": "Name"})
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})
    phone = StringField(validators=[
                           InputRequired(), Length(max=10)], render_kw={"placeholder": "Phone"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')
    def validate_email(self,email):
        existing_user_email= User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class PatchForm(FlaskForm):
    name = StringField(validators=[
                           InputRequired(), Length(max=10)], render_kw={"placeholder": "Name"})
    phone = StringField(validators=[
                           InputRequired(), Length(max=10)], render_kw={"placeholder": "Phone"})
    submit = SubmitField('Update')

class ProductForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(max=10)], render_kw={"placeholder": "Name"})
    description = StringField(validators=[InputRequired(), Length(max=100)], render_kw={"placeholder": "briefy describe"})
    picture = StringField(validators=[InputRequired(), Length(max=100)], render_kw={"placeholder": "link"})
    colors = StringField(validators=[InputRequired(), Length(max=100)], render_kw={"placeholder": "colors"}) ##need color form
    sizes = StringField(validators=[InputRequired(), Length(max=100)], render_kw={"placeholder": "sizes"}) ##need size form
    price = IntegerField('price', validators=[InputRequired()])
    available = BooleanField(false_values=(False, 'false','False'))
    startAt = DateField('start_time',format="%Y-%m-%d")
    endAt = DateField('end_time',format="%Y-%m-%d")
    submit = SubmitField('upload')

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/users/signIn', methods=['GET', 'POST'])
def login():
    form = LoginForm()   
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                response = jsonify({"msg": "login successful"})
                access_token = create_access_token(identity=user.id)
                set_access_cookies(response, access_token)
                
                return redirect(url_for('dashboard', jwt=access_token))
            else:
                return make_response('Please insert correct password!', 403, {'wWW-Authenticate':'Basic realm: "Authentication Failed!"'}) 
        return make_response('User not found!', 403, {'wWW-Authenticate':'Basic realm: "Authentication Failed!"'})          
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    jwt = request.args.get('jwt')
    return render_template('dashboard.html',jwt=jwt)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return redirect(url_for('login'))

@app.route('/users/me', methods=['GET','POST'])
@login_required
@jwt_required()
def patch():
    form=PatchForm()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    jwt = request.args.get('jwt')
    if form.validate_on_submit():
           user.name=form.name.data 
           user.phone=form.phone.data
           db.session.add(user)
            #User.name=form.name.data
            #User.phone=form.phone.data
           db.session.commit()
           return redirect(url_for('dashboard',jwt=jwt))
    
    return render_template('patch.html',form=form,jwt=jwt)

@ app.route('/users', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data,email=form.email.data, password=hashed_password,phone=form.phone.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route("/users/<int:id>", methods=["GET"])
@login_required
@jwt_required()
def single_book(id):
    if request.method == "GET":
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        now_data={
            "status": 0,
            "message": "success",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone
            }

        }
        if id!=user.id:
            return 'Unauthenticated!'
        return jsonify(now_data)

@app.route("/sellers/me/products", methods=["GET","POST"])
@login_required
@jwt_required()
def product():
    form=ProductForm()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    jwt = request.args.get('jwt')
    if form.validate_on_submit():
        
        new_user = Product(name=form.name.data,description=form.description.data,colors=form.colors.data,sizes=form.sizes.data,price=form.price.data,picture=form.picture.data,available=form.available.data,startAt=form.startAt.data,endAt=form.endAt.data,sellerId=user.id )
        new_colors=Color(color=form.colors.data,name=form.name.data)
        new_sizes=Size(size=form.sizes.data,name=form.name.data)
        
        
        db.session.add(new_user)
        db.session.add(new_colors)
        db.session.add(new_sizes)
        number_color=Color.query.filter(Color.color==form.colors.data,Color.name==form.name.data).count()
        number_size=Size.query.filter(Size.size==form.colors.data,Size.name==form.name.data).count()
        new_user.inventories=number_color+number_size
        db.session.commit()
        
        return redirect(url_for('product',jwt=jwt))
    
    conn = sqlite3.connect('database1.db')
    current_user_id = get_jwt_identity()
    #product = Product.query.filter(Product.name==form.name.data).first()

    c = conn.cursor()
    c.execute("SELECT id,name,available,price,startAt,colors,sizes,inventories,endAt,sellerId FROM product WHERE sellerId=?", (user.id,))
    rows = c.fetchall()
    columns = [col[0] for col in c.description]
    
    return render_template('product.html', form=form,jwt=jwt, rows=rows, columns=columns)    

@app.route("/sellers/<int:SellerId>/products", methods=["GET"])  ## get seller's products
@login_required
def get_seller_product(SellerId):
    jwt = request.args.get('jwt')
    c = sqlite3.connect('database1.db').cursor()
    c.execute("SELECT id,name,available,price,startAt,endAt,sellerId FROM product WHERE sellerId=?", (SellerId,))
    rows = c.fetchall()
    columns = [col[0] for col in c.description]

    return render_template('product1.html', jwt=jwt,rows=rows, columns=columns)

@app.route("/products/<int:ProductId>", methods=["GET","PATCH"])  ## get the product. update the product 
@login_required
def get_product(ProductId):
    jwt = request.args.get('jwt')
    c = sqlite3.connect('database1.db').cursor()
    c.execute("SELECT * FROM product WHERE id=?", (ProductId,))
    rows = c.fetchall()
    columns = [col[0] for col in c.description]

    return render_template('product2.html', jwt=jwt,rows=rows, columns=columns)
    

if __name__ == "__main__":
    app.run(debug=True)
