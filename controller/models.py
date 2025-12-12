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



class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    lot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    pincode = db.Column(db.String(10), nullable=False)     # <--- new field for PIN code
    city = db.Column(db.String(100), nullable=True)     
    number_of_spots = db.Column(db.Integer, nullable=True)
    price_per_hour = db.Column(db.Float, nullable=True)   # optional
    created_on = db.Column(db.DateTime, default=db.func.now())
    manager_id = db.Column(db.Integer, db.ForeignKey('lot_manager.manager_id'), nullable=False)
    manager = db.relationship('LotManager', backref=db.backref('lots', lazy=True))
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete-orphan")


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    spot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id'), nullable=False)
    spot_number = db.Column(db.String(50), nullable=False)  # e.g., "A1", "001", etc.
    is_occupied = db.Column(db.String(1), nullable=False, default='A') # 'A' for available, 'O' for occupied
    vehicle_reg_no = db.Column(db.String(50), nullable=True)  # optionally store currently parked vehicle's reg no
    occupied_since = db.Column(db.DateTime, nullable=True)