import self as self
from flask_wtf import FlaskForm, RecaptchaField
import email_validator
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, TextAreaField, \
    FloatField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flasksystem.models import User, Area, Devisionoffice, Farmworker, Crop, SysCrop, SysSubCategory, Field_Visit
import phonenumbers
from flask_login import current_user


# Registration form
class RegistrationForm(FlaskForm):
    fristname = StringField('Frist Name', validators=[DataRequired(), Length(min=4, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = IntegerField('Phone', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10)])
    # district = SelectField('District', choices=[], validators=[DataRequired()], coerce=int)
    # area = SelectField('Area', choices=[], validators=[DataRequired()], coerce=int)
    # usertype = SelectField('User Type', choices=[('Farmer','Farmer')], validators=[DataRequired()]
    # devisionoffice = SelectField('Devison Office', choices=[], validators=[DataRequired()], coerce=int)
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken.Please choose a another email!')

    def validate_phone(self, phone):

        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('That Phone Number is taken.Please choose a another Phone Number!')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login Here')


# Update Account Form Validations
class UpdateAccountForm(FlaskForm):
    fristname = StringField('Frist Name', validators=[DataRequired(), Length(min=4, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = IntegerField('Phone', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10)])
    # district = SelectField('District', choices=[], validators=[DataRequired()], coerce=int)
    # area = SelectField('Area', choices=[], validators=[DataRequired()], coerce=int)
    # active = SelectField('Account Status', choices=[('1', 'Active'), ('0', 'Deactive')], validators=[DataRequired()])
    # devisionoffice = SelectField('Devison Office', choices=[], validators=[DataRequired()],coerce=int)
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update My Account')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken.Please choose a another email!')

    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('That Phone Number is taken.Please choose a another Phone Number!')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request to password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email!,You must Register Frist')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class InsertNewFarmForm(FlaskForm):
    farmname = StringField('Farm Name', validators=[DataRequired(), Length(min=4, max=50)])
    latitude = FloatField('Laitude', validators=[DataRequired()])
    longitude = FloatField('Longtude', validators=[DataRequired()])
    phone = IntegerField('Phone', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    surface = IntegerField('Surface(Ha)', validators=[DataRequired()])
    submit = SubmitField('Insert Farm')


class AddFarmWokerForm(FlaskForm):
    fristname = StringField('Frist Name', validators=[DataRequired(), Length(min=4, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=4, max=50)])
    gender = SelectField('Gender', choices=[('1', 'Male'), ('0', 'Female')], validators=[DataRequired()])
    dob = DateField('DOB', format='%Y-%m-%d')
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10)])
    phone = IntegerField('Phone', validators=[DataRequired()])
    type = SelectField('Woker Type', choices=[('Permernet', 'Permernet'), ('Casual', 'Casual')],
                       validators=[DataRequired()])
    submit = SubmitField('Insert')

    def validate_phone(self, phone):
        frmworker = Farmworker.query.filter_by(worker_phone=phone.data).first()
        if frmworker:
            raise ValidationError('That Phone Number is taken.Please choose a another Phone Number!')


class FarmCropForm(FlaskForm):
    cropename = StringField('Crop Name', validators=[DataRequired(), Length(min=4, max=50)])

    def validate_crop(self, cropename):
        crop = Crop.query.filter_by(cropeName=cropename.data).first()
        if crop:
            raise ValidationError('Crop is All ready Exits!')


class AddUserForm(FlaskForm):
    fristname = StringField('Frist Name', validators=[DataRequired(), Length(min=4, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = IntegerField('Phone', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10)])
    usertype = SelectField('User Type',
                           choices=[('Farmer', 'Farmer'), ('ARPA', 'Agriculture Reserch and Product Assistant'),
                                    ('ADO', 'Agriculture Development Officer')], validators=[DataRequired()])
    # district = SelectField('District', choices=[], validators=[DataRequired()], coerce=int)
    # area = SelectField('Area', choices=[], validators=[DataRequired()], coerce=int)
    # usertype = SelectField('User Type', choices=[('Farmer','Farmer')], validators=[DataRequired()]
    # devisionoffice = SelectField('Devison Office', choices=[], validators=[DataRequired()], coerce=int)
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken.Please choose a another email!')

    def validate_phone(self, phone):

        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('That Phone Number is taken.Please choose a another Phone Number!')


class AddUserForm2(FlaskForm):
    fristname = StringField('Frist Name', validators=[DataRequired(), Length(min=4, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = IntegerField('Phone', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10)])
    # usertype = SelectField('User Type',choices=[('Farmer','Farmer'),('ARPA','Agriculture Reserch and Product Assistant'),('ADO','Agriculture Development Officer')],validators=[DataRequired()])
    # district = SelectField('District', choices=[], validators=[DataRequired()], coerce=int)
    # area = SelectField('Area', choices=[], validators=[DataRequired()], coerce=int)
    # usertype = SelectField('User Type', choices=[('Farmer','Farmer')], validators=[DataRequired()]
    # devisionoffice = SelectField('Devison Office', choices=[], validators=[DataRequired()], coerce=int)
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken.Please choose a another email!')

    def validate_phone(self, phone):

        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('That Phone Number is taken.Please choose a another Phone Number!')


class SysCropForm(FlaskForm):
    system_crop_name = StringField('Main Crop Catogrey Name', validators=[DataRequired(), Length(min=4, max=50)])
    system_crop_sci_name = StringField('Crop Science Name', validators=[DataRequired(), Length(min=4, max=50)])
    system_crop_catgoery = SelectField('Crop Catogery',
                                       choices=[('Food Crops', 'Food Crops'), ('Fiber Crops', 'Fiber Crops'),
                                                ('Oil Crops', 'Oil Crops'),
                                                ('Ornamental Crops', 'Ornamental Crops'),
                                                ('Industrial Crops', 'Industrial Crops'),
                                                ('Harvesting Crops', 'Harvesting Crops'), ('GMO', 'GMO')],
                                       validators=[DataRequired()])
    system_crop_growing_time = StringField('Growing Time Months', validators=[DataRequired()])
    system_crop_image = FileField('Crop Image', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    submit = SubmitField('Submit')

    def validate_crop(self, system_crop_name):
        syscrop = SysCrop.query.filter_by(system_crop_name=system_crop_name.data).first()
        if syscrop:
            raise ValidationError('This crop alreday in Database!')


class SysSubCategoryForm(FlaskForm):
    variety_name = StringField('Variety Name', validators=[DataRequired(), Length(min=4, max=50)])
    line_designation = StringField('Line Designation', validators=[DataRequired(), Length(min=4, max=50)])
    pedgiree = StringField('Pedgiree', validators=[DataRequired(), Length(min=4, max=50)])
    origin = StringField('Origin', validators=[DataRequired(), Length(min=4, max=50)])
    method_of_propagation = StringField('Method of Propagation', validators=[DataRequired(), Length(min=4, max=50)])
    sub_crop_image = FileField('Varity Image', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    submit = SubmitField('Submit')

    def validate_crop(self, variety_name):
        syssubcategory = SysSubCategory.query.filter_by(variety_name=variety_name.data).first()
        if syssubcategory:
            raise ValidationError('This Variety alreday in Database!')


class Field_VisitForm(FlaskForm):
    field_visit_date = DateField('Date', format='%Y-%m-%d')
    field_visit_name = StringField('Task Name', validators=[DataRequired(), Length(min=4, max=50)])
    ado_field_visit_descreption = StringField('Descreption', validators=[DataRequired(), Length(min=4, max=250)])
    # attach_document = FileField('Document', validators=[FileAllowed(['pdf', 'docx','csv','xlsx'])])
    submit = SubmitField('Submit')
