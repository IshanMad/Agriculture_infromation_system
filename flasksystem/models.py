from flasksystem import db, login_manager, app

from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# DATABASE MODELING
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    districtName = db.Column(db.Text, nullable=False)
    area = db.relationship('Area', backref='district', lazy=True)
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # add relation ship with area(one to Many)
    # one to many relationship beetween district and user which mean one district live in many users


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    areaName = db.Column(db.Text, nullable=False)
    devisionoffices = db.relationship('Devisionoffice', backref='area')
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # add Relationship with offices(one to many)
    # add crop growing area


class Devisionoffice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officeName = db.Column(db.Text, nullable=False)
    officeAddress = db.Column(db.Text, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    users = db.relationship('User', backref='devisionoffice')

    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    field_visit = db.relationship('Field_Visit', backref='devisionoffice')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fristname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Integer, nullable=False, unique=True)
    address = db.Column(db.Text, nullable=False)
    profile = db.Column(db.String(255), nullable=True)
    usertype = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean)
    farm = db.relationship('Farm', backref='user')
    fieldvisit = db.relationship('Fieldvisit', backref='user')
    systemfertilizertypes = db.relationship('SystemFertilizerTypes', backref='user')
    systemsubfertilizertyeps = db.relationship('SystemSubFertilizerTypes', backref='user')
    fertilizermatter = db.relationship('FertilizerMtter', backref='user')
    systemfertilizer = db.relationship('SystemFertilizer', backref='user')
    systemcommonfertilizerplan = db.relationship('SystemCommonFertilizerPlan', backref='user')
    farmfertilizerplan = db.relationship('FarmFertilizerPlan', backref='user')
    devisionoffice_id = db.Column(db.Integer, db.ForeignKey('devisionoffice.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    syscrops = db.relationship('SysCrop', backref='user')
    syssubcategories = db.relationship('SysSubCategory', backref='user')
    subcatyield = db.relationship('SubCatYield', backref='user')
    maturityies = db.relationship('Maturity', backref='user')
    importanttraits = db.relationship('ImportantTrait', backref='user')
    reactiontodiseases = db.relationship('ReactionToDisease', backref='user')
    reactiontoinsectpest = db.relationship('ReactionToInsectPest', backref='user')
    qulitycharacteristic = db.relationship('QulityCharacteristic', backref='user')
    cropseason = db.relationship('CropSeason', backref='user')
    farm_fertilizer_results = db.relationship('FarmFertilizerResults', backref='user')
    system_pest_and_diseases = db.relationship('System_Pest_and_Diseases', backref='user')
    system_pest_disease_soulutions = db.relationship('System_Pest_Disease_Soulutions', backref='user')
    farm_pest_details = db.relationship('Farm_pest_details', backref='user')
    field_visit = db.relationship('Field_Visit', backref='user')

    # one to many relationship between district and user which mean one district live in many
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_email_confirm_token(self, expier_time=1800):
        es = Serializer(app.config['SECRET_KEY'], expier_time)
        return es.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_email_token(token):
        se = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = se.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


farm_crops = db.Table('farm_crops',
                      db.Column('farm_id', db.Integer, db.ForeignKey('farm.id')),
                      db.Column('crop_id', db.Integer, db.ForeignKey('crop.id'))
                      )

farm_fieldvisits = db.Table('farm_fieldvisits',
                            db.Column('fieldvisit_id', db.Integer, db.ForeignKey('fieldvisit.id')),
                            db.Column('farm_id', db.Integer, db.ForeignKey('farm.id'))
                            )


class Fieldvisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vistareaname = db.Column(db.Text, nullable=False)
    specialnotes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmname = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float(10, 6), nullable=False)
    longitude = db.Column(db.Float(10, 6), nullable=False)
    phone = db.Column(db.Integer, nullable=False, unique=False)
    address = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), nullable=True, unique=False)
    farmtask = db.relationship('Farmtask', backref='farm')
    farmworker = db.relationship('Farmworker', backref='farm')
    fieldvisit = db.relationship('Fieldvisit', secondary=farm_fieldvisits, backref='farm')
    farmfertilizerplan = db.relationship('FarmFertilizerPlan', backref='farm')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    surface = db.Column(db.String(255), nullable=True, unique=False)
    devisionoffice_id = db.Column(db.Integer)
    farm_pest_details = db.relationship('Farm_pest_details',
                                        backref='farm')


class Farmtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taskName = db.Column(db.Text, nullable=False)
    isDone = db.Column(db.Boolean)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


crop_fertilizers = db.Table('crop_fertilizers',
                            db.Column('crop_id', db.Integer, db.ForeignKey('crop.id')),
                            db.Column('fertilizer_id', db.Integer, db.ForeignKey('fertilizer.id'))
                            )
crop_soils = db.Table('crop_soils',
                      db.Column('crop_id', db.Integer, db.ForeignKey('crop.id')),
                      db.Column('soil_id', db.Integer, db.ForeignKey('soil.id'))
                      )


class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cropeName = db.Column(db.Text, nullable=False)
    cropImage = db.Column(db.String(255), nullable=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    farms = db.relationship('Farm', secondary=farm_crops, backref='crop')
    harvest = db.relationship('Harvest', backref='crop')
    pestdisease = db.relationship('Pestdisease', backref='crop')
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    sys_sub_crop_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    production_type = db.Column(db.String(255), nullable=True)
    panting_unit = db.Column(db.String(255), nullable=True)
    crop_surface_on_farm = db.Column(db.String(255), nullable=True)
    # add relationships fertilizer,crop tasks,soils,user,harvesting,tasks


class Fertilizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fertlizerName = db.Column(db.Text, nullable=False)
    gorowingLevel = db.Column(db.Text, nullable=False)
    fertilizertype = db.Column(db.Text, nullable=False)
    crops = db.relationship('Crop', secondary=crop_fertilizers, backref='fertilizer')
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # Add relationship crops


class Soil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    soilidName = db.Column(db.Text, nullable=False)
    soilidType = db.Column(db.Text, nullable=False)
    growingLevel = db.Column(db.Text, nullable=False)
    crops = db.relationship('Crop', secondary=crop_soils, backref='soil')
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # add relationship with crop


class Harvest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cropName = db.Column(db.Text, nullable=False)
    harvestAmount = db.Column(db.Float, nullable=False)
    sellingPrice = db.Column(db.Float, nullable=False)
    datetime = db.Column(db.Date, nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'))

    # add relationship with crop


pestdisease_diseasethreatmants = db.Table('pestdisease_diseasethreatmants',
                                          db.Column('pestdisease_id', db.Integer, db.ForeignKey('pestdisease.id')),
                                          db.Column('diseasethreatmant_id', db.Integer,
                                                    db.ForeignKey('diseasethreatmant.id'))

                                          )


class Pestdisease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diseaseName = db.Column(db.Text, nullable=False)
    diseaseCauses = db.Column(db.Text, nullable=False)
    diseaseSymptons = db.Column(db.Text, nullable=False)
    crops_id = db.Column(db.Integer, db.ForeignKey('crop.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # add relationship with crops threatments


class Diseasethreatmant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threatmentName = db.Column(db.Text, nullable=False)
    threatments = db.Column(db.Text, nullable=False)
    threatmentChemicalLevel = db.Column(db.Text, nullable=False)
    preventionStatus = db.Column(db.Text, nullable=False)
    pestdisease = db.relationship('Pestdisease', secondary=pestdisease_diseasethreatmants, backref='diseasethreatmant')
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # add relationship with crops


# class Tasks(db.Model):
# taskid = db.Column(db.Integer, primary_key=True)
# taskName = db.Column(db.String(200), nullable=False)
# taskIsDone = db.Column(db.Boolean, nullable=False)
# taskStartDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
# taskEndDate = db.Column(db.DateTime, nullable=False)
# add relationships
class Farmworker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_frist_name = db.Column(db.Text, nullable=False)
    worker_last_name = db.Column(db.Text, nullable=False)
    worker_gender = db.Column(db.Boolean)
    worker_dob = db.Column(db.DateTime, nullable=False)
    worker_address = db.Column(db.Text, nullable=False)
    worker_phone = db.Column(db.Integer, nullable=False, unique=False)
    worker_type = db.Column(db.String(200), nullable=False)
    farmworker = db.relationship('FarmworkerAlarms', backref='farmworker')
    farmcomment = db.relationship('FarmWorkerComments', backref='farmworker')
    workedocument = db.relationship('FarmWorkerDocuments', backref='farmworker')
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class FarmworkerAlarms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_msg = db.Column(db.Text, nullable=False)
    worker_phone = db.Column(db.Integer, nullable=False, unique=False)
    farmworker_id = db.Column(db.Integer, db.ForeignKey('farmworker.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    alrm_date = db.Column(db.DateTime, nullable=False)


class FarmWorkerComments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_comment = db.Column(db.Text, nullable=False)
    farmworker_id = db.Column(db.Integer, db.ForeignKey('farmworker.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class FarmWorkerDocuments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_name = db.Column(db.Text, nullable=False)
    farmworker_id = db.Column(db.Integer, db.ForeignKey('farmworker.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    doc_title = db.Column(db.Text, nullable=False)


class SysCrop(db.Model):
    __tablename__ = 'syscrop'
    id = db.Column(db.Integer, primary_key=True)
    system_crop_name = db.Column(db.Text, nullable=True)
    system_crop_sci_name = db.Column(db.Text, nullable=True)
    system_crop_catgoery = db.Column(db.Text, nullable=True)
    system_crop_growing_time = db.Column(db.Text, nullable=True)
    system_crop_image = db.Column(db.String(255), nullable=True)
    # crop_id = db.Column(db.Integer(), db.ForeignKey('crop.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    syssubcategory = db.relationship('SysSubCategory', backref='syscrop')
    cropseason = db.relationship('CropSeason', backref='syscrop')
    systemcommonfertilizerplan = db.relationship('SystemCommonFertilizerPlan', backref='syscrop')
    farmfertilizerplan = db.relationship('FarmFertilizerPlan', backref='syscrop')
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    farm_fertilizer_results = db.relationship('FarmFertilizerResults', backref='syscrop')
    farm_pest_details = db.relationship('Farm_pest_details', backref='syscrop')


class SysSubCategory(db.Model):
    __tablename__ = 'syssubcategory'
    id = db.Column(db.Integer, primary_key=True)
    variety_name = db.Column(db.Text, nullable=True)
    line_designation = db.Column(db.Text, nullable=True)
    pedgiree = db.Column(db.Text, nullable=True)
    origin = db.Column(db.Text, nullable=True)
    method_of_propagation = db.Column(db.Text, nullable=True)
    syscrop_id = db.Column(db.Integer(), db.ForeignKey('syscrop.id'))
    sub_cat_yield = db.relationship('SubCatYield', backref='syssubcategory', uselist=False)
    maturity = db.relationship('Maturity', backref='syssubcategory', uselist=False)
    importanttrait = db.relationship('ImportantTrait', backref='syssubcategory', uselist=False)
    reactiontodisease = db.relationship('ReactionToDisease', backref='syssubcategory', uselist=False)
    reactiontoinsectpest = db.relationship('ReactionToInsectPest', backref='syssubcategory', uselist=False)
    qulitycharacteristic = db.relationship('QulityCharacteristic', backref='syssubcategory', uselist=False)
    farmfertilizerplan = db.relationship('FarmFertilizerPlan', backref='syssubcategory')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    sub_crop_image = db.Column(db.String(255), nullable=True)
    crops = db.relationship('Crop', backref='syssubcategory')
    farm_fertilizer_results = db.relationship('FarmFertilizerResults', backref='syssubcategory')
    farm_pest_details = db.relationship('Farm_pest_details', backref='syssubcategory')


class SubCatYield(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    highest_yield_recorded = db.Column(db.String(255), nullable=True)
    average_yield = db.Column(db.String(255), nullable=True)
    average_yield_yla = db.Column(db.String(255), nullable=True)
    average_yield_mha = db.Column(db.String(255), nullable=True)
    reaction_to_salinity = db.Column(db.String(255), nullable=True)
    syssubcategory_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class Maturity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seson_name = db.Column(db.Text, nullable=True)
    num_of_date = db.Column(db.String(255), nullable=True)
    syssubcategory_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class ImportantTrait(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    traits_name = db.Column(db.Text, nullable=True)
    traits_descreption = db.Column(db.Text, nullable=True)
    syssubcategory_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class ReactionToDisease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diseasese_name = db.Column(db.Text, nullable=True)
    syssubcategory_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    resistant = db.Column(db.Boolean)
    moderately_resistant = db.Column(db.Boolean)
    susceptible = db.Column(db.Boolean)
    moderately_susceptible = db.Column(db.Boolean)
    system_pest_and_diseases_id = db.Column(db.Integer)
    syssubcategory_name = db.Column(db.Text, nullable=True)


class ReactionToInsectPest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diseasese_name = db.Column(db.Text, nullable=True)
    syssubcategory_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    resistant = db.Column(db.Boolean)
    moderately_resistant = db.Column(db.Boolean)
    susceptible = db.Column(db.Boolean)
    moderately_susceptible = db.Column(db.Boolean)
    system_pest_and_diseases_id = db.Column(db.Integer)
    syssubcategory_name = db.Column(db.Text, nullable=True)


class QulityCharacteristic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characteristic_name = db.Column(db.Text, nullable=True)
    characteristic_descreption = db.Column(db.Text, nullable=True)
    syssubcategory_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class SystemFertilizerTypes(db.Model):
    __tablename__ = 'systemfertilizertyeps'
    id = db.Column(db.Integer, primary_key=True)
    main_fertilizer_type = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    systemsubfertilizertyeps = db.relationship('SystemSubFertilizerTypes', backref='systemfertilizertyeps')
    systemFertilizer = db.relationship('SystemFertilizer', backref='systemfertilizertyeps')
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class FertilizerMtter(db.Model):
    __tablename__ = 'fertilizermatter'
    id = db.Column(db.Integer, primary_key=True)
    fertilizer_matter_name = db.Column(db.Text, nullable=True)
    systemFertilizer = db.relationship('SystemFertilizer', backref='fertilizermatter')
    systemsubfertilizertyeps = db.relationship('SystemSubFertilizerTypes', backref='fertilizermatter')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    farm_fertilizer_results = db.relationship('FarmFertilizerResults', backref='fertilizermatter')


class SystemSubFertilizerTypes(db.Model):
    __tablename__ = 'systemsubfertilizertyeps'
    id = db.Column(db.Integer, primary_key=True)
    sub_fertilizer_type = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    systemFertilizer = db.relationship('SystemFertilizer', backref='systemsubfertilizertyeps')
    systemfertilizertyeps_id = db.Column(db.Integer(), db.ForeignKey('systemfertilizertyeps.id'))
    fertilizermatter_id = db.Column(db.Integer(), db.ForeignKey('fertilizermatter.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    farm_fertilizer_results = db.relationship('FarmFertilizerResults', backref='systemsubfertilizertyeps')


class SystemFertilizer(db.Model):
    __tablename__ = 'systemfertilizer'
    id = db.Column(db.Integer, primary_key=True)
    fertilizer_name = db.Column(db.Text, nullable=True)
    fertilizer_image = db.Column(db.String(255), nullable=True)
    fertilizer_document = db.Column(db.String(255), nullable=True)
    fertilizer_descreption = db.Column(db.Text, nullable=True)
    fertilizer_main_type_name = db.Column(db.Text, nullable=True)
    fertilizer_sub_type_name = db.Column(db.Text, nullable=True)
    fertilizer_user_instructons = db.Column(db.Text, nullable=True)
    fertilizer_matter = db.Column(db.Text, nullable=True)
    systemfertilizertyeps_id = db.Column(db.Integer(), db.ForeignKey('systemfertilizertyeps.id'))
    fertilizermatter_id = db.Column(db.Integer(), db.ForeignKey('fertilizermatter.id'))
    systemsubfertilizertyeps_id = db.Column(db.Integer(), db.ForeignKey('systemsubfertilizertyeps.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    systemcommonfertilizerplan = db.relationship('SystemCommonFertilizerPlan', backref='systemFertilizer')
    farmfertilizerplan = db.relationship('FarmFertilizerPlan', backref='systemFertilizer')
    farm_fertilizer_results = db.relationship('FarmFertilizerResults', backref='systemFertilizer')


class SystemCommonFertilizerPlan(db.Model):
    __tablename__ = 'systemcommonfertilizerplan'
    id = db.Column(db.Integer, primary_key=True)
    crop_age_range = db.Column(db.Text, nullable=True)
    fertilizer_need_time = db.Column(db.Text, nullable=True)
    fertilizer_name = db.Column(db.Text, nullable=True)
    fertilizer_amount = db.Column(db.Text, nullable=True)
    sys_crop_category_name = db.Column(db.Text, nullable=True)
    syscrop_id = db.Column(db.Integer(), db.ForeignKey('syscrop.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    fertilizer_need_time_name = db.Column(db.Text, nullable=True)
    systemfertilizer_id = db.Column(db.Integer, db.ForeignKey('systemfertilizer.id'))
    production_type = db.Column(db.String(255), nullable=True)
    season_id = db.Column(db.Integer)


class FarmFertilizerPlan(db.Model):
    __tablename__ = 'farmfertilizerplan'
    id = db.Column(db.Integer, primary_key=True)
    crop_age_range = db.Column(db.Text, nullable=True)
    fertilizer_need_time = db.Column(db.Text, nullable=True)
    fertilizer_name = db.Column(db.Text, nullable=True)
    fertilizer_amount = db.Column(db.Text, nullable=True)
    sys_crop_category_name = db.Column(db.Text, nullable=True)
    sys_sub_crop_category_name = db.Column(db.Text, nullable=True)
    syscrop_id = db.Column(db.Integer(), db.ForeignKey('syscrop.id'))
    syssubcategory_id = db.Column(db.Integer(), db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    fertilizer_need_time_name = db.Column(db.Text, nullable=True)
    systemfertilizer_id = db.Column(db.Integer, db.ForeignKey('systemfertilizer.id'))
    production_type = db.Column(db.String(255), nullable=True)
    season_id = db.Column(db.Integer)


class CropSeason(db.Model):
    __tablename__ = 'cropseason'
    id = db.Column(db.Integer, primary_key=True)
    season_name = db.Column(db.Text, nullable=True)
    crop_name = db.Column(db.Text, nullable=True)
    variety_name = db.Column(db.Text, nullable=True)
    syscrop_id = db.Column(db.Integer(), db.ForeignKey('syscrop.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class FarmFertilizerResults(db.Model):
    __tablename__ = 'farm_fertilizer_results'
    id = db.Column(db.Integer, primary_key=True)
    fertilizer_name = db.Column(db.Text, nullable=True)
    main_fertilizer_type = db.Column(db.Text, nullable=True)
    sub_fertilizer_type = db.Column(db.Text, nullable=True)
    farm_used_fertilizer_amount = db.Column(db.Text, nullable=True)
    fertilizer_matter_name = db.Column(db.Text, nullable=True)
    system_crop_name = db.Column(db.Text, nullable=True)
    variety_name = db.Column(db.Text, nullable=True)
    fertilizer_surface = db.Column(db.String(255), nullable=True)
    fertilizer_result = db.Column(db.Integer, nullable=True)
    syssubcategory_id = db.Column(db.Integer, db.ForeignKey('syssubcategory.id'))
    syscrop_id = db.Column(db.Integer, db.ForeignKey('syscrop.id'))
    fertilizermatter_id = db.Column(db.Integer, db.ForeignKey('fertilizermatter.id'))
    systemsubfertilizertyeps_id = db.Column(db.Integer, db.ForeignKey('systemsubfertilizertyeps.id'))
    systemfertilizertyeps_id = db.Column(db.Integer, db.ForeignKey('systemfertilizertyeps.id'))
    systemfertilizer_id = db.Column(db.Integer, db.ForeignKey('systemfertilizer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fertilizer_date = db.Column(db.DateTime)
    farm_id = db.Column(db.Integer)


class System_Pest_and_Diseases(db.Model):
    __tablename__ = 'system_pest_and_diseases'
    id = db.Column(db.Integer, primary_key=True)
    threat_name = db.Column(db.Text, nullable=True)
    threat_sci_name = db.Column(db.Text, nullable=True)
    threat_type = db.Column(db.Text, nullable=True)
    disease_name = db.Column(db.Text, nullable=True)
    disease_symptoms = db.Column(db.Text, nullable=True)
    disease_causes = db.Column(db.Text, nullable=True)
    disease_discreption = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    system_pest_disease_soulutions = db.relationship('System_Pest_Disease_Soulutions',
                                                     backref='system_pest_and_diseases')
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    threat_image = db.Column(db.Text, nullable=True)
    farm_pest_details = db.relationship('Farm_pest_details',
                                        backref='system_pest_and_diseases')


class System_Pest_Disease_Soulutions(db.Model):
    __tablename__ = 'system_pest_disease_soulutions'
    id = db.Column(db.Integer, primary_key=True)
    pest_or_diseas_name = db.Column(db.Text, nullable=True)
    threatment_type = db.Column(db.Text, nullable=True)
    threatment_method = db.Column(db.Text, nullable=True)
    threatment_chemi_amount = db.Column(db.Text, nullable=True)
    threatment_method_descreption = db.Column(db.Text, nullable=True)
    prevention_level = db.Column(db.Text, nullable=True)
    system_pest_and_diseases_id = db.Column(db.Integer, db.ForeignKey('system_pest_and_diseases.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    soulution_image = db.Column(db.Text, nullable=True)
    farm_pest_details = db.relationship('Farm_pest_details',
                                        backref='system_pest_disease_soulutions')


class Farm_pest_details(db.Model):
    __tablename__ = 'farm_pest_details'
    id = db.Column(db.Integer, primary_key=True)
    pest_or_diseas_name = db.Column(db.Text, nullable=True)
    threatment_type = db.Column(db.Text, nullable=True)
    threatment_method = db.Column(db.Text, nullable=True)
    threatment_method_descreption = db.Column(db.Text, nullable=True)
    threatment_chemi_amount = db.Column(db.Text, nullable=True)
    optinal_details = db.Column(db.Text, nullable=True)
    prevention_level = db.Column(db.Text, nullable=True)
    soulution_image = db.Column(db.Text, nullable=True)
    system_crop_name = db.Column(db.Text, nullable=True)
    variety_name = db.Column(db.Text, nullable=True)
    farm_name = db.Column(db.Text, nullable=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    syscrop_id = db.Column(db.Integer, db.ForeignKey('syscrop.id'))
    system_pest_disease_soulutions_id = db.Column(db.Integer, db.ForeignKey('system_pest_disease_soulutions.id'))
    system_pest_and_diseases_id = db.Column(db.Integer, db.ForeignKey('system_pest_and_diseases.id'))
    syssubcategory_id = db.Column(db.Integer, db.ForeignKey('syssubcategory.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    latitude = db.Column(db.Float(10, 6), nullable=False)
    longitude = db.Column(db.Float(10, 6), nullable=False)


class Field_Visit(db.Model):
    __tablename__ = 'field_visit'
    id = db.Column(db.Integer, primary_key=True)
    field_visit_date = db.Column(db.DateTime, default=datetime.now)
    field_visit_name = db.Column(db.Text, nullable=True)
    field_visit_descreption = db.Column(db.Text, nullable=True)
    attach_document = db.Column(db.Text, nullable=True)
    isDone =  db.Column(db.Boolean)
    devisionoffice_id = db.Column(db.Integer, db.ForeignKey('devisionoffice.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_timestamp = db.Column(db.DateTime, default=datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    ado_field_visit_descreption = db.Column(db.Text, nullable=True)
    attach_document_arpa = db.Column(db.Text, nullable=True)