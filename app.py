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

    def __repr__(self):
        return '<Name %r>' % self.ts_registry
    











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


class Controller(ModelView):
     def is_accessible(self):
            return current_user.role == "Admin"
     def not_auth(self):
            return redirect(url_for('index'))

admin.add_view(Controller(Users, db.session))
admin.add_view(Controller(Feedback, db.session))













@login.user_loader
def load_user(id_users):
    return Users.query.get(int(id_users))



#Форма
class FeedbackForm(FlaskForm):
    pib = StringField('Ваше повне ім`я',validators=[DataRequired()])
    email = EmailField('Ваша електрона адреа',validators=[DataRequired(),Email()])
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
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
    

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
    

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")    






if  __name__ == "__main__":
        app.run(debug = True)