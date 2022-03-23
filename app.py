from flask import Flask, render_template,redirect,url_for,request, flash
from flask_sqlalchemy import SQLAlchemy
import phonenumbers
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField,EmailField,DateField,DecimalField, SelectField,TextAreaField,SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Email,NumberRange, length,ValidationError,EqualTo
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager, UserMixin,current_user,login_user,logout_user,login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b\x1aL\x05}\xe6\xfb\xf2\xd5\x13`S\x89\x8f/\xc5\xfcO\x93fN?\xe1\xa1\xe1\x0b\x01\xf7\x88Y\x12\xbe|' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Perevoski.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
login = LoginManager(app)
admin = Admin(app,name = 'Admin')
login.login_view = 'login'
#Модель
class Users(UserMixin,db.Model):
    id_users = db.Column(db.Integer, primary_key = True)
    pib = db.Column(db.String(255))
    email = db.Column(db.String(150), index = True, unique = True)
    phone_number = db.Column(db.String(15))
    password_hash = db.Column(db.String(128))
    ts_registry = db.Column(db.DateTime, default = datetime.utcnow())
    role = db.Column(db.String(50),default = "User")
    citys = db.relationship("Citys",secondary = "orders")
    

    def __repr__(self):
        return  self.pib

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash,password)

    def get_id(self):
        return (self.id_users)
class Feedback(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    pib = db.Column(db.String(255))
    email = db.Column(db.String(155))
    phone_number = db.Column(db.String(15))
    comments = db.Column(db.String(255))
    ts_feedback = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.pib
class Citys(db.Model):
    __tablename__ = "citys"
    id = db.Column(db.Integer, primary_key = True)
    city = db.Column(db.String(255))
    users  = db.relationship("Users",secondary = "orders")

    def __repr__(self):
        return self.city

class Orders(db.Model):
    __tablename__ = "orders"
    id_orders = db.Column(db.Integer, primary_key = True)
    id_user= db.Column(db.Integer,db.ForeignKey('users.id_users'))
    cargo = db.Column(db.String(150))
    weight = db.Column(db.String(60))
    check_orders = db.Column(db.String(50),default = "В обробці")
    ts_orders = db.Column(db.DateTime,default = datetime.utcnow)
    city_sender= db.Column(db.Integer,db.ForeignKey('citys.id'))
    steet_sender= db.Column(db.String(255))
    house_number = db.Column(db.Integer)
    date_senders = db.Column(db.String(60),default ="__")
    date_recipients = db.Column(db.String(60),default ="__")
    pay_method = db.Column(db.String(60))
    suma = db.Column(db.String(60),default ="__")
    user = db.relationship('Users', backref="orders",overlaps ="citys,users")
    city = db.relationship('Citys', backref="orders", overlaps ="citys,users")
    
    
    def __repr__(self):
        return '<Name %r>' % self.cargo
    
    
    
class  AddOrders(FlaskForm):
	  Cargo = StringField("Вантаж якій треба перевести")
	


class Controller(ModelView):
     def is_accessible(self):
            return current_user.role == "Admin"
     def not_auth(self):
            return redirect(url_for('index'))

admin.add_view(Controller(Users, db.session))
admin.add_view(Controller(Feedback, db.session))
admin.add_view(Controller(Citys, db.session))
admin.add_view(Controller(Orders, db.session))














@login.user_loader
def load_user(id_users):
    return Users.query.get(int(id_users))




class FeedbackForm(FlaskForm):
    pib = StringField('Ваше повне ім`я',validators=[DataRequired()])
    email = EmailField('Ваша електрона адреса',validators=[DataRequired(),Email()])
    phone= StringField('Ваш номер телефона',validators=[DataRequired(), length(max = 15)],render_kw={"placeholder":"+380XXXXXXXXX"})
    comments = TextAreaField("Ваш коментар",validators=[DataRequired(),length( max=255,message='Кометар великий')])
    submit = SubmitField('Send')
    
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class UserUpdateForm(FlaskForm):
    pib = StringField('Ваше повне ім`я')
    email = EmailField('Ваша електрона адреса',validators=[Email()])
    phone= StringField('Ваш номер телефона')
    
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
    
    def validate_email(self,email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
            
    

    
#View


@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])

def index():
    form = FeedbackForm()
    if form.validate_on_submit():
        pib = form.pib.data
        email = form.pib.data
        phone_number = form.phone.data
        comments = form.comments.data
        feedback = Feedback(pib= pib,email = email, phone_number = phone_number, comments = comments)
        flash("Дані відпралено. Ми зв'язимся з вами.")
        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('index'))
 
      
    return render_template('index.html',form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)
    
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
      
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])	
    pib = StringField('Ваш ПІБ', validators=[DataRequired()])
    phone =StringField('Ваш номер телефона', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),length(min=8, max=16)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_email(self,email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
            

            
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

        



                
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(pib=form.pib.data, email=form.email.data,phone_number =form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)


 



@app.route('/contacts')
def contacts():
    return render_template ("contatcts.html")

@app.route('/price')
def price():
    return render_template("price.html")

@app.route('/dashboard',methods = ['GET', 'POST'])   
@login_required
def dashboard():
    form = UserUpdateForm()
    id = current_user.id_users
    usersupdate = Users.query.get_or_404(id)
    if request.method == "POST":
    	  usersupdate.pib = request.form['pib']
    	  usersupdate.email= request.form['email']
    	  usersupdate.phone_number= request.form['phone']
    	  try:
    	    db.session.commit()
    	    flash("Дані оновлено!")
    	    return render_template("dashboard.html",form = form,usersupdate = usersupdate,id = id)
    	  except(ValueError):
    	    flash("Помилка!")
    	    return render_template("dashboard.html",form = form,usersupdate = usersupdate,id = id)
    else:
        return render_template("dashboard.html",form = form,usersupdate = usersupdate,id=id)
@app.route('/delete/<int:id>',methods = ['GET', 'POST'])
@login_required
def delete(id):
    if id == current_user.id_users:
        usersdelete = Users.query.get_or_404(id)
      
        
        try:
            db.session.delete(usersdelete)
            db.session.commit()
            flash("Профіль видалено!")
            return redirect(url_for('index'))
        except(ValueError):
            return redirect(url_for('index'))
    else:
        flash("Помилка!")
        return redirect(url_for('dashboard'))	
        
         	
         	
         	
         
    

    	
    
        
          	    
          	    
          


    	
    	    
    
    		
    
         
         
       
    	
    







if  __name__ == "__main__":
        app.run(debug = True)
