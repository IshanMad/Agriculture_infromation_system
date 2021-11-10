import secrets
import os
import time
from datetime import date, datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session, jsonify, abort, send_from_directory
from sqlalchemy import func
from flasksystem import app, db, bcrypt, mail, client, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flasksystem.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, \
    InsertNewFarmForm, AddFarmWokerForm, FarmCropForm, AddUserForm, SysCropForm, SysSubCategoryForm, AddUserForm2, \
    Field_VisitForm
from flasksystem.models import User, District, Area, Devisionoffice, Farm, Farmworker, FarmworkerAlarms, \
    FarmWorkerComments, FarmWorkerDocuments, SysCrop, SysSubCategory, SubCatYield, Maturity, ImportantTrait, \
    ReactionToDisease, ReactionToInsectPest, QulityCharacteristic, Crop, CropSeason, SystemCommonFertilizerPlan, \
    FarmFertilizerPlan, SystemFertilizer, FarmFertilizerResults, System_Pest_Disease_Soulutions, \
    System_Pest_and_Diseases, Farm_pest_details, Field_Visit
from flask_login import login_user, login_required, current_user, logout_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from flasksystem import SocketIO, join_room, leave_room, send, socketio, emit


# Home Route
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


# Contact Route
@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )


# About Route
@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )


# Email Confirm Message
def send_confirm_email(user):
    token = user.get_email_confirm_token()
    massage = Message('Email confirmation link', sender='ishanmadhawa440@gmail.com', recipients=[user.email])
    massage.body = f'''To confirm your password and login, please visit fallowing link:
{url_for('confirm_email', token=token, _external=True)} 
If you want to access your Agri info account please use this confirmation link!     
     
     '''
    mail.send(massage)


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('This Email not in the Database', 'warning')
            redirect(url_for('login'))
        else:
            user_confirm = user.confirmed
            if (user_confirm == 0):
                send_confirm_email(user)
                flash(
                    'You need to confirm your email!,Email Confirmation link has been send your Email Please check your Email!! .',
                    'info')
                return redirect(url_for('email_confirmation_msg'))
            else:
                if user and bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('loginhome'))
                else:
                    flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


# Confirm Email Route
@app.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    user = User.verify_email_token(token)
    if user is None:
        flash('That is inavalid or expired token', 'warning')
        redirect(url_for('login'))
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.commit()
        flash('Email confirm sucess fully please re enter login credantiels to login', 'success')
        return redirect(url_for('login'))


# Email Confirm Message Route
@app.route('/email_confirmation_msg')
def email_confirmation_msg():
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    return render_template(
        'email_confirmation_msg.html',
        title='Email Confirmation Message',
        year=datetime.now().year,
    )


# Users Login Home Route
@app.route('/loginhome')
@login_required
def loginhome():
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template(
        'loginhome.html',
        title='User Home',
        image_file=image_file,
        year=datetime.now().year,

    )


# Farmer Route
@app.route('/farmer')
@login_required
def farmer():
    return render_template(
        'farmer.html',
        title='Farmer Home',
        year=datetime.now().year,

    )


@app.route('/arpa')
@login_required
def arpa():
    return render_template(
        'arpa.html',
        title='Agriculture  Home',
        year=datetime.now().year,

    )


# Agri Development Offficer Route
@app.route('/ado')
@login_required
def ado():
    return render_template(
        'ado.html',
        title='Agriyan Development Officer',
        year=datetime.now().year,

    )


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    form = RegistrationForm()

    district = District.query.all()
    area = Area.query.filter_by(district_id=1).all()
    devisionoffices = Devisionoffice.query.filter_by(area_id=2).all()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf-8')
        user = User(fristname=form.fristname.data, lastname=form.lastname.data, email=form.email.data,
                    password=hashed_password, phone=form.phone.data, address=form.address.data,
                    profile='defaultprofile.jpg', usertype='Farmer', active=1,
                    devisionoffice_id=request.form['devisionoffice'], created_timestamp=datetime.now(),
                    modified_timestamp=datetime.now(), confirmed=False)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('login'))

    return render_template(
        'register.html',
        title='Register',
        district=district,
        area=area,
        devisionoffices=devisionoffices,
        year=datetime.now().year, form=form
    )


# Get Select box Values
@app.route('/district/<district_id>')
def district(district_id):
    areas = Area.query.filter_by(district_id=district_id).all()

    areaListArray = []

    for area in areas:
        areaObj = {}
        areaObj['id'] = area.id
        areaObj['areaName'] = area.areaName
        areaListArray.append(areaObj)

    return jsonify({'areas': areaListArray})


# Get data from JASON format and return to it Register form
@app.route('/area/<area_id>')
def area(area_id):
    # get data from devison oficess using area id
    devisionoffices = Devisionoffice.query.filter_by(area_id=area_id).all()
    # Defining Array
    devisionofficesListArray = []
    # Passing data to Array and redirect it form
    for devisionoffice in devisionoffices:
        devisionofficeObj = {}
        devisionofficeObj['id'] = devisionoffice.id
        devisionofficeObj['officeName'] = devisionoffice.officeName
        devisionofficesListArray.append(devisionofficeObj)
    return jsonify({'devisionoffices': devisionofficesListArray})


# Logout Route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# Prifile picture Save Function
def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


# User Profile Route
@app.route('/myaccount', methods=['GET', 'POST'])
@login_required
def myaccount():
    form = UpdateAccountForm()
    ######################################################
    devisionoffices = Devisionoffice.query.all()
    ######################################################
    devisionoffice = Devisionoffice.query.filter_by(id=current_user.devisionoffice_id).first()
    devisionoffice_area_id = devisionoffice.area_id
    print(current_user.devisionoffice_id)
    print(devisionoffice_area_id)
    #####################################################
    area = Area.query.all()
    area_select = Area.query.filter_by(id=devisionoffice_area_id).first()
    area_districts_id = area_select.district_id
    # area = Area.query.filter_by(district_id=area_districts_id).all()

    ########################################################
    select_district = District.query.filter_by(id=area_districts_id).first()
    district = District.query.all()
    ###################################################
    if form.validate_on_submit():
        current_user.fristname = form.fristname.data
        current_user.lastname = form.lastname.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.active = int(request.form['active'])
        current_user.devisionoffice_id = request.form['devisionoffice']
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.profile = picture_file
        db.session.commit()
        flash('your account has been updated', 'success')
    elif request.method == 'GET':
        form.fristname.data = current_user.fristname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.address.data = current_user.address

    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    """Renders the about page."""
    return render_template(
        'myaccount.html',
        title='Myaccount',
        year=datetime.now().year,
        image_file=image_file,
        form=form,
        devisionoffices=devisionoffices,
        select_district=select_district,
        district=district,
        area_select=area_select,
        area=area,
        devisionoffice_area_id=devisionoffice_area_id,
        message='Your application description page.'
    )


# Password reset Email Message
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='ishanmadhawa440@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your account password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply igrone this email and no changes will be made

    '''
    mail.send(msg)


# password reset form
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', year=datetime.now().year, form=form)


# change password form
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Reset token invalid or expierd!', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been update! You are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', year=datetime.now().year, form=form)


# farm home
@app.route('/farm_home', methods=['GET', 'POST'])
@login_required
def farm_home():
    farm_count = Farm.query.filter_by(user_id=current_user.id).count()
    if (farm_count == 0):
        flash('You have no farm yet please add farm', 'danger')
        return redirect(url_for('addnewfarm'))
    else:
        farmdata = Farm.query.filter_by(user_id=current_user.id).all()

    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('farm_home.html', title='Farm Home', year=datetime.now().year, image_file=image_file,
                           farmdata=farmdata)


# add new farm
@app.route('/farm_home/addnewfarm', methods=['GET', 'POST'])
@login_required
def addnewfarm():
    form = InsertNewFarmForm()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    district = District.query.all()
    area = Area.query.filter_by(district_id=1).all()
    devisionoffices = Devisionoffice.query.filter_by(area_id=2).all()
    if form.validate_on_submit():

        farm = Farm(farmname=form.farmname.data, latitude=form.latitude.data, longitude=form.longitude.data,
                    phone=form.phone.data, address=form.address.data, email=form.email.data, user_id=current_user.id,
                    created_timestamp=datetime.now(), modified_timestamp=datetime.now(), surface=form.surface.data,
                    devisionoffice_id=request.form['devisionoffice'])
        db.session.add(farm)
        db.session.commit()
        flash('Your farm details insert sucessfully', 'success')
        return redirect(url_for('farm_home'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    return render_template('addnewfarm.html', title='Add new Farm', year=datetime.now().year, image_file=image_file,
                           form=form, district=district, area=area, devisionoffices=devisionoffices)


@app.route("/farm_home/<int:id>/my_farm", methods=['GET', 'POST'])
@login_required
def my_farm(id):
    farm = Farm.query.get_or_404(id)
    if farm.user_id != current_user.id:
        flash('This is not your farm', 'danger')
        return redirect(url_for('farm_home'))
    farmdata = Farm.query.filter_by(id=id).all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('my_farm_manage.html', title='Farm Home', year=datetime.now().year, image_file=image_file,
                           farmdata=farmdata)


@app.route("/farm_home/my_farm/<int:id>/farm_worker", methods=['GET', 'POST'])
@login_required
def farm_worker(id):
    form = AddFarmWokerForm()
    farm = Farm.query.get_or_404(id)
    if farm.user_id != current_user.id:
        flash('This is not your farm', 'danger')
        return redirect(url_for('farm_home'))
    farmdata = Farm.query.filter_by(id=id).all()
    if form.validate_on_submit():
        farmWoker = Farmworker(worker_frist_name=form.fristname.data, worker_last_name=form.lastname.data,
                               worker_gender=int(form.gender.data), worker_dob=form.dob.data,
                               worker_address=form.address.data, worker_phone=form.phone.data,
                               worker_type=form.type.data,
                               farm_id=id, created_timestamp=datetime.now(),
                               modified_timestamp=datetime.now())
        db.session.add(farmWoker)
        db.session.commit()
        flash('Employee adding  sucessfully', 'success')
        return redirect(url_for('farm_worker', id=id))

    myFarmWoker = Farmworker.query.filter_by(farm_id=id).order_by(Farmworker.created_timestamp.desc())
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('farm_worker.html', title='Farm Home', year=datetime.now().year, image_file=image_file,
                           farmdata=farmdata, form=form, myFarmWoker=myFarmWoker)


@app.route('/update_worker/<id>', methods=['GET', 'POST'])
@login_required
def update_worker(id):
    updteworkers = Farmworker.query.filter_by(id=id).all()
    userdetailsListArray = []
    for updteworker in updteworkers:
        upworkerObj = {}
        upworkerObj['id'] = updteworker.id
        upworkerObj['worker_frist_name'] = updteworker.worker_frist_name
        upworkerObj['worker_last_name'] = updteworker.worker_last_name
        upworkerObj['worker_gender'] = updteworker.worker_gender
        upworkerObj['worker_dob'] = updteworker.worker_dob.strftime('%Y-%m-%d')
        upworkerObj['worker_address'] = updteworker.worker_address
        upworkerObj['worker_phone'] = updteworker.worker_phone
        upworkerObj['worker_type'] = updteworker.worker_type

        userdetailsListArray.append(upworkerObj)
    return jsonify({'updteworkers': userdetailsListArray})


@app.route('/farm_update_worker', methods=['GET', 'POST'])
@login_required
def farm_update_worker():
    if request.method == 'POST':
        fid = request.form['fid']
        print(fid)
        updte_farmworkers = Farmworker.query.filter_by(id=fid).first()
        id = updte_farmworkers.farm_id
        farm = Farm.query.get_or_404(id)
        if farm.user_id != current_user.id:
            flash('This is not your farm', 'danger')
            return redirect(url_for('farm_home'))
        else:
            updte_farmworkers.worker_frist_name = request.form['fristname1']
            updte_farmworkers.worker_last_name = request.form['lastname1']
            updte_farmworkers.worker_gender = int(request.form['gender1'])
            converttime = request.form['dob1']
            updte_farmworkers.worker_dob = converttime
            updte_farmworkers.worker_address = request.form['address1']
            updte_farmworkers.worker_phone = request.form['phone1']
            updte_farmworkers.worker_type = request.form['type1']
            updte_farmworkers.modified_timestamp = datetime.now()
            db.session.commit()
            flash('Worker Details has been updated!', 'success')
            return redirect(url_for('farm_worker', id=id))


@app.route('/show_worker/<id>', methods=['GET', 'POST'])
@login_required
def show_worker(id):
    show_workers = Farmworker.query.filter_by(id=id).all()
    show_workerdetailsListArray = []
    for shwteworker in show_workers:
        shwteworkersObj = {}
        shwteworkersObj['id'] = shwteworker.id
        shwteworkersObj['worker_frist_name'] = shwteworker.worker_frist_name
        shwteworkersObj['worker_last_name'] = shwteworker.worker_last_name
        shwteworkersObj['worker_gender'] = shwteworker.worker_gender
        shwteworkersObj['worker_dob'] = shwteworker.worker_dob.strftime('%Y-%m-%d')
        shwteworkersObj['worker_address'] = shwteworker.worker_address
        shwteworkersObj['worker_phone'] = shwteworker.worker_phone
        shwteworkersObj['worker_type'] = shwteworker.worker_type

        show_workerdetailsListArray.append(shwteworkersObj)
    return jsonify({'show_workers': show_workerdetailsListArray})


@app.route('/insert_worker_alarm', methods=['GET', 'POST'])
@login_required
def insert_worker_alarm():
    if request.method == 'POST':
        frmwid = request.form['alrmfrmid']
        print(frmwid)
        updte_farmworkers = Farmworker.query.filter_by(id=frmwid).first()
        id = updte_farmworkers.farm_id
        farm = Farm.query.get_or_404(id)
        if farm.user_id != current_user.id:
            flash('This is not your farm', 'danger')
            return redirect(url_for('farm_home'))
        else:
            send_msg = request.form['msg']
            send_phn = request.form['showphone']
            response = client.send_message({'from': 'Vonage APIs', 'to': send_phn, 'text': send_msg})
            response = response['messages'][0]
            if response['status'] == '0':
                farmworkerAlarms = FarmworkerAlarms(worker_msg=send_msg, worker_phone=send_phn,
                                                    farmworker_id=frmwid, created_timestamp=datetime.now(),
                                                    modified_timestamp=datetime.now(), alrm_date=datetime.now())
                db.session.add(farmworkerAlarms)
                db.session.commit()
                flash('Message Send!', 'success')
                return redirect(url_for('farm_worker', id=id))
            else:
                flash('Message not send!' + response['error-text'], 'danger')
                return redirect(url_for('farm_worker', id=id))

    # flash('Worker Details has been updated!', 'success')
    # return redirect(url_for('farm_worker', id=id))


@app.route('/show_worker_alarms/<id>', methods=['GET', 'POST'])
@login_required
def show_worker_arams(id):
    get_user_alrms = FarmworkerAlarms.query.filter_by(farmworker_id=id).order_by(
        FarmworkerAlarms.created_timestamp.desc())
    show_worker_alarmsListArray = []
    for show_alarm in get_user_alrms:
        showalrmsObj = {}
        showalrmsObj['id'] = show_alarm.id
        showalrmsObj['worker_msg'] = show_alarm.worker_msg
        showalrmsObj['worker_phone'] = show_alarm.worker_phone
        showalrmsObj['created_timestamp'] = show_alarm.created_timestamp
        show_worker_alarmsListArray.append(showalrmsObj)
    return jsonify({'get_user_alrms': show_worker_alarmsListArray})


@app.route('/insert_worker_cmnt', methods=['GET', 'POST'])
@login_required
def insert_worker_cmnt():
    if request.method == 'POST':
        frmwkrid = request.form['wkrid']
        updte_farmworkers = Farmworker.query.filter_by(id=frmwkrid).first()
        id = updte_farmworkers.farm_id
        farm = Farm.query.get_or_404(id)
        if farm.user_id != current_user.id:
            flash('This is not your farm', 'danger')
            return redirect(url_for('farm_home'))
        else:
            workercmnt = request.form['cmnt']
            farmcmnt = FarmWorkerComments(worker_comment=workercmnt, farmworker_id=frmwkrid,
                                          created_timestamp=datetime.now(), modified_timestamp=datetime.now())
            db.session.add(farmcmnt)
            db.session.commit()
            flash('Comment Added!', 'success')
            return redirect(url_for('farm_worker', id=id))
    else:
        return redirect(url_for('farm_worker', id=id))


@app.route('/view_worker_cmnt/<id>', methods=['GET', 'POST'])
@login_required
def view_worker_cmnt(id):
    view_cmnts = FarmWorkerComments.query.filter_by(farmworker_id=id).order_by(
        FarmWorkerComments.created_timestamp.desc())
    show_worker_comentsListArray = []
    for show_cmnt in view_cmnts:
        showcmntObj = {}
        showcmntObj['id'] = show_cmnt.id
        showcmntObj['worker_comment'] = show_cmnt.worker_comment
        showcmntObj['created_timestamp'] = show_cmnt.created_timestamp.strftime('%Y-%m-%d')
        show_worker_comentsListArray.append(showcmntObj)
    return jsonify({'view_cmnts': show_worker_comentsListArray})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_document', methods=['GET', 'POST'])
@login_required
def upload_document():
    if request.method == 'POST':
        if request.method == 'POST':
            frmwkrid = request.form['docid']
            updte_farmworkers = Farmworker.query.filter_by(id=frmwkrid).first()
            id = updte_farmworkers.farm_id
            farm = Farm.query.get_or_404(id)
            if farm.user_id != current_user.id:
                flash('This is not your farm', 'danger')
                return redirect(url_for('farm_home'))
            else:
                if 'file' not in request.files:
                    flash('No file part', 'danger')
                    return redirect(request.url)
                file = request.files['file']

                if file.filename == '':
                    flash('No selected file', 'danger')
                    return redirect(url_for('farm_worker', id=id))
                if file and allowed_file(file.filename):
                    random_hex = secrets.token_hex(8)
                    _, f_ext = os.path.splitext(file.filename)
                    uniqename = random_hex + f_ext
                    filename = secure_filename(uniqename)
                    save_document = FarmWorkerDocuments(document_name=filename, farmworker_id=frmwkrid,
                                                        created_timestamp=datetime.now(),
                                                        modified_timestamp=datetime.now(),
                                                        doc_title=request.form['title'])
                    db.session.add(save_document)
                    db.session.commit()
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    flash('Upload Sucessfully', 'success')
                    return redirect(url_for('farm_worker', id=id))
    flash('Document not Upload', 'danger')
    return redirect(url_for('farm_worker', id=id))


@app.route('/show_worker_document/<id>', methods=['GET', 'POST'])
@login_required
def show_worker_document(id):
    get_user_docs = FarmWorkerDocuments.query.filter_by(farmworker_id=id).order_by(
        FarmWorkerDocuments.created_timestamp.desc())
    show_documentListArray = []
    for sho_doc in get_user_docs:
        shodocsObj = {}
        shodocsObj['id'] = sho_doc.id
        shodocsObj['document_name'] = sho_doc.document_name
        shodocsObj['farmworker_id'] = sho_doc.farmworker_id
        shodocsObj['doc_title'] = sho_doc.doc_title
        show_documentListArray.append(shodocsObj)
    return jsonify({'get_user_docs': show_documentListArray})


@app.route('/documents/<path:filename>', methods=['GET', 'POST'])
@login_required
def documents(filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
seasons = [('Maha', (date(Y, 1, 1), date(Y, 3, 20))),
           ('Yala', (date(Y, 3, 21), date(Y, 8, 20))),
           ('Maha', (date(Y, 8, 21), date(Y, 12, 31)))]


def get_season(now):
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)


@app.route("/farm_home/my_farm/<int:id>/farm_crop", methods=['GET', 'POST'])
@login_required
def farm_crop(id):
    form = FarmCropForm()
    farm = Farm.query.get_or_404(id)
    if farm.user_id != current_user.id:
        flash('This is not your farm', 'danger')
        return redirect(url_for('farm_home'))
    farmdata = Farm.query.filter_by(id=id).all()
    system_inbuild_crops = SysCrop.query.all()
    myfarmCrop = Crop.query.filter_by(farm_id=id).all()
    system_pest_and_diseases = System_Pest_and_Diseases.query.all()
    current_season = get_season(date.today())
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('farm_crop.html', title='Farm Crop', year=datetime.now().year, image_file=image_file,
                           farmdata=farmdata, system_inbuild_crops=system_inbuild_crops, myfarmCrop=myfarmCrop,
                           current_season=current_season, system_pest_and_diseases=system_pest_and_diseases)


@app.route('/crop/<id>', methods=['GET', 'POST'])
@login_required
def get_crop(id):
    get_systemcrops = SysCrop.query.filter_by(id=id)
    systemcropListArray = []
    for systemcrop in get_systemcrops:
        systemcropsObj = {}
        systemcropsObj['id'] = systemcrop.id
        systemcropsObj['system_crop_name'] = systemcrop.system_crop_name
        systemcropsObj['system_crop_sci_name'] = systemcrop.system_crop_sci_name
        systemcropsObj['system_crop_catgoery'] = systemcrop.system_crop_catgoery
        systemcropsObj['system_crop_growing_time'] = systemcrop.system_crop_growing_time
        systemcropsObj['system_crop_image'] = systemcrop.system_crop_image
        systemcropsObj['created_timestamp'] = systemcrop.created_timestamp.strftime('%Y-%m-%d')
        systemcropListArray.append(systemcropsObj)
    return jsonify({'get_systemcrops': systemcropListArray})


@app.route('/sub_crop/<id>', methods=['GET', 'POST'])
@login_required
def get_sub_crop(id):
    get_system_sub_crops = SysSubCategory.query.filter_by(syscrop_id=id)
    system_sub_crop_ListArray = []
    for subcrop in get_system_sub_crops:
        subcropObj = {}
        subcropObj['id'] = subcrop.id
        subcropObj['variety_name'] = subcrop.variety_name
        subcropObj['line_designation'] = subcrop.line_designation
        subcropObj['pedgiree'] = subcrop.pedgiree
        subcropObj['origin'] = subcrop.origin
        subcropObj['method_of_propagation'] = subcrop.method_of_propagation
        subcropObj['sub_crop_image'] = subcrop.sub_crop_image
        system_sub_crop_ListArray.append(subcropObj)
    return jsonify({'get_system_sub_crops': system_sub_crop_ListArray})


@app.route('/sub_crop_Detail/<id>', methods=['GET', 'POST'])
@login_required
def get_sys_sub_crop_detail(id):
    get_sys_sub_crop_details = SysSubCategory.query.filter_by(id=id)
    get_sys_sub_crop_detail_ListArray = []
    for sub_crop_detail in get_sys_sub_crop_details:
        syssubcropObj = {}
        syssubcropObj['id'] = sub_crop_detail.id
        syssubcropObj['variety_name'] = sub_crop_detail.variety_name
        syssubcropObj['line_designation'] = sub_crop_detail.line_designation
        syssubcropObj['pedgiree'] = sub_crop_detail.pedgiree
        syssubcropObj['origin'] = sub_crop_detail.origin
        syssubcropObj['method_of_propagation'] = sub_crop_detail.method_of_propagation
        syssubcropObj['sub_crop_image'] = sub_crop_detail.sub_crop_image
        syssubcropObj['created_timestamp'] = sub_crop_detail.created_timestamp.strftime('%Y-%m-%d')
        get_sys_sub_crop_detail_ListArray.append(syssubcropObj)
    return jsonify({'get_sys_sub_crop_details': get_sys_sub_crop_detail_ListArray})


@app.route('/get_sys_sub_crop_yield/<id>', methods=['GET', 'POST'])
@login_required
def get_sys_sub_crop_yield(id):
    get_sys_sub_crop_yields = SubCatYield.query.filter_by(syssubcategory_id=id)
    get_sys_sub_crop_yield_ListArray = []
    for sub_yield_detail in get_sys_sub_crop_yields:
        sysyieldObj = {}
        sysyieldObj['id'] = sub_yield_detail.id
        sysyieldObj['highest_yield_recorded'] = sub_yield_detail.highest_yield_recorded
        sysyieldObj['average_yield'] = sub_yield_detail.average_yield
        sysyieldObj['average_yield_yla'] = sub_yield_detail.average_yield_yla
        sysyieldObj['average_yield_mha'] = sub_yield_detail.average_yield_mha
        sysyieldObj['reaction_to_salinity'] = sub_yield_detail.reaction_to_salinity
        sysyieldObj['created_timestamp'] = sub_yield_detail.created_timestamp.strftime('%Y-%m-%d')
        get_sys_sub_crop_yield_ListArray.append(sysyieldObj)
    return jsonify({'get_sys_sub_crop_yields': get_sys_sub_crop_yield_ListArray})


@app.route('/get_sys_sub_crop_maturity/<id>', methods=['GET', 'POST'])
@login_required
def get_sys_sub_crop_maturity(id):
    get_sys_sub_crop_maturitys = Maturity.query.filter_by(syssubcategory_id=id)
    get_sys_sub_crop_maturity_ListArray = []
    for sub_yield_maturity in get_sys_sub_crop_maturitys:
        sysmaturityObj = {}
        sysmaturityObj['id'] = sub_yield_maturity.id
        sysmaturityObj['seson_name'] = sub_yield_maturity.seson_name
        sysmaturityObj['num_of_date'] = sub_yield_maturity.num_of_date
        get_sys_sub_crop_maturity_ListArray.append(sysmaturityObj)
    return jsonify({'get_sys_sub_crop_maturitys': get_sys_sub_crop_maturity_ListArray})


@app.route('/get_sys_sub_crop_important_trait/<id>', methods=['GET', 'POST'])
@login_required
def get_sys_sub_crop_important_trait(id):
    get_sys_sub_crop_important_traits = ImportantTrait.query.filter_by(syssubcategory_id=id)
    get_sys_sub_crop_important_trait_ListArray = []
    for sub_crop_important_trait in get_sys_sub_crop_important_traits:
        sysimportant_traitObj = {}
        sysimportant_traitObj['id'] = sub_crop_important_trait.id
        sysimportant_traitObj['traits_name'] = sub_crop_important_trait.traits_name
        sysimportant_traitObj['traits_descreption'] = sub_crop_important_trait.traits_descreption
        get_sys_sub_crop_important_trait_ListArray.append(sysimportant_traitObj)
    return jsonify({'get_sys_sub_crop_important_traits': get_sys_sub_crop_important_trait_ListArray})


@app.route('/get_sys_sub_crop_reaction_to_disease/<id>', methods=['GET', 'POST'])
@login_required
def get_sys_sub_crop_reaction_to_disease(id):
    get_sys_sub_crop_reaction_to_diseases = ReactionToDisease.query.filter_by(syssubcategory_id=id)
    get_sys_sub_crop_reaction_to_disease_ListArray = []
    for sub_crop_reaction_to_disease in get_sys_sub_crop_reaction_to_diseases:
        get_sys_reaction_to_diseaseObj = {}
        get_sys_reaction_to_diseaseObj['id'] = sub_crop_reaction_to_disease.id
        get_sys_reaction_to_diseaseObj['diseasese_name'] = sub_crop_reaction_to_disease.diseasese_name
        get_sys_reaction_to_diseaseObj['resistant'] = sub_crop_reaction_to_disease.resistant
        get_sys_reaction_to_diseaseObj['moderately_resistant'] = sub_crop_reaction_to_disease.moderately_resistant
        get_sys_reaction_to_diseaseObj['susceptible'] = sub_crop_reaction_to_disease.susceptible
        get_sys_reaction_to_diseaseObj['moderately_susceptible'] = sub_crop_reaction_to_disease.moderately_susceptible
        get_sys_sub_crop_reaction_to_disease_ListArray.append(get_sys_reaction_to_diseaseObj)
    return jsonify({'get_sys_sub_crop_reaction_to_diseases': get_sys_sub_crop_reaction_to_disease_ListArray})


@app.route('/get_sys_sub_crop_reaction_to_insect_pest/<id>', methods=['GET', 'POST'])
@login_required
def get_sys_sub_crop_reaction_to_insect_pest(id):
    get_sys_sub_crop_reaction_to_insect_pests = ReactionToInsectPest.query.filter_by(syssubcategory_id=id)
    get_sys_sub_crop_reaction_to_insect_pest_ListArray = []
    for get_sys_sub_crop_reaction_to_insect_pest in get_sys_sub_crop_reaction_to_insect_pests:
        get_sys_reaction_to_pestObj = {}
        get_sys_reaction_to_pestObj['id'] = get_sys_sub_crop_reaction_to_insect_pest.id
        get_sys_reaction_to_pestObj['diseasese_name'] = get_sys_sub_crop_reaction_to_insect_pest.diseasese_name
        get_sys_reaction_to_pestObj['resistant'] = get_sys_sub_crop_reaction_to_insect_pest.resistant
        get_sys_reaction_to_pestObj[
            'moderately_resistant'] = get_sys_sub_crop_reaction_to_insect_pest.moderately_resistant
        get_sys_reaction_to_pestObj['susceptible'] = get_sys_sub_crop_reaction_to_insect_pest.susceptible
        get_sys_reaction_to_pestObj[
            'moderately_susceptible'] = get_sys_sub_crop_reaction_to_insect_pest.moderately_susceptible
        get_sys_sub_crop_reaction_to_insect_pest_ListArray.append(get_sys_reaction_to_pestObj)
    return jsonify({'get_sys_sub_crop_reaction_to_insect_pests': get_sys_sub_crop_reaction_to_insect_pest_ListArray})


@app.route('/get_sys_sub_crop_qulity_characteristic/<id>', methods=['GET', 'POST'])
@login_required
def get_sys_sub_crop_qulity_characteristic(id):
    get_sys_sub_crop_qulity_characteristics = QulityCharacteristic.query.filter_by(syssubcategory_id=id)
    get_sys_sub_crop_qulity_characteristic_ListArray = []
    for get_sys_sub_crop_qulity_characteristic in get_sys_sub_crop_qulity_characteristics:
        get_sys_sub_crop_qulity_characteristiObj = {}
        get_sys_sub_crop_qulity_characteristiObj['id'] = get_sys_sub_crop_qulity_characteristic.id
        get_sys_sub_crop_qulity_characteristiObj[
            'characteristic_name'] = get_sys_sub_crop_qulity_characteristic.characteristic_name
        get_sys_sub_crop_qulity_characteristiObj[
            'characteristic_descreption'] = get_sys_sub_crop_qulity_characteristic.characteristic_descreption
        get_sys_sub_crop_qulity_characteristic_ListArray.append(get_sys_sub_crop_qulity_characteristiObj)
    return jsonify({'get_sys_sub_crop_qulity_characteristics': get_sys_sub_crop_qulity_characteristic_ListArray})


@app.route('/get_select_crop/<id>', methods=['GET', 'POST'])
@login_required
def get_select_crop(id):
    get_select_crops = SysSubCategory.query.filter_by(syscrop_id=id)
    get_select_crop_ListArray = []
    for get_select_crop in get_select_crops:
        get_select_cropObj = {}
        get_select_cropObj['id'] = get_select_crop.id
        get_select_cropObj['variety_name'] = get_select_crop.variety_name
        get_select_crop_ListArray.append(get_select_cropObj)
    return jsonify({'get_select_crops': get_select_crop_ListArray})


@app.route('/insert_farm_crop', methods=['GET', 'POST'])
@login_required
def insert_farm_crop():
    if request.method == 'POST':
        id = request.form['fid']
        print(id)
        farm = Farm.query.get_or_404(id)

        farm_surface = farm.surface
        if farm.user_id != current_user.id:
            flash('This is not your farm', 'danger')
            return redirect(url_for('farm_home'))
        else:
            sub_crop_id = request.form['subcrops']
            print(sub_crop_id)
            syste_sub_crop_category_details = SysSubCategory.query.filter_by(id=sub_crop_id).first()
            farm_crop_name = syste_sub_crop_category_details.variety_name
            farm_crop_image = syste_sub_crop_category_details.sub_crop_image
            production_type = request.form['productiontypes']
            planting_unit = request.form['plantingunit']
            surface = request.form['surface']
            crop = Crop(cropeName=farm_crop_name, cropImage=farm_crop_image, farm_id=id,
                        created_timestamp=datetime.now(), modified_timestamp=datetime.now(),
                        sys_sub_crop_id=sub_crop_id, production_type=production_type,
                        panting_unit=planting_unit, crop_surface_on_farm=surface
                        )
            db.session.add(crop)
            db.session.commit()
            flash('Crop Added!', 'success')
            return redirect(url_for('farm_crop', id=id))
    else:
        return redirect(url_for('farm_crop', id=id))


@app.route('/crp_sub_crop_Detail/<id>', methods=['GET', 'POST'])
@login_required
def crp_sub_crop_Detail(id):
    get_sys_sub_crop_details = SysSubCategory.query.filter_by(id=id)
    get_sys_sub_crop_detail_ListArray = []
    for sub_crop_detail in get_sys_sub_crop_details:
        syssubcropObj = {}
        syssubcropObj['id'] = sub_crop_detail.id
        syssubcropObj['variety_name'] = sub_crop_detail.variety_name
        syssubcropObj['line_designation'] = sub_crop_detail.line_designation
        syssubcropObj['pedgiree'] = sub_crop_detail.pedgiree
        syssubcropObj['origin'] = sub_crop_detail.origin
        syssubcropObj['method_of_propagation'] = sub_crop_detail.method_of_propagation
        syssubcropObj['sub_crop_image'] = sub_crop_detail.sub_crop_image
        syssubcropObj['created_timestamp'] = sub_crop_detail.created_timestamp.strftime('%Y-%m-%d')
        get_sys_sub_crop_detail_ListArray.append(syssubcropObj)
    return jsonify({'get_sys_sub_crop_details': get_sys_sub_crop_detail_ListArray})


@app.route('/conventiol_production_fertilizer_plan/<id>', methods=['GET', 'POST'])
@login_required
def show_fertilizer_plans(id):
    get_sys_crop_id = SysSubCategory.query.filter_by(id=id).first()
    sys_crop_id = get_sys_crop_id.syscrop_id
    cropseasons = CropSeason.query.filter_by(syscrop_id=sys_crop_id).all()
    TODAY_CHECK = datetime.now()
    if cropseasons is None:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id)
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
        get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})

    else:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id, production_type="1", season_id="1")
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
            get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})


@app.route('/conventiol_production_fertilizer_plan_yla/<id>', methods=['GET', 'POST'])
@login_required
def show_fertilizer_plans_yala(id):
    get_sys_crop_id = SysSubCategory.query.filter_by(id=id).first()
    sys_crop_id = get_sys_crop_id.syscrop_id
    cropseasons = CropSeason.query.filter_by(syscrop_id=sys_crop_id).all()
    TODAY_CHECK = datetime.now()
    if cropseasons is None:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id)
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
        get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})

    else:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id, production_type="1", season_id="2")
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
            get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})


@app.route('/organic_production_fertilizer_plan_mha/<id>', methods=['GET', 'POST'])
@login_required
def organic_production_fertilizer_plan_mha(id):
    get_sys_crop_id = SysSubCategory.query.filter_by(id=id).first()
    sys_crop_id = get_sys_crop_id.syscrop_id
    cropseasons = CropSeason.query.filter_by(syscrop_id=sys_crop_id).all()
    TODAY_CHECK = datetime.now()
    if cropseasons is None:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id)
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
        get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})

    else:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id, production_type="2", season_id="1")
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
            get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})


@app.route('/organic_production_fertilizer_plan_yala/<id>', methods=['GET', 'POST'])
@login_required
def organic_production_fertilizer_plan_yala(id):
    get_sys_crop_id = SysSubCategory.query.filter_by(id=id).first()
    sys_crop_id = get_sys_crop_id.syscrop_id
    cropseasons = CropSeason.query.filter_by(syscrop_id=sys_crop_id).all()
    TODAY_CHECK = datetime.now()
    if cropseasons is None:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id)
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
        get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})

    else:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id, production_type="2", season_id="2")
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
            get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})


#
@app.route('/intergrated_production_fertilizer_plan_mha/<id>', methods=['GET', 'POST'])
@login_required
def intergrated_production_fertilizer_plan_mha(id):
    get_sys_crop_id = SysSubCategory.query.filter_by(id=id).first()
    sys_crop_id = get_sys_crop_id.syscrop_id
    cropseasons = CropSeason.query.filter_by(syscrop_id=sys_crop_id).all()
    TODAY_CHECK = datetime.now()
    if cropseasons is None:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id)
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
        get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})

    else:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id, production_type="2", season_id="1")
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
            get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})


@app.route('/intergrated_production_fertilizer_plan_yala/<id>', methods=['GET', 'POST'])
@login_required
def intergrated_production_fertilizer_plan_yala(id):
    get_sys_crop_id = SysSubCategory.query.filter_by(id=id).first()
    sys_crop_id = get_sys_crop_id.syscrop_id
    cropseasons = CropSeason.query.filter_by(syscrop_id=sys_crop_id).all()
    TODAY_CHECK = datetime.now()
    if cropseasons is None:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id)
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
        get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})

    else:
        get_conventional_production_fertilizer_palns = SystemCommonFertilizerPlan.query.filter_by(
            syscrop_id=sys_crop_id, production_type="2", season_id="2")
        get_conventional_production_fertilizer_palnListArray = []
        for get_conventional_production_fertilizer_paln in get_conventional_production_fertilizer_palns:
            get_conventional_production_fertilizer_palnObj = {}
            get_conventional_production_fertilizer_palnObj['id'] = get_conventional_production_fertilizer_paln.id
            get_conventional_production_fertilizer_palnObj[
                'crop_age_range'] = get_conventional_production_fertilizer_paln.crop_age_range
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_name'] = get_conventional_production_fertilizer_paln.fertilizer_name
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_amount'] = get_conventional_production_fertilizer_paln.fertilizer_amount
            get_conventional_production_fertilizer_palnObj[
                'sys_crop_category_name'] = get_conventional_production_fertilizer_paln.sys_crop_category_name
            get_conventional_production_fertilizer_palnObj[
                'syscrop_id'] = get_conventional_production_fertilizer_paln.syscrop_id
            get_conventional_production_fertilizer_palnObj[
                'user_id'] = get_conventional_production_fertilizer_paln.user_id
            get_conventional_production_fertilizer_palnObj[
                'fertilizer_need_time_name'] = get_conventional_production_fertilizer_paln.fertilizer_need_time_name
            get_conventional_production_fertilizer_palnObj[
                'systemfertilizer_id'] = get_conventional_production_fertilizer_paln.systemfertilizer_id
            get_conventional_production_fertilizer_palnObj[
                'production_type'] = get_conventional_production_fertilizer_paln.production_type
            get_conventional_production_fertilizer_palnObj[
                'season_id'] = get_conventional_production_fertilizer_paln.season_id
            get_conventional_production_fertilizer_palnListArray.append(get_conventional_production_fertilizer_palnObj)
        return jsonify(
            {'get_conventional_production_fertilizer_palns': get_conventional_production_fertilizer_palnListArray})


@app.route('/get_system_fertilizer_result_crp/<id>', methods=['GET', 'POST'])
@login_required
def get_system_fertilizer_result_crp(id):
    get_sys_sub_crop_details = SysSubCategory.query.filter_by(id=id)
    get_sys_sub_crop_detail_ListArray = []
    for sub_crop_detail in get_sys_sub_crop_details:
        syssubcropObj = {}
        syssubcropObj['id'] = sub_crop_detail.id
        syssubcropObj['variety_name'] = sub_crop_detail.variety_name
        syssubcropObj['line_designation'] = sub_crop_detail.line_designation
        syssubcropObj['pedgiree'] = sub_crop_detail.pedgiree
        syssubcropObj['origin'] = sub_crop_detail.origin
        syssubcropObj['method_of_propagation'] = sub_crop_detail.method_of_propagation
        syssubcropObj['sub_crop_image'] = sub_crop_detail.sub_crop_image
        syssubcropObj['created_timestamp'] = sub_crop_detail.created_timestamp.strftime('%Y-%m-%d')
        get_sys_sub_crop_detail_ListArray.append(syssubcropObj)
    return jsonify({'get_sys_sub_crop_details': get_sys_sub_crop_detail_ListArray})


@app.route('/get_system_fertilizer_to_sumit_result/', methods=['GET', 'POST'])
@login_required
def get_system_fertilizers_to_sumit_result():
    systemcommonfertilizerplans = SystemFertilizer.query.all()
    systemcommonfertilizerplan_ListArray = []
    for systemcommonfertilizerplan in systemcommonfertilizerplans:
        systemcommonfertilizerplanObj = {}
        systemcommonfertilizerplanObj['id'] = systemcommonfertilizerplan.id
        systemcommonfertilizerplanObj['fertilizer_name'] = systemcommonfertilizerplan.fertilizer_name

        systemcommonfertilizerplan_ListArray.append(systemcommonfertilizerplanObj)
    return jsonify({'systemcommonfertilizerplans': systemcommonfertilizerplan_ListArray})


@app.route('/submit_furtilizer_result', methods=['GET', 'POST'])
@login_required
def submit_furtilizer_result():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        farm = Farm.query.get_or_404(farm_id)
        if farm.user_id != current_user.id:
            flash('This is not your farm', 'danger')
            return redirect(url_for('farm_home'))
        else:
            sub_crop_id = request.form['frtilizerresultvarity']
            syssubcategory = SysSubCategory.query.filter_by(id=sub_crop_id).first()
            syscrop_id = syssubcategory.syscrop_id
            varityname = syssubcategory.variety_name
            syscrop = SysCrop.query.filter_by(id=syscrop_id).first()
            system_crop_names = syscrop.system_crop_name
            fertilizer_id = request.form['crop_all_fertilzers']
            systemfertilizer = SystemFertilizer.query.filter_by(id=fertilizer_id).first()
            fertilizer_name = systemfertilizer.fertilizer_name
            main_fertilizer_type = systemfertilizer.fertilizer_main_type_name
            sub_fertilizer_type = systemfertilizer.fertilizer_sub_type_name
            crp_fertilizer_amount = int(request.form['fertilzeramount'])
            fertilizer_matter_name = systemfertilizer.fertilizer_matter
            system_crop_name = system_crop_names
            variety_name = varityname
            fertilzersurface = int(request.form['fertilzersurface'])
            fertilizer_result = request.form['fertilizer_result']
            subcrops_id = request.form['subcrop_id']
            fertilizermatter_id = systemfertilizer.fertilizermatter_id
            systemsubfertilizertyeps_id = systemfertilizer.systemsubfertilizertyeps_id
            systemfertilizertyeps_id = systemfertilizer.systemfertilizertyeps_id
            systemfertilizer_id = systemfertilizer.id
            user_id = current_user.id
            fertilizer_date = request.form['fertilizerdate']
            farm_id = farm_id
            farmfertilizerresults = FarmFertilizerResults(fertilizer_name=fertilizer_name,
                                                          main_fertilizer_type=main_fertilizer_type,
                                                          sub_fertilizer_type=sub_fertilizer_type,
                                                          farm_used_fertilizer_amount=crp_fertilizer_amount,
                                                          fertilizer_matter_name=fertilizer_matter_name,
                                                          system_crop_name=system_crop_name, variety_name=variety_name,
                                                          fertilizer_surface=fertilzersurface,
                                                          fertilizer_result=fertilizer_result,
                                                          syssubcategory_id=sub_crop_id, syscrop_id=syscrop_id,
                                                          fertilizermatter_id=fertilizermatter_id,
                                                          systemsubfertilizertyeps_id=systemsubfertilizertyeps_id,
                                                          systemfertilizertyeps_id=systemfertilizertyeps_id,
                                                          systemfertilizer_id=systemfertilizer_id, user_id=user_id,
                                                          fertilizer_date=fertilizer_date, farm_id=farm_id)
            db.session.add(farmfertilizerresults)
            db.session.commit()
            flash('Fertilizer Result Added!', 'success')
            return redirect(url_for('farm_crop', id=farm_id))


@app.route('/get_system_fertilizer_result_in_farm/<id>', methods=['GET', 'POST'])
@login_required
def get_system_fertilizer_result_in_farm(id):
    farmfertilizerresults = FarmFertilizerResults.query.filter_by(farm_id=id).all()
    farmfertilizerresults_ListArray = []
    for farmfertilizerresult in farmfertilizerresults:
        farmfertilizerresultObj = {}
        farmfertilizerresultObj['id'] = farmfertilizerresult.id
        farmfertilizerresultObj['fertilizer_name'] = farmfertilizerresult.fertilizer_name
        farmfertilizerresultObj['main_fertilizer_type'] = farmfertilizerresult.main_fertilizer_type
        farmfertilizerresultObj['sub_fertilizer_type'] = farmfertilizerresult.sub_fertilizer_type
        farmfertilizerresultObj['fertilizer_matter_name'] = farmfertilizerresult.fertilizer_matter_name
        farmfertilizerresultObj['system_crop_name'] = farmfertilizerresult.system_crop_name
        farmfertilizerresultObj['variety_name'] = farmfertilizerresult.variety_name
        farmfertilizerresultObj['fertilizer_surface'] = farmfertilizerresult.fertilizer_surface
        farmfertilizerresultObj['farm_used_fertilizer_amount'] = farmfertilizerresult.farm_used_fertilizer_amount
        farmfertilizerresultObj['fertilizer_result'] = farmfertilizerresult.fertilizer_result
        farmfertilizerresultObj['fertilizer_date'] = farmfertilizerresult.fertilizer_date.strftime('%Y-%m-%d')
        farmfertilizerresults_ListArray.append(farmfertilizerresultObj)
    return jsonify({'farmfertilizerresults': farmfertilizerresults_ListArray})


@app.route('/get_system_crp_diseases_details/<id>', methods=['GET', 'POST'])
@login_required
def get_system_crp_diseases_details(id):
    get_system_crp_diseases_details = ReactionToDisease.query.filter_by(syssubcategory_id=id).all()
    get_system_crp_diseases_details_ListArray = []
    for get_system_crp_diseases_detail in get_system_crp_diseases_details:
        get_system_crp_diseases_detailObj = {}
        get_system_crp_diseases_detailObj['id'] = get_system_crp_diseases_detail.id
        get_system_crp_diseases_detailObj['diseasese_name'] = get_system_crp_diseases_detail.diseasese_name
        get_system_crp_diseases_detailObj['syssubcategory_name'] = get_system_crp_diseases_detail.syssubcategory_name
        get_system_crp_diseases_detailObj['resistant'] = get_system_crp_diseases_detail.resistant
        get_system_crp_diseases_detailObj['moderately_resistant'] = get_system_crp_diseases_detail.moderately_resistant
        get_system_crp_diseases_detailObj['susceptible'] = get_system_crp_diseases_detail.susceptible
        get_system_crp_diseases_detailObj[
            'moderately_susceptible'] = get_system_crp_diseases_detail.moderately_susceptible
        get_system_crp_diseases_detailObj[
            'system_pest_and_diseases_id'] = get_system_crp_diseases_detail.system_pest_and_diseases_id
        get_system_crp_diseases_details_ListArray.append(get_system_crp_diseases_detailObj)
    return jsonify({'get_system_crp_diseases_details': get_system_crp_diseases_details_ListArray})


@app.route('/get_system_crp_pest_details/<id>', methods=['GET', 'POST'])
@login_required
def get_system_crp_pest_details(id):
    get_system_crp_pest_details = ReactionToInsectPest.query.filter_by(syssubcategory_id=id).all()
    get_system_crp_pest_details_ListArray = []
    for get_system_crp_pest_detail in get_system_crp_pest_details:
        get_system_crp_pest_detailObj = {}
        get_system_crp_pest_detailObj['id'] = get_system_crp_pest_detail.id
        get_system_crp_pest_detailObj['diseasese_name'] = get_system_crp_pest_detail.diseasese_name
        get_system_crp_pest_detailObj['syssubcategory_name'] = get_system_crp_pest_detail.syssubcategory_name
        get_system_crp_pest_detailObj['resistant'] = get_system_crp_pest_detail.resistant
        get_system_crp_pest_detailObj['moderately_resistant'] = get_system_crp_pest_detail.moderately_resistant
        get_system_crp_pest_detailObj['susceptible'] = get_system_crp_pest_detail.susceptible
        get_system_crp_pest_detailObj[
            'moderately_susceptible'] = get_system_crp_pest_detail.moderately_susceptible
        get_system_crp_pest_detailObj[
            'system_pest_and_diseases_id'] = get_system_crp_pest_detail.system_pest_and_diseases_id
        get_system_crp_pest_details_ListArray.append(get_system_crp_pest_detailObj)
    return jsonify({'get_system_crp_pest_details': get_system_crp_pest_details_ListArray})


@app.route('/system_pest_and_diseases/<id>', methods=['GET', 'POST'])
@login_required
def system_pest_and_diseases(id):
    system_pest_and_diseases = System_Pest_and_Diseases.query.filter_by(id=id).all()
    system_pest_and_diseases_ListArray = []
    for system_pest_and_disease in system_pest_and_diseases:
        system_pest_and_diseaseObj = {}
        system_pest_and_diseaseObj['id'] = system_pest_and_disease.id
        system_pest_and_diseaseObj['threat_name'] = system_pest_and_disease.threat_name
        system_pest_and_diseaseObj['threat_sci_name'] = system_pest_and_disease.threat_sci_name
        system_pest_and_diseaseObj['threat_type'] = system_pest_and_disease.threat_type
        system_pest_and_diseaseObj['disease_name'] = system_pest_and_disease.disease_name
        system_pest_and_diseaseObj['disease_symptoms'] = system_pest_and_disease.disease_symptoms
        system_pest_and_diseaseObj['disease_causes'] = system_pest_and_disease.disease_causes
        system_pest_and_diseaseObj['disease_discreption'] = system_pest_and_disease.disease_discreption
        system_pest_and_diseaseObj['threat_image'] = system_pest_and_disease.threat_image
        system_pest_and_diseaseObj['created_timestamp'] = system_pest_and_disease.created_timestamp.strftime('%Y-%m-%d')
        system_pest_and_diseaseObj['modified_timestamp'] = system_pest_and_disease.modified_timestamp
        system_pest_and_diseases_ListArray.append(system_pest_and_diseaseObj)
    return jsonify({'system_pest_and_diseases': system_pest_and_diseases_ListArray})


@app.route('/system_pest_and_diseases_solutions/<id>', methods=['GET', 'POST'])
@login_required
def system_pest_and_diseases_solutions(id):
    system_pest_and_diseases_solutions = System_Pest_Disease_Soulutions.query.filter_by(
        system_pest_and_diseases_id=id).all()
    system_pest_and_diseases_solutions_ListArray = []
    for system_pest_and_diseases_solution in system_pest_and_diseases_solutions:
        system_pest_and_diseases_solutionObj = {}
        system_pest_and_diseases_solutionObj['id'] = system_pest_and_diseases_solution.id
        system_pest_and_diseases_solutionObj[
            'pest_or_diseas_name'] = system_pest_and_diseases_solution.pest_or_diseas_name
        system_pest_and_diseases_solutionObj['threatment_type'] = system_pest_and_diseases_solution.threatment_type
        system_pest_and_diseases_solutionObj['threatment_method'] = system_pest_and_diseases_solution.threatment_method
        system_pest_and_diseases_solutionObj[
            'threatment_chemi_amount'] = system_pest_and_diseases_solution.threatment_chemi_amount
        system_pest_and_diseases_solutionObj[
            'threatment_method_descreption'] = system_pest_and_diseases_solution.threatment_method_descreption
        system_pest_and_diseases_solutionObj['prevention_level'] = system_pest_and_diseases_solution.prevention_level
        system_pest_and_diseases_solutionObj['soulution_image'] = system_pest_and_diseases_solution.soulution_image
        system_pest_and_diseases_solutionObj['created_timestamp'] = system_pest_and_diseases_solution.created_timestamp
        system_pest_and_diseases_solutions_ListArray.append(system_pest_and_diseases_solutionObj)
    return jsonify({'system_pest_and_diseases_solution': system_pest_and_diseases_solutions_ListArray})


@app.route('/farmer_weather', methods=['GET', 'POST'])
@login_required
def farmer_weather():
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('farmer_weather.html', title='Weather in Sri Lanka', year=datetime.now().year,
                           image_file=image_file)


@app.route('/paddy_leaf_color_chart', methods=['GET', 'POST'])
@login_required
def paddy_leaf_color_chart():
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('paddy_leaf_color_chart.html', title='Leaf color chart', year=datetime.now().year,
                           image_file=image_file)


@app.route('/submit_pest_d_info', methods=['GET', 'POST'])
@login_required
def submit_pest_d_info():
    if request.method == 'POST':
        farm_id = request.form['farm_ids']
        farm = Farm.query.get_or_404(farm_id)
        if farm.user_id != current_user.id:
            flash('This is not your farm', 'danger')
            return redirect(url_for('farm_home'))
        else:
            farm_id = farm_id
            farm = Farm.query.filter_by(id=farm_id).first()
            farmnme = farm.farmname
            farmlat = farm.latitude
            farmlong = farm.longitude
            sub_crp_id = request.form['pest_and_diseas_varity']
            syssubcategory = SysSubCategory.query.filter_by(id=sub_crp_id).first()
            syscrop_id = syssubcategory.syscrop_id
            varityname = syssubcategory.variety_name
            syscrop = SysCrop.query.filter_by(id=syscrop_id).first()
            syscrp_id = syscrop.id
            system_crop_names = syscrop.system_crop_name
            system_pd_id = request.form['pestdiseasname']
            system_pest_and_diseas = System_Pest_and_Diseases.query.filter_by(id=system_pd_id).first()
            pest_or_diseas_name = system_pest_and_diseas.threat_name
            threatment_type = request.form['threatmenttype']
            pstdsoultions = System_Pest_Disease_Soulutions.query.filter_by(threatment_type=threatment_type).first()
            if pstdsoultions is None:
                flash('Database has not any record this solution type pest or disease!', 'warning')
                return redirect(url_for('farm_crop', id=farm_id))
            else:
                system_pest_disease_soulutions_id = pstdsoultions.id
                threatment_method = request.form['threatmentname']
                threatment_chemi_amount = request.form['threatmentchemicalamount']
                threatment_method_descreption = request.form['descreption']
                optinal_details = request.form['optinal_details']
                prevention_level = request.form['prevention_level']
                farm_pest_details = Farm_pest_details(pest_or_diseas_name=pest_or_diseas_name,
                                                      threatment_type=threatment_type,
                                                      threatment_method=threatment_method,
                                                      threatment_method_descreption=threatment_method_descreption,
                                                      threatment_chemi_amount=threatment_chemi_amount,
                                                      optinal_details=optinal_details,
                                                      prevention_level=prevention_level,
                                                      soulution_image="no image yet",
                                                      system_crop_name=system_crop_names,
                                                      variety_name=varityname, farm_name=farmnme, farm_id=farm_id,
                                                      syscrop_id=syscrp_id,
                                                      system_pest_disease_soulutions_id=system_pest_disease_soulutions_id,
                                                      system_pest_and_diseases_id=system_pd_id,
                                                      syssubcategory_id=sub_crp_id, user_id=current_user.id,
                                                      created_timestamp=datetime.now(),
                                                      modified_timestamp=datetime.now(),
                                                      latitude=farmlat, longitude=farmlong)
                db.session.add(farm_pest_details)
                db.session.commit()
                flash('Data insert Sucessfully', 'success')
                return redirect(url_for('farm_crop', id=farm_id))


@app.route('/get_farm_pest_details/<id>', methods=['GET', 'POST'])
@login_required
def farm_pest_details(id):
    farm_pest_details = Farm_pest_details.query.filter_by(farm_id=id).all()
    get_farm_pest_details_ListArray = []
    for farm_pest_detail in farm_pest_details:
        get_farm_pest_detailsObj = {}
        get_farm_pest_detailsObj['id'] = farm_pest_detail.id
        get_farm_pest_detailsObj['pest_or_diseas_name'] = farm_pest_detail.pest_or_diseas_name
        get_farm_pest_detailsObj['threatment_type'] = farm_pest_detail.threatment_type
        get_farm_pest_detailsObj['threatment_method'] = farm_pest_detail.threatment_method
        get_farm_pest_detailsObj['threatment_method_descreption'] = farm_pest_detail.threatment_method_descreption
        get_farm_pest_detailsObj['threatment_chemi_amount'] = farm_pest_detail.threatment_chemi_amount
        get_farm_pest_detailsObj['optinal_details'] = farm_pest_detail.optinal_details
        get_farm_pest_detailsObj['pest_or_diseas_name'] = farm_pest_detail.pest_or_diseas_name
        get_farm_pest_detailsObj['prevention_level'] = farm_pest_detail.prevention_level
        get_farm_pest_detailsObj['variety_name'] = farm_pest_detail.variety_name
        get_farm_pest_details_ListArray.append(get_farm_pest_detailsObj)
    return jsonify({'farm_pest_details': get_farm_pest_details_ListArray})


@app.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    farm = Farm.query.all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)

    return render_template(
        'analytics.html',
        title='Analaytics',
        year=datetime.now().year,
        farm=farm,
        image_file=image_file
    )


@app.route('/get_all_farms', methods=['GET', 'POST'])
@login_required
def get_all_farms():
    farms = Farm.query.all()
    get_farms_ListArray = []
    for farm in farms:
        get_farm_detailsObj = {}
        get_farm_detailsObj['id'] = farm.id
        get_farm_detailsObj['farmname'] = farm.farmname
        get_farm_detailsObj['latitude'] = str(farm.latitude)
        get_farm_detailsObj['longitude'] = str(farm.longitude)
        get_farm_detailsObj['address'] = farm.address
        get_farm_detailsObj['phone'] = farm.phone
        get_farms_ListArray.append(get_farm_detailsObj)
    return jsonify({'get_all_farms': get_farms_ListArray})


@app.route('/infectedpestmap', methods=['GET', 'POST'])
@login_required
def infectedpestmap():
    farm = Farm.query.all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)

    return render_template(
        'infectedpestmap.html',
        title='Analaytics',
        year=datetime.now().year,
        farm=farm,
        image_file=image_file
    )


@app.route('/get_infected_farms', methods=['GET', 'POST'])
@login_required
def get_infected_farms():
    farm_pest_details = Farm_pest_details.query.all()
    farm_pest_details_ListArray = []
    for farm_pest_detail in farm_pest_details:
        farm_pest_detailsObj = {}
        farm_pest_detailsObj['id'] = farm_pest_detail.id
        farm_pest_detailsObj['pest_or_diseas_name'] = farm_pest_detail.pest_or_diseas_name
        farm_pest_detailsObj['latitude'] = str(farm_pest_detail.latitude)
        farm_pest_detailsObj['longitude'] = str(farm_pest_detail.longitude)
        farm_pest_detailsObj['farm_name'] = farm_pest_detail.farm_name
        farm_pest_detailsObj['system_crop_name'] = farm_pest_detail.system_crop_name
        farm_pest_detailsObj['variety_name'] = farm_pest_detail.variety_name
        farm_pest_details_ListArray.append(farm_pest_detailsObj)
    return jsonify({'get_infected_farms': farm_pest_details_ListArray})


@app.route('/manage_all_farmers', methods=['GET', 'POST'])
@login_required
def manage_all_farmers():
    curnt_user_devison_office_id = current_user.devisionoffice_id
    users = User.query.filter_by(devisionoffice_id=curnt_user_devison_office_id).all()
    districts = District.query.all()
    areas = Area.query.all()
    devisionoffices = Devisionoffice.query.all()
    form = AddUserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf-8')
        user = User(fristname=form.fristname.data, lastname=form.lastname.data, email=form.email.data,
                    password=hashed_password, phone=form.phone.data, address=form.address.data,
                    profile='defaultprofile.jpg', usertype=form.usertype.data, active=1,
                    devisionoffice_id=request.form['devisionoffice'], created_timestamp=datetime.now(),
                    modified_timestamp=datetime.now(), confirmed=False)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.email.data}!', 'success')
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template(
        'manage_all_farmers.html',
        title='Manage All Farmers',
        year=datetime.now().year,
        image_file=image_file,
        users=users,
        districts=districts,
        areas=areas,
        devisionoffices=devisionoffices,
        form=form
    )


@app.route('/updte_farmers/<id>', methods=['GET', 'POST'])
@login_required
def updte_farmers(id):
    user_details = User.query.filter_by(id=id).all()
    get_user_details_ListArray = []
    for user_detail in user_details:
        get_user_detailsObJ = {}
        get_user_detailsObJ['id'] = user_detail.id
        get_user_detailsObJ['fristname'] = user_detail.fristname
        get_user_detailsObJ['lastname'] = user_detail.lastname
        get_user_detailsObJ['email'] = user_detail.email
        get_user_detailsObJ['phone'] = user_detail.phone
        get_user_detailsObJ['address'] = user_detail.address
        get_user_detailsObJ['profile'] = user_detail.profile
        get_user_detailsObJ['usertype'] = user_detail.usertype
        get_user_detailsObJ['active'] = user_detail.active
        get_user_detailsObJ['devisionoffice_id'] = user_detail.devisionoffice_id
        get_user_details_ListArray.append(get_user_detailsObJ)
    return jsonify({'get_user_details': get_user_details_ListArray})


@app.route('/farmer_update', methods=['GET', 'POST'])
@login_required
def farmer_update():
    if request.method == 'POST':
        userid = request.form['userid']
        update_users = User.query.filter_by(id=userid).first()
        update_users.fristname = request.form['fristname1']
        update_users.lastname = request.form['lastname1']
        update_users.email = request.form['email']
        update_users.phone = request.form['phone1']
        update_users.address = request.form['address1']
        update_users.profile = update_users.profile
        update_users.usertype = request.form['type1']
        update_users.active = int(request.form['status'])
        update_users.devisionoffice_id = request.form['devisionoffice']
        update_users.modified_timestamp = datetime.now()
        db.session.commit()
        flash('User Details has been updated!', 'success')
        return redirect(url_for('manage_all_farmers'))


ROOMS = ["crop", "society", "pest&desis", "fertilizer"]


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    # farm = Farm.query.all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)

    return render_template(
        'chat.html',
        title='Communication',
        year=datetime.now().year,
        image_file=image_file,
        username=current_user.fristname,
        rooms=ROOMS
    )


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""

    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    # Set timestamp
    time_stamp = time.strftime('%b-%d %I:%M%p', time.localtime())
    send({"username": username, "msg": msg, "time_stamp": time_stamp}, room=room)


@socketio.on('join')
def on_join(data):
    """User joins a room"""

    username = data["username"]
    room = data["room"]
    join_room(room)

    # Broadcast that new user has joined
    send({"msg": username + " has joined the " + room + " room."}, room=room)


@socketio.on('leave')
def on_leave(data):
    """User leaves a room"""

    username = data['username']
    room = data['room']
    leave_room(room)
    send({"msg": username + " has left the room"}, room=room)


@app.route('/manage_farm', methods=['GET', 'POST'])
@login_required
def manage_farm():
    farmdata = Farm.query.filter_by(devisionoffice_id=current_user.devisionoffice_id).all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template(
        'manage_all_farm.html',
        title='Communication',
        year=datetime.now().year,
        image_file=image_file,
        farmdata=farmdata

    )


@app.route('/get_select_farms_detail/<id>', methods=['GET', 'POST'])
@login_required
def get_select_farms_detail(id):
    farms = Farm.query.filter_by(id=id).all()
    get_select_farms_ListArray = []
    for farm in farms:
        get_farm_detailsObj = {}
        get_farm_detailsObj['id'] = farm.id
        get_farm_detailsObj['farmname'] = farm.farmname
        get_farm_detailsObj['latitude'] = str(farm.latitude)
        get_farm_detailsObj['longitude'] = str(farm.longitude)
        get_farm_detailsObj['address'] = farm.address
        get_farm_detailsObj['phone'] = farm.phone
        get_farm_detailsObj['email'] = farm.email
        get_farm_detailsObj['surface'] = farm.surface
        get_select_farms_ListArray.append(get_farm_detailsObj)
    return jsonify({'get_all_farms': get_select_farms_ListArray})


@app.route('/farm_growing_crops/<id>', methods=['GET', 'POST'])
@login_required
def farm_growing_crops(id):
    crops = Crop.query.filter_by(farm_id=id).all()
    get_crop_ListArray = []
    for crop in crops:
        get_crop_detailsObj = {}
        get_crop_detailsObj['id'] = crop.id
        get_crop_detailsObj['cropImage'] = crop.cropImage
        get_crop_detailsObj['cropeName'] = crop.cropeName
        get_crop_detailsObj['production_type'] = crop.production_type
        get_crop_detailsObj['panting_unit'] = crop.panting_unit
        get_crop_detailsObj['crop_surface_on_farm'] = crop.crop_surface_on_farm
        get_crop_ListArray.append(get_crop_detailsObj)
    return jsonify({'get_all_farms': get_crop_ListArray})


@app.route("/manage_farm_home/<int:id>/manage_farms", methods=['GET', 'POST'])
@login_required
def manage_farms(id):
    farm = Farm.query.get_or_404(id)
    if farm.devisionoffice_id != current_user.devisionoffice_id:
        flash('This is not your area farm', 'danger')
        return redirect(url_for('manage_farm'))
    farmdata = Farm.query.filter_by(id=id).all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('manage_farm_home.html', title='Farm Home', year=datetime.now().year, image_file=image_file,
                           farmdata=farmdata)


@app.route("/manage_farm_home/select_farm/<int:id>/farm_crop", methods=['GET', 'POST'])
@login_required
def farm_manage_farm_crop(id):
    form = FarmCropForm()
    farm = Farm.query.get_or_404(id)
    if farm.devisionoffice_id != current_user.devisionoffice_id:
        flash('This is not your area farm', 'danger')
        return redirect(url_for('manage_farm'))
    farmdata = Farm.query.filter_by(id=id).all()
    system_inbuild_crops = SysCrop.query.all()
    myfarmCrop = Crop.query.filter_by(farm_id=id).all()
    system_pest_and_diseases = System_Pest_and_Diseases.query.all()
    current_season = get_season(date.today())
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('manage_farm_crop.html', title='Farm Crop', year=datetime.now().year, image_file=image_file,
                           farmdata=farmdata, system_inbuild_crops=system_inbuild_crops, myfarmCrop=myfarmCrop,
                           current_season=current_season, system_pest_and_diseases=system_pest_and_diseases)


@app.route('/insert_farm_crop_by_officer', methods=['GET', 'POST'])
@login_required
def insert_farm_crop_by_officer():
    if request.method == 'POST':
        id = request.form['fid']
        print(id)
        farm = Farm.query.get_or_404(id)

        farm_surface = farm.surface
        if farm.devisionoffice_id != current_user.devisionoffice_id:
            flash('This is not your area farm', 'danger')
            return redirect(url_for('manage_farms'))
        else:
            sub_crop_id = request.form['subcrops']
            print(sub_crop_id)
            syste_sub_crop_category_details = SysSubCategory.query.filter_by(id=sub_crop_id).first()
            farm_crop_name = syste_sub_crop_category_details.variety_name
            farm_crop_image = syste_sub_crop_category_details.sub_crop_image
            production_type = request.form['productiontypes']
            planting_unit = request.form['plantingunit']
            surface = request.form['surface']
            crop = Crop(cropeName=farm_crop_name, cropImage=farm_crop_image, farm_id=id,
                        created_timestamp=datetime.now(), modified_timestamp=datetime.now(),
                        sys_sub_crop_id=sub_crop_id, production_type=production_type,
                        panting_unit=planting_unit, crop_surface_on_farm=surface
                        )
            db.session.add(crop)
            db.session.commit()
            flash('Crop Added!', 'success')
            return redirect(url_for('farm_manage_farm_crop', id=id))
    else:
        return redirect(url_for('farm_manage_farm_crop', id=id))


@app.route('/submit_furtilizer_result_by_ado', methods=['GET', 'POST'])
@login_required
def submit_furtilizer_result_by_ado():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        farm = Farm.query.get_or_404(farm_id)
        if farm.devisionoffice_id != current_user.devisionoffice_id:
            flash('This is not your area farm', 'danger')
            return redirect(url_for('manage_farm'))
        else:
            sub_crop_id = request.form['frtilizerresultvarity']
            syssubcategory = SysSubCategory.query.filter_by(id=sub_crop_id).first()
            syscrop_id = syssubcategory.syscrop_id
            varityname = syssubcategory.variety_name
            syscrop = SysCrop.query.filter_by(id=syscrop_id).first()
            system_crop_names = syscrop.system_crop_name
            fertilizer_id = request.form['crop_all_fertilzers']
            systemfertilizer = SystemFertilizer.query.filter_by(id=fertilizer_id).first()
            fertilizer_name = systemfertilizer.fertilizer_name
            main_fertilizer_type = systemfertilizer.fertilizer_main_type_name
            sub_fertilizer_type = systemfertilizer.fertilizer_sub_type_name
            crp_fertilizer_amount = int(request.form['fertilzeramount'])
            fertilizer_matter_name = systemfertilizer.fertilizer_matter
            system_crop_name = system_crop_names
            variety_name = varityname
            fertilzersurface = int(request.form['fertilzersurface'])
            fertilizer_result = request.form['fertilizer_result']
            subcrops_id = request.form['subcrop_id']
            fertilizermatter_id = systemfertilizer.fertilizermatter_id
            systemsubfertilizertyeps_id = systemfertilizer.systemsubfertilizertyeps_id
            systemfertilizertyeps_id = systemfertilizer.systemfertilizertyeps_id
            systemfertilizer_id = systemfertilizer.id
            user_id = current_user.id
            fertilizer_date = request.form['fertilizerdate']
            farm_id = farm_id
            farmfertilizerresults = FarmFertilizerResults(fertilizer_name=fertilizer_name,
                                                          main_fertilizer_type=main_fertilizer_type,
                                                          sub_fertilizer_type=sub_fertilizer_type,
                                                          farm_used_fertilizer_amount=crp_fertilizer_amount,
                                                          fertilizer_matter_name=fertilizer_matter_name,
                                                          system_crop_name=system_crop_name, variety_name=variety_name,
                                                          fertilizer_surface=fertilzersurface,
                                                          fertilizer_result=fertilizer_result,
                                                          syssubcategory_id=sub_crop_id, syscrop_id=syscrop_id,
                                                          fertilizermatter_id=fertilizermatter_id,
                                                          systemsubfertilizertyeps_id=systemsubfertilizertyeps_id,
                                                          systemfertilizertyeps_id=systemfertilizertyeps_id,
                                                          systemfertilizer_id=systemfertilizer_id, user_id=user_id,
                                                          fertilizer_date=fertilizer_date, farm_id=farm_id)
            db.session.add(farmfertilizerresults)
            db.session.commit()
            flash('Fertilizer Result Added!', 'success')
            return redirect(url_for('farm_manage_farm_crop', id=farm_id))


@app.route('/submit_pest_d_info_by_ado', methods=['GET', 'POST'])
@login_required
def submit_pest_d_info_by_Ado():
    if request.method == 'POST':
        farm_id = request.form['farm_ids']
        farm = Farm.query.get_or_404(farm_id)
        if farm.devisionoffice_id != current_user.devisionoffice_id:
            flash('This is not your area farm', 'danger')
            return redirect(url_for('manage_farm'))
        else:
            farm_id = farm_id
            farm = Farm.query.filter_by(id=farm_id).first()
            farmnme = farm.farmname
            farmlat = farm.latitude
            farmlong = farm.longitude
            sub_crp_id = request.form['pest_and_diseas_varity']
            syssubcategory = SysSubCategory.query.filter_by(id=sub_crp_id).first()
            syscrop_id = syssubcategory.syscrop_id
            varityname = syssubcategory.variety_name
            syscrop = SysCrop.query.filter_by(id=syscrop_id).first()
            syscrp_id = syscrop.id
            system_crop_names = syscrop.system_crop_name
            system_pd_id = request.form['pestdiseasname']
            system_pest_and_diseas = System_Pest_and_Diseases.query.filter_by(id=system_pd_id).first()
            pest_or_diseas_name = system_pest_and_diseas.threat_name
            threatment_type = request.form['threatmenttype']
            pstdsoultions = System_Pest_Disease_Soulutions.query.filter_by(threatment_type=threatment_type).first()
            if pstdsoultions is None:
                flash('This Solution not in the Database form not submmited', 'danger')
                return redirect(url_for('farm_manage_farm_crop_arpa', id=farm_id))
            else:
                system_pest_disease_soulutions_id = pstdsoultions.id
                threatment_method = request.form['threatmentname']
                threatment_chemi_amount = request.form['threatmentchemicalamount']
                threatment_method_descreption = request.form['descreption']
                optinal_details = request.form['optinal_details']
                prevention_level = request.form['prevention_level']
                farm_pest_details = Farm_pest_details(pest_or_diseas_name=pest_or_diseas_name,
                                                      threatment_type=threatment_type,
                                                      threatment_method=threatment_method,
                                                      threatment_method_descreption=threatment_method_descreption,
                                                      threatment_chemi_amount=threatment_chemi_amount,
                                                      optinal_details=optinal_details,
                                                      prevention_level=prevention_level,
                                                      soulution_image="no image yet",
                                                      system_crop_name=system_crop_names,
                                                      variety_name=varityname, farm_name=farmnme, farm_id=farm_id,
                                                      syscrop_id=syscrp_id,
                                                      system_pest_disease_soulutions_id=system_pest_disease_soulutions_id,
                                                      system_pest_and_diseases_id=system_pd_id,
                                                      syssubcategory_id=sub_crp_id, user_id=current_user.id,
                                                      created_timestamp=datetime.now(),
                                                      modified_timestamp=datetime.now(),
                                                      latitude=farmlat, longitude=farmlong)
                db.session.add(farm_pest_details)
                db.session.commit()
                flash('Data insert Sucessfully', 'success')
                return redirect(url_for('farm_manage_farm_crop', id=farm_id))


@app.route('/addnewfarm_by_officer', methods=['GET', 'POST'])
@login_required
def addnewfarm_by_officer():
    form = InsertNewFarmForm()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    district = District.query.all()
    area = Area.query.filter_by(district_id=1).all()
    devisionoffices = Devisionoffice.query.filter_by(area_id=2).all()
    users = User.query.filter_by(devisionoffice_id=current_user.devisionoffice_id).all()
    if form.validate_on_submit():

        farm = Farm(farmname=form.farmname.data, latitude=form.latitude.data, longitude=form.longitude.data,
                    phone=form.phone.data, address=form.address.data, email=form.email.data,
                    user_id=request.form['user'],
                    created_timestamp=datetime.now(), modified_timestamp=datetime.now(), surface=form.surface.data,
                    devisionoffice_id=request.form['devisionoffice'])
        db.session.add(farm)
        db.session.commit()
        flash('Your farm details insert sucessfully', 'success')
        return redirect(url_for('addnewfarm_by_officer'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    return render_template('add_new_farm_by_admin.html', title='Add new Farm', year=datetime.now().year,
                           image_file=image_file,
                           form=form, district=district, area=area, devisionoffices=devisionoffices, users=users)


def save_crop_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/crop_images', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/manage_sys_crops', methods=['GET', 'POST'])
@login_required
def manage_sys_crops():
    form = SysCropForm()

    syscrops = SysCrop.query.all()
    if form.validate_on_submit():
        if form.system_crop_image.data:
            picture_file = save_crop_picture(form.system_crop_image.data)

            syscrop = SysCrop(system_crop_name=form.system_crop_name.data,
                              system_crop_sci_name=form.system_crop_sci_name.data,
                              system_crop_catgoery=form.system_crop_catgoery.data,
                              system_crop_growing_time=form.system_crop_growing_time.data,
                              system_crop_image=picture_file,
                              user_id=current_user.id, created_timestamp=datetime.now(),
                              modified_timestamp=datetime.now())
            db.session.add(syscrop)
            db.session.commit()

            flash('Crop Submit sucessfully', 'success')
            return redirect(url_for('manage_sys_crops'))

    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('manage_sys_crops.html', title='Add Crop', year=datetime.now().year,
                           image_file=image_file,
                           form=form, syscrops=syscrops)


@app.route('/add_sys_sub_crops/<id>', methods=['GET', 'POST'])
@login_required
def add_sys_sub_crops(id):
    system_crops = SysCrop.query.filter_by(id=id).all()
    get_syscrop_ListArray = []
    for syscrops in system_crops:
        get_syscrop_detailsObj = {}
        get_syscrop_detailsObj['id'] = syscrops.id
        get_syscrop_detailsObj['system_crop_name'] = syscrops.system_crop_name
        get_syscrop_detailsObj['system_crop_sci_name'] = syscrops.system_crop_sci_name
        get_syscrop_detailsObj['system_crop_catgoery'] = syscrops.system_crop_catgoery
        get_syscrop_detailsObj['system_crop_growing_time'] = syscrops.system_crop_growing_time
        get_syscrop_detailsObj['system_crop_image'] = syscrops.system_crop_image
        get_syscrop_ListArray.append(get_syscrop_detailsObj)
    return jsonify({'get_syscrops': get_syscrop_ListArray})


@app.route('/update_sys_crop', methods=['GET', 'POST'])
@login_required
def update_sys_crop():
    if request.method == 'POST':
        sys_crp_id = request.form['crpid']
        update_sys_crops = SysCrop.query.filter_by(id=sys_crp_id).first()
        update_sys_crops.system_crop_name = request.form['maincropcategoryname']
        update_sys_crops.system_crop_sci_name = request.form['cropsciencename']
        update_sys_crops.system_crop_catgoery = request.form['cropcatogrtype']
        update_sys_crops.system_crop_growing_time = request.form['systemcropgrowingtime']
        # crp_update_img = request.files['file']
        if request.files['file']:
            picture_file = save_crop_picture(request.files['file'])
            update_sys_crops.system_crop_image = picture_file
        update_sys_crops.modified_timestamp = datetime.now()
        db.session.commit()
        flash('Crop Details has been updated!', 'success')
        return redirect(url_for('manage_sys_crops'))


@app.route('/add_sys_sub_cat', methods=['GET', 'POST'])
@login_required
def add_sys_sub_cat():
    syscrp_id = request.form['syscrp']
    chkduplicate = SysSubCategory.query.filter_by(id=syscrp_id).first()
    varityname = request.form['varietyname']
    if chkduplicate.variety_name == varityname:
        flash('Varitey Name Already in th Database', 'danger')
        return redirect(url_for('manage_sys_crops'))
    else:
        if request.files['files']:
            picture_file = save_crop_picture(request.files['files'])
            add_sub_crops = SysSubCategory(variety_name=request.form['varietyname'],
                                           line_designation=request.form['linedesignation'],
                                           pedgiree=request.form['pedgiree'], origin=request.form['suborigin'],
                                           method_of_propagation=request.form['method_propagation'],
                                           syscrop_id=syscrp_id, user_id=current_user.id,
                                           created_timestamp=datetime.now(), modified_timestamp=datetime.now(),
                                           sub_crop_image=picture_file)
            db.session.add(add_sub_crops)
            db.session.commit()
            flash('Data Insert Sucessfully', 'success')
            return redirect(url_for('manage_sys_crops'))


@app.route('/get_sub_cat_details/<id>', methods=['GET', 'POST'])
@login_required
def get_sub_cat_details(id):
    sys_sub_catogries = SysSubCategory.query.filter_by(syscrop_id=id).all()
    get_sub_category_ListArray = []
    for sys_sub_crops in sys_sub_catogries:
        get_sys_sub_crop_detailObj = {}
        get_sys_sub_crop_detailObj['id'] = sys_sub_crops.id
        get_sys_sub_crop_detailObj['variety_name'] = sys_sub_crops.variety_name
        get_sys_sub_crop_detailObj['line_designation'] = sys_sub_crops.line_designation
        get_sys_sub_crop_detailObj['pedgiree'] = sys_sub_crops.pedgiree
        get_sys_sub_crop_detailObj['origin'] = sys_sub_crops.origin
        get_sys_sub_crop_detailObj['method_of_propagation'] = sys_sub_crops.method_of_propagation
        get_sys_sub_crop_detailObj['syscrop_id'] = sys_sub_crops.id
        get_sys_sub_crop_detailObj['sub_crop_image'] = sys_sub_crops.sub_crop_image
        get_sub_category_ListArray.append(get_sys_sub_crop_detailObj)
    return jsonify({'get_all_sub_variety': get_sub_category_ListArray})


@app.route('/get_update_sub_cat_details/<id>', methods=['GET', 'POST'])
@login_required
def get_update_sub_cat_details(id):
    sys_sub_catogries = SysSubCategory.query.filter_by(id=id).all()
    get_sub_category_ListArray = []
    for sys_sub_crops in sys_sub_catogries:
        get_sys_sub_crop_detailObj = {}
        get_sys_sub_crop_detailObj['id'] = sys_sub_crops.id
        get_sys_sub_crop_detailObj['variety_name'] = sys_sub_crops.variety_name
        get_sys_sub_crop_detailObj['line_designation'] = sys_sub_crops.line_designation
        get_sys_sub_crop_detailObj['pedgiree'] = sys_sub_crops.pedgiree
        get_sys_sub_crop_detailObj['origin'] = sys_sub_crops.origin
        get_sys_sub_crop_detailObj['method_of_propagation'] = sys_sub_crops.method_of_propagation
        get_sys_sub_crop_detailObj['syscrop_id'] = sys_sub_crops.id
        get_sys_sub_crop_detailObj['sub_crop_image'] = sys_sub_crops.sub_crop_image
        get_sub_category_ListArray.append(get_sys_sub_crop_detailObj)
    return jsonify({'get_update_all_sub_variety': get_sub_category_ListArray})


@app.route('/update_sub_crop', methods=['GET', 'POST'])
@login_required
def update_sub_crop():
    if request.method == 'POST':
        sub_crp_id = request.form['subcrp_id']
        updatesyssybcategory = SysSubCategory.query.filter_by(id=sub_crp_id).first()
        updatesyssybcategory.variety_name = request.form['updatevarietyname']
        updatesyssybcategory.line_designation = request.form['updatelinedesignation']
        updatesyssybcategory.pedgiree = request.form['updatepedgiree']
        updatesyssybcategory.origin = request.form['updatesuborigin']
        updatesyssybcategory.method_of_propagation = request.form['update_method_propagation']
        if request.files['crpfiles']:
            picture_file = save_crop_picture(request.files['crpfiles'])
            updatesyssybcategory.sub_crop_image = picture_file
        updatesyssybcategory.modified_timestamp = datetime.now()
        db.session.commit()
        flash('Sub Crop Details has been updated!', 'success')
        return redirect(url_for('manage_sys_crops'))


@app.route('/add_yield_sub_crop', methods=['GET', 'POST'])
@login_required
def add_yield_sub_crop():
    if request.method == 'POST':
        sub_cat_id = request.form['subcat_id']
        addYiledInfo = SubCatYield(highest_yield_recorded=request.form['highestyieldrecord'],
                                   average_yield=request.form['averageyieldrecord'],
                                   average_yield_yla=request.form['average_yield_yla'],
                                   average_yield_mha=request.form['average_yield_mha'],
                                   reaction_to_salinity=request.form['reactiontosalinity'],
                                   syssubcategory_id=sub_cat_id, user_id=current_user.id,
                                   created_timestamp=datetime.now(), modified_timestamp=datetime.now())
        db.session.add(addYiledInfo)
        db.session.commit()
        flash('Data Insert Sucessfully', 'success')
        return redirect(url_for('manage_sys_crops'))


@app.route('/get_yield_crop_details/<id>', methods=['GET', 'POST'])
@login_required
def get_yield_crop_details(id):
    yields = SubCatYield.query.filter_by(syssubcategory_id=id).all()
    get_yield_ListArray = []
    for cyield in yields:
        get_yield_detailsObj = {}
        get_yield_detailsObj['id'] = cyield.id
        get_yield_detailsObj['highest_yield_recorded'] = cyield.highest_yield_recorded
        get_yield_detailsObj['average_yield'] = cyield.average_yield
        get_yield_detailsObj['average_yield_yla'] = cyield.average_yield_yla
        get_yield_detailsObj['average_yield_mha'] = cyield.average_yield_mha
        get_yield_detailsObj['reaction_to_salinity'] = cyield.reaction_to_salinity
        get_yield_detailsObj['syssubcategory_id'] = cyield.syssubcategory_id
        get_yield_ListArray.append(get_yield_detailsObj)
    return jsonify({'get_all_yield': get_yield_ListArray})


@app.route('/manage_farm_arpa', methods=['GET', 'POST'])
@login_required
def manage_farm_arpa():
    farmdata = Farm.query.filter_by(devisionoffice_id=current_user.devisionoffice_id).all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template(
        'arpafarms.html',
        title='Communication',
        year=datetime.now().year,
        image_file=image_file,
        farmdata=farmdata

    )


@app.route('/addnewfarm_by_arpa_officer', methods=['GET', 'POST'])
@login_required
def addnewfarm_by_arpa_officer():
    form = InsertNewFarmForm()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    district = District.query.all()
    area = Area.query.filter_by(district_id=1).all()
    devisionoffices = Devisionoffice.query.filter_by(area_id=2).all()
    users = User.query.filter_by(devisionoffice_id=current_user.devisionoffice_id).all()
    if form.validate_on_submit():

        farm = Farm(farmname=form.farmname.data, latitude=form.latitude.data, longitude=form.longitude.data,
                    phone=form.phone.data, address=form.address.data, email=form.email.data,
                    user_id=request.form['user'],
                    created_timestamp=datetime.now(), modified_timestamp=datetime.now(), surface=form.surface.data,
                    devisionoffice_id=request.form['devisionoffice'])
        db.session.add(farm)
        db.session.commit()
        flash('Your farm details insert sucessfully', 'success')
        return redirect(url_for('manage_farm_arpa'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    return render_template('addnewfarm_by_arpa.html', title='Add new Farm', year=datetime.now().year,
                           image_file=image_file,
                           form=form, district=district, area=area, devisionoffices=devisionoffices, users=users)


@app.route("/manage_farm_home/<int:id>/manage_farms_arpa", methods=['GET', 'POST'])
@login_required
def manage_farms_arpa(id):
    farm = Farm.query.get_or_404(id)
    if farm.devisionoffice_id != current_user.devisionoffice_id:
        flash('This is not your area farm', 'danger')
        return redirect(url_for('manage_farm_arpa'))
    farmdata = Farm.query.filter_by(id=id).all()
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('manage_arpa_farm_home.html', title='Farm Home', year=datetime.now().year,
                           image_file=image_file,
                           farmdata=farmdata)


@app.route("/manage_farm_home/select_farm/<int:id>/farm_croparpa", methods=['GET', 'POST'])
@login_required
def farm_manage_farm_crop_arpa(id):
    form = FarmCropForm()
    farm = Farm.query.get_or_404(id)
    if farm.devisionoffice_id != current_user.devisionoffice_id:
        flash('This is not your area farm', 'danger')
        return redirect(url_for('manage_farm_arpa'))
    farmdata = Farm.query.filter_by(id=id).all()
    system_inbuild_crops = SysCrop.query.all()
    myfarmCrop = Crop.query.filter_by(farm_id=id).all()
    system_pest_and_diseases = System_Pest_and_Diseases.query.all()
    current_season = get_season(date.today())
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template('manage_farm_crop_arpa.html', title='Farm Crop', year=datetime.now().year,
                           image_file=image_file,
                           farmdata=farmdata, system_inbuild_crops=system_inbuild_crops, myfarmCrop=myfarmCrop,
                           current_season=current_season, system_pest_and_diseases=system_pest_and_diseases)


@app.route('/insert_farm_crop_by_arpa', methods=['GET', 'POST'])
@login_required
def insert_farm_crop_by_arpa():
    if request.method == 'POST':
        id = request.form['fid']
        print(id)
        farm = Farm.query.get_or_404(id)

        farm_surface = farm.surface
        if farm.devisionoffice_id != current_user.devisionoffice_id:
            flash('This is not your area farm', 'danger')
            return redirect(url_for('manage_farm_arpa'))
        else:
            sub_crop_id = request.form['subcrops']
            print(sub_crop_id)
            syste_sub_crop_category_details = SysSubCategory.query.filter_by(id=sub_crop_id).first()
            farm_crop_name = syste_sub_crop_category_details.variety_name
            farm_crop_image = syste_sub_crop_category_details.sub_crop_image
            production_type = request.form['productiontypes']
            planting_unit = request.form['plantingunit']
            surface = request.form['surface']
            crop = Crop(cropeName=farm_crop_name, cropImage=farm_crop_image, farm_id=id,
                        created_timestamp=datetime.now(), modified_timestamp=datetime.now(),
                        sys_sub_crop_id=sub_crop_id, production_type=production_type,
                        panting_unit=planting_unit, crop_surface_on_farm=surface
                        )
            db.session.add(crop)
            db.session.commit()
            flash('Crop Added!', 'success')
            return redirect(url_for('farm_manage_farm_crop_arpa', id=id))
    else:
        return redirect(url_for('farm_manage_farm_crop_arpa', id=id))


@app.route('/submit_pest_d_info_by_arpa', methods=['GET', 'POST'])
@login_required
def submit_pest_d_info_by_arpa():
    if request.method == 'POST':
        farm_id = request.form['farm_ids']
        farm = Farm.query.get_or_404(farm_id)
        if farm.devisionoffice_id != current_user.devisionoffice_id:
            flash('This is not your area farm', 'danger')
            return redirect(url_for('manage_farm_arpa'))
        else:
            farm_id = farm_id
            farm = Farm.query.filter_by(id=farm_id).first()
            farmnme = farm.farmname
            farmlat = farm.latitude
            farmlong = farm.longitude
            sub_crp_id = request.form['pest_and_diseas_varity']
            syssubcategory = SysSubCategory.query.filter_by(id=sub_crp_id).first()
            syscrop_id = syssubcategory.syscrop_id
            varityname = syssubcategory.variety_name
            syscrop = SysCrop.query.filter_by(id=syscrop_id).first()
            syscrp_id = syscrop.id
            system_crop_names = syscrop.system_crop_name
            system_pd_id = request.form['pestdiseasname']
            system_pest_and_diseas = System_Pest_and_Diseases.query.filter_by(id=system_pd_id).first()
            pest_or_diseas_name = system_pest_and_diseas.threat_name
            threatment_type = request.form['threatmenttype']
            pstdsoultions = System_Pest_Disease_Soulutions.query.filter_by(threatment_type=threatment_type).first()

            if pstdsoultions is None:
                flash('This Solution not in the Database form not submmited', 'danger')
                return redirect(url_for('farm_manage_farm_crop_arpa', id=farm_id))
            else:
                system_pest_disease_soulutions_id = pstdsoultions.id
                threatment_method = request.form['threatmentname']
                threatment_chemi_amount = request.form['threatmentchemicalamount']
                threatment_method_descreption = request.form['descreption']
                optinal_details = request.form['optinal_details']
                prevention_level = request.form['prevention_level']
                farm_pest_details = Farm_pest_details(pest_or_diseas_name=pest_or_diseas_name,
                                                      threatment_type=threatment_type,
                                                      threatment_method=threatment_method,
                                                      threatment_method_descreption=threatment_method_descreption,
                                                      threatment_chemi_amount=threatment_chemi_amount,
                                                      optinal_details=optinal_details,
                                                      prevention_level=prevention_level,
                                                      soulution_image="no image yet",
                                                      system_crop_name=system_crop_names,
                                                      variety_name=varityname, farm_name=farmnme, farm_id=farm_id,
                                                      syscrop_id=syscrp_id,
                                                      system_pest_disease_soulutions_id=system_pest_disease_soulutions_id,
                                                      system_pest_and_diseases_id=system_pd_id,
                                                      syssubcategory_id=sub_crp_id, user_id=current_user.id,
                                                      created_timestamp=datetime.now(),
                                                      modified_timestamp=datetime.now(),
                                                      latitude=farmlat, longitude=farmlong)
                db.session.add(farm_pest_details)
                db.session.commit()
                flash('Data insert Sucessfully', 'success')
                return redirect(url_for('farm_manage_farm_crop_arpa', id=farm_id))


@app.route('/submit_furtilizer_result_by_arpa', methods=['GET', 'POST'])
@login_required
def submit_furtilizer_result_by_arpa():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        farm = Farm.query.get_or_404(farm_id)
        if farm.devisionoffice_id != current_user.devisionoffice_id:
            flash('This is not your area farm', 'danger')
            return redirect(url_for('manage_farm_arpa'))
        else:
            sub_crop_id = request.form['frtilizerresultvarity']
            syssubcategory = SysSubCategory.query.filter_by(id=sub_crop_id).first()
            syscrop_id = syssubcategory.syscrop_id
            varityname = syssubcategory.variety_name
            syscrop = SysCrop.query.filter_by(id=syscrop_id).first()
            system_crop_names = syscrop.system_crop_name
            fertilizer_id = request.form['crop_all_fertilzers']
            systemfertilizer = SystemFertilizer.query.filter_by(id=fertilizer_id).first()
            fertilizer_name = systemfertilizer.fertilizer_name
            main_fertilizer_type = systemfertilizer.fertilizer_main_type_name
            sub_fertilizer_type = systemfertilizer.fertilizer_sub_type_name
            crp_fertilizer_amount = int(request.form['fertilzeramount'])
            fertilizer_matter_name = systemfertilizer.fertilizer_matter
            system_crop_name = system_crop_names
            variety_name = varityname
            fertilzersurface = int(request.form['fertilzersurface'])
            fertilizer_result = request.form['fertilizer_result']
            subcrops_id = request.form['subcrop_id']
            fertilizermatter_id = systemfertilizer.fertilizermatter_id
            systemsubfertilizertyeps_id = systemfertilizer.systemsubfertilizertyeps_id
            systemfertilizertyeps_id = systemfertilizer.systemfertilizertyeps_id
            systemfertilizer_id = systemfertilizer.id
            user_id = current_user.id
            fertilizer_date = request.form['fertilizerdate']
            farm_id = farm_id
            farmfertilizerresults = FarmFertilizerResults(fertilizer_name=fertilizer_name,
                                                          main_fertilizer_type=main_fertilizer_type,
                                                          sub_fertilizer_type=sub_fertilizer_type,
                                                          farm_used_fertilizer_amount=crp_fertilizer_amount,
                                                          fertilizer_matter_name=fertilizer_matter_name,
                                                          system_crop_name=system_crop_name, variety_name=variety_name,
                                                          fertilizer_surface=fertilzersurface,
                                                          fertilizer_result=fertilizer_result,
                                                          syssubcategory_id=sub_crop_id, syscrop_id=syscrop_id,
                                                          fertilizermatter_id=fertilizermatter_id,
                                                          systemsubfertilizertyeps_id=systemsubfertilizertyeps_id,
                                                          systemfertilizertyeps_id=systemfertilizertyeps_id,
                                                          systemfertilizer_id=systemfertilizer_id, user_id=user_id,
                                                          fertilizer_date=fertilizer_date, farm_id=farm_id)
            db.session.add(farmfertilizerresults)
            db.session.commit()
            flash('Fertilizer Result Added!', 'success')
            return redirect(url_for('farm_manage_farm_crop_arpa', id=farm_id))


@app.route('/manage_all_farmers_by_arpa', methods=['GET', 'POST'])
@login_required
def manage_all_farmers_by_arpa():
    curnt_user_devison_office_id = current_user.devisionoffice_id
    users = User.query.filter_by(devisionoffice_id=curnt_user_devison_office_id).all()
    districts = District.query.all()
    areas = Area.query.all()
    devisionoffices = Devisionoffice.query.all()
    form = AddUserForm2()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf-8')
        user = User(fristname=form.fristname.data, lastname=form.lastname.data, email=form.email.data,
                    password=hashed_password, phone=form.phone.data, address=form.address.data,
                    profile='defaultprofile.jpg', usertype='Farmer', active=1,
                    devisionoffice_id=request.form['devisionoffice'], created_timestamp=datetime.now(),
                    modified_timestamp=datetime.now(), confirmed=False)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.email.data}!', 'success')
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template(
        'arpa_user_management.html',
        title='Manage All Farmers',
        year=datetime.now().year,
        image_file=image_file,
        users=users,
        districts=districts,
        areas=areas,
        devisionoffices=devisionoffices,
        form=form
    )


@app.route('/ado_arpa_field_visit_management', methods=['GET', 'POST'])
@login_required
def ado_arpa_field_visit_management():
    form = Field_VisitForm()
    if form.validate_on_submit():
        file = request.files['file']
        if file and allowed_file(file.filename):
            random_hex = secrets.token_hex(16)
            _, f_ext = os.path.splitext(file.filename)
            uniqename = random_hex + f_ext
            filename = secure_filename(uniqename)
            field_visit = Field_Visit(field_visit_date=form.field_visit_date.data,
                                      field_visit_name=form.field_visit_name.data,
                                      field_visit_descreption=form.ado_field_visit_descreption.data,
                                      attach_document=filename, isDone=False,
                                      devisionoffice_id=current_user.devisionoffice_id, user_id=current_user.id,
                                      created_timestamp=datetime.now(),
                                      modified_timestamp=datetime.now())
            db.session.add(field_visit)
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'Data Insert Sucessfully', 'success')
            return redirect(url_for('ado_arpa_field_visit_management'))
    page = request.args.get('page', 1, type=int)
    field_visit = Field_Visit.query.order_by(Field_Visit.modified_timestamp.desc()).paginate(page=page, per_page=10)
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template(
        'ado_arpa_filed_visit_mamagement.html',
        title='Manage Filed Visit',
        year=datetime.now().year,
        image_file=image_file,
        form=form, field_visit=field_visit
    )


@app.route('/get_field_visit_details/<id>', methods=['GET', 'POST'])
@login_required
def get_field_visit_details(id):
    get_field_visits = Field_Visit.query.filter_by(id=id).all()
    get_field_visits_ListArray = []
    for get_field_visit in get_field_visits:
        get_field_visitObj = {}
        get_field_visitObj['id'] = get_field_visit.id
        get_field_visitObj['field_visit_date'] = get_field_visit.field_visit_date
        get_field_visitObj['field_visit_name'] = get_field_visit.field_visit_name
        get_field_visitObj['field_visit_descreption'] = get_field_visit.field_visit_descreption
        get_field_visitObj['attach_document'] = get_field_visit.attach_document
        get_field_visitObj['isDone'] = get_field_visit.isDone
        get_field_visitObj['ado_field_visit_descreption'] = get_field_visit.ado_field_visit_descreption
        get_field_visitObj['attach_document_arpa'] = get_field_visit.attach_document_arpa
        get_field_visits_ListArray.append(get_field_visitObj)
    return jsonify({'getfieldvists': get_field_visits_ListArray})

@app.route('/charts')
def charts():
    """Renders the about page."""
    image_file = url_for('static', filename='profilepics/' + current_user.profile)
    return render_template(
        'charts.html',
        title='Chart',
        year=datetime.now().year,
        message='Charts',
        image_file=image_file
    )

