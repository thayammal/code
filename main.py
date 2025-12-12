from flask import Flask, render_template, session, redirect, request, url_for, abort, flash #Flask is a class from the Flask framework
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, login_required, logout_user
from controller.config import Config
from controller.database import db
from controller.models import *
from sqlalchemy import or_

app = Flask(__name__) #object creation
app.config.from_object(Config) # Load configuration from Config class
db.init_app(app) # Initialize the database with the Flask app

with app.app_context():
    db.create_all()  # Create database tables based on models
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)

    lot_manager_role = Role.query.filter_by(name='lot_manager').first()
    if not lot_manager_role:
        lot_manager_role = Role(name='lot_manager')
        db.session.add(lot_manager_role)

    customer_role = Role.query.filter_by(name='customer').first()
    if not customer_role:
        customer_role = Role(name='customer')
        db.session.add(customer_role)
    db.session.commit()


    admin_user = User.query.filter_by(username='VPA_ADMIN').first()
    if not admin_user:
        admin_user = User(
            username='VPA_ADMIN',
            email = 'admin@vpa.com',
            password_hash='123456',
            roles=[admin_role]
        )
        db.session.add(admin_user)
    db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.user_id
            # determine role
            roles = [r.name for r in user.roles]
            session['role'] = 'lot_manager' if 'lot_manager' in roles else 'customer'
            # redirect based on role
            if session['role'] == 'lot_manager':
                return redirect(url_for('dashboard'))
            else:
                return render_template('home.html')
        else:
            # invalid login
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')




@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')           # 'customer' or 'lot_manager'
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        # basic validation
        if not (role and name and email and mobile and password and confirm):
            flash('Please fill out all required fields', 'warning')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Passwords do not match', 'warning')
            return redirect(url_for('register'))

        # check email uniqueness
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'warning')
            return redirect(url_for('register'))

        # create User
        hashed_pw = generate_password_hash(password)
        new_user = User(username=name, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()  # so that new_user.user_id is assigned

        # assign role
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            # optionally create the role if not exists
            role_obj = Role(name=role)
            db.session.add(role_obj)
            db.session.commit()
        new_user.roles.append(role_obj)   #id, name, email, password_hash, roles(3,customer)

        # create profile depending on role
        if role == 'customer':
            profile = Customer(user_id=new_user.user_id,                               
                               mobile_number=mobile,
                               address=address,
                               flag=False)
        else:  # lot_manager
            profile = LotManager(user_id=new_user.user_id,
                                 mobile_number=mobile,
                                 address=address,
                                 flag=False)
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')    




@app.route('/dashboard')
def dashboard():
    user = User.query.get(session.get('user_id'))
    if not user:
        return redirect(url_for('login'))

    manager = LotManager.query.filter_by(user_id=user.user_id).first()
    if not manager:
        lots = []
    else:
        # Start with a Query object
        query = ParkingLot.query.filter_by(manager_id=manager.manager_id)

        search_term = request.args.get('search')
        if search_term:
            pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    ParkingLot.lot_name.ilike(pattern),
                    ParkingLot.city.ilike(pattern),
                    ParkingLot.pincode.ilike(pattern)
                )
            )

        # Only call .all() once at the end
        lots = query.all()

    return render_template('lotmanager.html', lots=lots)



@app.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if request.method == 'POST':
        # Read form fields
        lot_name = request.form.get('lot_name')
        address = request.form.get('address')
        city = request.form.get('city')
        pincode = request.form.get('pincode')
        
        # Convert to int so we can use in range()
        number_of_spots = request.form.get("number_of_spots", type=int)
        price = request.form.get("price_per_hour", type=float)

        manager = LotManager.query.filter_by(user_id=session.get('user_id')).first()
        if not manager:
            return redirect(url_for('dashboard'))

        # Create parking lot
        new_lot = ParkingLot(
            lot_name=lot_name,
            address=address,
            city=city,
            pincode=pincode,
            number_of_spots=number_of_spots,
            price_per_hour=price,
            manager_id=manager.manager_id
        )
        db.session.add(new_lot)
        db.session.commit()  # needed so new_lot.lot_id exists

        # Now create ParkingSpot objects
        for i in range(1, number_of_spots + 1):
            spot = ParkingSpot(
                lot_id=new_lot.lot_id,
                spot_number=str(i),
                is_occupied='A'  # default available
            )
            db.session.add(spot)

        db.session.commit()  # commit spot records too

        return redirect(url_for('dashboard'))

    return render_template("add_lot.html")


@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.lot_name = request.form.get('lot_name')
        lot.address = request.form.get('address')
        lot.city = request.form.get('city')
        lot.pincode = request.form.get('pincode')
        lot.price_per_hour = request.form.get("price_per_hour", type=float)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_lot.html', lot=lot)


@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('dashboard'))



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)