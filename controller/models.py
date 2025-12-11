from controller.database import db

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy=True), lazy=True)
    customer_details = db.relationship('Customer', backref='user',lazy=True, uselist=False)
    lot_manager_details = db.relationship('LotManager', backref='user', lazy=True, uselist=False)

class Role(db.Model):  #hard coded, admin also need include with hard coded.
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False) # admin, lot_manager, customer
   

class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))

class LotManager(db.Model):
    __tablename__ = 'lot_manager'
    manager_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    flag = db.Column(db.Boolean, default=False)


class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    flag = db.Column(db.Boolean, default=False)

    