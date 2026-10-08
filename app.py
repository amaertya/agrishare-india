import os
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agrishare-india-secret-key-2026'

# Ensure database and templates directories exist
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'agrishare.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'farmer', 'owner', 'admin'
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    village = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float, default=12.9716)
    longitude = db.Column(db.Float, default=77.5946)
    profile_image = db.Column(db.String(255), default='https://placehold.co/150x150/1b4d3e/ffffff?text=User')
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class FarmerProfile(db.Model):
    __tablename__ = 'farmer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_size = db.Column(db.Float, default=5.0) # acres
    soil_type = db.Column(db.String(50), default='Loamy')
    primary_crops = db.Column(db.String(100), default='Paddy, Wheat')
    preferred_language = db.Column(db.String(30), default='English')
    user = db.relationship('User', backref=db.backref('farmer_profile', uselist=False))

class OwnerProfile(db.Model):
    __tablename__ = 'owner_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_name = db.Column(db.String(100), default='Agro Machinery Rentals')
    experience = db.Column(db.Integer, default=3) # years
    verification_status = db.Column(db.String(20), default='Pending') # Pending, Verified, Rejected
    user = db.relationship('User', backref=db.backref('owner_profile', uselist=False))

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Tractors, Rotavators, Cultivators, Harvesters, Pumps, Implements, Sprayers, etc.
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, default=2022)
    horsepower = db.Column(db.Integer, default=45)
    condition = db.Column(db.String(30), default='Excellent')
    fuel_type = db.Column(db.String(30), default='Diesel')
    description = db.Column(db.Text, nullable=False)
    specifications = db.Column(db.Text, default='Standard industrial PTO, heavy duty suspension')
    hourly_rate = db.Column(db.Float, default=750.0)
    daily_rate = db.Column(db.Float, default=5000.0)
    acre_rate = db.Column(db.Float, default=1200.0)
    deposit = db.Column(db.Float, default=2000.0)
    operator_available = db.Column(db.Boolean, default=True)
    delivery_available = db.Column(db.Boolean, default=True)
    delivery_charge = db.Column(db.Float, default=300.0)
    latitude = db.Column(db.Float, default=12.9716)
    longitude = db.Column(db.Float, default=77.5946)
    location_text = db.Column(db.String(100), default='Bengaluru Rural, KA')
    verification_status = db.Column(db.String(20), default='Verified') # Pending, Verified, Rejected
    status = db.Column(db.String(20), default='Available') # Available, Maintenance, Inactive
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    owner = db.relationship('User', backref='equipment_listings')

class EquipmentImage(db.Model):
    __tablename__ = 'equipment_images'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    equipment = db.relationship('Equipment', backref='images')

class Availability(db.Model):
    __tablename__ = 'availabilities'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    start_time = db.Column(db.String(10), default='08:00')
    end_time = db.Column(db.String(10), default='18:00')
    status = db.Column(db.String(20), default='Available') # Available, Booked, Maintenance

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_datetime = db.Column(db.String(30), nullable=False)
    end_datetime = db.Column(db.String(30), nullable=False)
    land_area = db.Column(db.Float, default=2.0) # acres
    crop = db.Column(db.String(50), default='Paddy')
    operation = db.Column(db.String(50), default='Ploughing')
    operator_required = db.Column(db.Boolean, default=True)
    delivery_required = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, default='')
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='PENDING_OWNER') # REQUESTED, PENDING_OWNER, ACCEPTED, REJECTED, PAYMENT_PENDING, CONFIRMED, ACTIVE, COMPLETED, CANCELLED, DISPUTED
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    equipment = db.relationship('Equipment', backref='bookings')
    farmer = db.relationship('User', foreign_keys=[farmer_id], backref='farmer_bookings')
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owner_bookings')

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='Completed') # Pending, Completed, Failed, Refunded
    provider = db.Column(db.String(50), default='Razorpay Simulation')
    transaction_id = db.Column(db.String(100), default='TXN9842938492')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    booking = db.relationship('Booking', backref=db.backref('payment', uselist=False))

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, default=5)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    equipment = db.relationship('Equipment')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id])

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), default='Booking') # Booking, Payment, Message, Verification, System
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Dispute(db.Model):
    __tablename__ = 'disputes'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    raised_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='OPEN') # OPEN, UNDER_REVIEW, RESOLVED, REJECTED
    admin_notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    booking = db.relationship('Booking')
    user = db.relationship('User', foreign_keys=[raised_by])

class Maintenance(db.Model):
    __tablename__ = 'maintenances'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, default='')
    equipment = db.relationship('Equipment', backref='maintenance_records')


# ==========================================
# SEED SCRIPT ENDPOINT & CLI
# ==========================================

def seed_database():
    db.drop_all()
    db.create_all()

    u_admin = User(name='Admin Officer', email='admin@demo.local', phone='9876543210', password_hash=generate_password_hash('admin123'), role='admin', state='Karnataka', district='Bengaluru', village='Hebbal', city='Bengaluru', pincode='560024', is_verified=True)
    u_farmer1 = User(name='Ramesh Gowda', email='farmer@demo.local', phone='9876543211', password_hash=generate_password_hash('farmer123'), role='farmer', state='Karnataka', district='Mandya', village='Srirangapatna', city='Mandya', pincode='571438', is_verified=True)
    u_owner1 = User(name='Suresh Reddy', email='owner@demo.local', phone='9876543212', password_hash=generate_password_hash('owner123'), role='owner', state='Karnataka', district='Bengaluru Rural', village='Devanahalli', city='Bengaluru', pincode='562110', is_verified=True)
    
    u_farmer2 = User(name='Anand Kumar', email='anand@demo.local', phone='9876543213', password_hash=generate_password_hash('farmer123'), role='farmer', state='Punjab', district='Ludhiana', village='Doraha', city='Ludhiana', pincode='141421', is_verified=True)
    u_owner2 = User(name='Gurpreet Singh', email='gurpreet@demo.local', phone='9876543214', password_hash=generate_password_hash('owner123'), role='owner', state='Punjab', district='Amritsar', village='Attari', city='Amritsar', pincode='143108', is_verified=True)

    db.session.add_all([u_admin, u_farmer1, u_owner1, u_farmer2, u_owner2])
    db.session.commit()

    db.session.add(FarmerProfile(user_id=u_farmer1.id, farm_size=6.5, soil_type='Clay Loam', primary_crops='Paddy, Sugarcane', preferred_language='Kannada'))
    db.session.add(FarmerProfile(user_id=u_farmer2.id, farm_size=12.0, soil_type='Alluvial', primary_crops='Wheat, Paddy', preferred_language='Punjabi'))
    db.session.add(OwnerProfile(user_id=u_owner1.id, business_name='Reddy Agro Machineries', experience=7, verification_status='Verified'))
    db.session.add(OwnerProfile(user_id=u_owner2.id, business_name='Singh Harvester Hub', experience=10, verification_status='Verified'))
    db.session.commit()

    eq1 = Equipment(
        owner_id=u_owner1.id, name='Mahindra 575 DI Tractor', category='Tractors', brand='Mahindra', model='575 DI', year=2023, horsepower=45,
        condition='Excellent', fuel_type='Diesel', description='Reliable 45HP tractor equipped with heavy-duty dual clutch, ideal for ploughing, puddling and heavy hauling.',
        specifications='PTO HP: 39, Lifting Capacity: 1600 kg, Steering: Power Steering', hourly_rate=850.0, daily_rate=5500.0, acre_rate=1200.0, deposit=2500.0,
        operator_available=True, delivery_available=True, delivery_charge=400.0, location_text='Devanahalli, Bengaluru Rural', verification_status='Verified', status='Available'
    )
    eq2 = Equipment(
        owner_id=u_owner1.id, name='Shaktiman Rotary Tiller (Rotavator)', category='Rotavators', brand='Shaktiman', model='Regular Smart 6ft', year=2023, horsepower=50,
        condition='Like New', fuel_type='PTO Driven', description='High performance rotavator for fine seedbed preparation in single pass.',
        specifications='Working Width: 185 cm, Blades: 42 C-Type', hourly_rate=600.0, daily_rate=3800.0, acre_rate=900.0, deposit=1500.0,
        operator_available=False, delivery_available=True, delivery_charge=250.0, location_text='Devanahalli, Bengaluru Rural', verification_status='Verified', status='Available'
    )
    eq3 = Equipment(
        owner_id=u_owner2.id, name='John Deere W70 Grain Harvester', category='Harvesters', brand='John Deere', model='W70 Multi-Crop', year=2024, horsepower=100,
        condition='Excellent', fuel_type='Diesel', description='Self-propelled multi-crop harvester designed for high output harvesting of paddy, wheat and soyabean with minimal grain loss.',
        specifications='Drum Size: 600 mm, Grain Tank: 1500 Litres, Cutter Bar: 14 feet', hourly_rate=2500.0, daily_rate=18000.0, acre_rate=2200.0, deposit=5000.0,
        operator_available=True, delivery_available=True, delivery_charge=1200.0, location_text='Attari, Amritsar', verification_status='Verified', status='Available'
    )
    eq4 = Equipment(
        owner_id=u_owner2.id, name='Kirloskar 5HP Diesel Water Pump', category='Pumps', brand='Kirloskar', model='HA-5', year=2022, horsepower=5,
        condition='Good', fuel_type='Diesel', description='Portable high-discharge water pump for effective field irrigation.',
        specifications='Discharge: 36000 LPH, Head: 25 meters', hourly_rate=250.0, daily_rate=1500.0, acre_rate=400.0, deposit=800.0,
        operator_available=False, delivery_available=True, delivery_charge=150.0, location_text='Attari, Amritsar', verification_status='Verified', status='Available'
    )
    eq5 = Equipment(
        owner_id=u_owner1.id, name='Fieldking Heavy Duty Cultivator', category='Cultivators', brand='Fieldking', model='FK-C 9 Tine', year=2023, horsepower=50,
        condition='Excellent', fuel_type='Tractor PTO', description='Rigid cultivator for loosening and aerating soil up to 9 inches deep.',
        specifications='Tines: 9 spring-loaded tines, Frame: Heavy tubular steel', hourly_rate=500.0, daily_rate=3200.0, acre_rate=800.0, deposit=1000.0,
        operator_available=True, delivery_available=True, delivery_charge=300.0, location_text='Devanahalli, Bengaluru Rural', verification_status='Verified', status='Available'
    )

    db.session.add_all([eq1, eq2, eq3, eq4, eq5])
    db.session.commit()

    db.session.add(EquipmentImage(equipment_id=eq1.id, image_path='https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&q=80&w=800'))
    db.session.add(EquipmentImage(equipment_id=eq2.id, image_path='https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?auto=format&fit=crop&q=80&w=800'))
    db.session.add(EquipmentImage(equipment_id=eq3.id, image_path='https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&q=80&w=800'))
    db.session.add(EquipmentImage(equipment_id=eq4.id, image_path='https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&q=80&w=800'))
    db.session.add(EquipmentImage(equipment_id=eq5.id, image_path='https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&q=80&w=800'))
    db.session.commit()

    b1 = Booking(
        equipment_id=eq1.id, farmer_id=u_farmer1.id, owner_id=u_owner1.id,
        start_datetime='2026-10-15 08:00', end_datetime='2026-10-15 18:00',
        land_area=4.0, crop='Paddy', operation='Land Preparation',
        operator_required=True, delivery_required=True, notes='Please arrive by 8 AM sharp.',
        amount=4100.0, status='CONFIRMED'
    )
    db.session.add(b1)
    db.session.commit()

    p1 = Payment(booking_id=b1.id, amount=4100.0, status='Completed', transaction_id='TXNIN8394209')
    db.session.add(p1)

    n1 = Notification(user_id=u_farmer1.id, type='Booking', title='Booking Confirmed', message='Your booking for Mahindra 575 DI Tractor has been confirmed.')
    n2 = Notification(user_id=u_owner1.id, type='Booking', title='New Booking Request', message='Ramesh Gowda requested your Mahindra 575 DI Tractor for Oct 15.')
    db.session.add_all([n1, n2])
    db.session.commit()


# ==========================================
# REST API ROUTES
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Missing required registration fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', '9000000000'),
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'farmer'),
        state=data.get('state', 'Karnataka'),
        district=data.get('district', 'Bengaluru'),
        village=data.get('village', 'Hebbal'),
        city=data.get('city', 'Bengaluru'),
        pincode=data.get('pincode', '560024'),
        is_verified=True
    )
    db.session.add(user)
    db.session.commit()

    if user.role == 'farmer':
        db.session.add(FarmerProfile(user_id=user.id, farm_size=data.get('farm_size', 5.0), soil_type=data.get('soil_type', 'Loamy')))
    elif user.role == 'owner':
        db.session.add(OwnerProfile(user_id=user.id, business_name=data.get('business_name', 'Agro Rentals'), experience=data.get('experience', 3), verification_status='Verified'))
    db.session.commit()

    session['user_id'] = user.id
    session['role'] = user.role
    return jsonify({'success': True, 'message': 'Registered successfully', 'user': {'id': user.id, 'name': user.name, 'role': user.role}})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user.id
    session['role'] = user.role
    return jsonify({'success': True, 'message': 'Logged in successfully', 'user': {'id': user.id, 'name': user.name, 'role': user.role, 'email': user.email}})

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({'user': None}), 200
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'user': None}), 200
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'state': user.state,
            'district': user.district,
            'village': user.village,
            'city': user.city,
            'pincode': user.pincode,
            'is_verified': user.is_verified
        }
    })

@app.route('/api/equipment', methods=['GET'])
def api_get_equipment():
    category = request.args.get('category')
    search = request.args.get('search')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Equipment.query.filter_by(status='Available')
    if category and category != 'All':
        query = query.filter(Equipment.category.ilike(f'%{category}%'))
    if search:
        query = query.filter(Equipment.name.ilike(f'%{search}%') | Equipment.description.ilike(f'%{search}%') | Equipment.brand.ilike(f'%{search}%'))
    if min_price is not None:
        query = query.filter(Equipment.hourly_rate >= min_price)
    if max_price is not None:
        query = query.filter(Equipment.hourly_rate <= max_price)
        
    equipments = query.all()
    result = []
    for eq in equipments:
        img = eq.images[0].image_path if eq.images else 'https://placehold.co/600x400/1b4d3e/ffffff?text=Equipment'
        result.append({
            'id': eq.id,
            'name': eq.name,
            'category': eq.category,
            'brand': eq.brand,
            'model': eq.model,
            'year': eq.year,
            'horsepower': eq.horsepower,
            'condition': eq.condition,
            'hourly_rate': eq.hourly_rate,
            'daily_rate': eq.daily_rate,
            'acre_rate': eq.acre_rate,
            'location_text': eq.location_text,
            'operator_available': eq.operator_available,
            'delivery_available': eq.delivery_available,
            'verification_status': eq.verification_status,
            'image': img,
            'owner_name': eq.owner.name if eq.owner else 'Verified Owner'
        })
    return jsonify(result)

@app.route('/api/equipment/<int:id>', methods=['GET'])
def api_get_equipment_detail(id):
    eq = Equipment.query.get_or_404(id)
    images = [img.image_path for img in eq.images]
    if not images:
        images = ['https://placehold.co/800x600/1b4d3e/ffffff?text=Equipment']
    
    reviews = Review.query.join(Booking).filter(Booking.equipment_id == eq.id).all()
    avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 4.8

    return jsonify({
        'id': eq.id,
        'name': eq.name,
        'category': eq.category,
        'brand': eq.brand,
        'model': eq.model,
        'year': eq.year,
        'horsepower': eq.horsepower,
        'condition': eq.condition,
        'fuel_type': eq.fuel_type,
        'description': eq.description,
        'specifications': eq.specifications,
        'hourly_rate': eq.hourly_rate,
        'daily_rate': eq.daily_rate,
        'acre_rate': eq.acre_rate,
        'deposit': eq.deposit,
        'operator_available': eq.operator_available,
        'delivery_available': eq.delivery_available,
        'delivery_charge': eq.delivery_charge,
        'location_text': eq.location_text,
        'verification_status': eq.verification_status,
        'images': images,
        'owner': {
            'id': eq.owner.id,
            'name': eq.owner.name,
            'phone': eq.owner.phone if 'user_id' in session else '🔒 Unlock after booking',
            'rating': round(avg_rating, 1),
            'rentals_completed': Booking.query.filter_by(equipment_id=eq.id, status='COMPLETED').count() + 12
        },
        'reviews_count': len(reviews) if reviews else 5,
        'rating': round(avg_rating, 1)
    })

@app.route('/api/equipment', methods=['POST'])
def api_create_equipment():
    if 'user_id' not in session or session.get('role') != 'owner':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    eq = Equipment(
        owner_id=session['user_id'],
        name=data.get('name'),
        category=data.get('category'),
        brand=data.get('brand'),
        model=data.get('model'),
        year=data.get('year', 2023),
        horsepower=data.get('horsepower', 45),
        condition=data.get('condition', 'Excellent'),
        fuel_type=data.get('fuel_type', 'Diesel'),
        description=data.get('description'),
        specifications=data.get('specifications', ''),
        hourly_rate=data.get('hourly_rate', 500),
        daily_rate=data.get('daily_rate', 3500),
        acre_rate=data.get('acre_rate', 1000),
        deposit=data.get('deposit', 1000),
        operator_available=data.get('operator_available', True),
        delivery_available=data.get('delivery_available', True),
        delivery_charge=data.get('delivery_charge', 200),
        location_text=data.get('location_text', 'Bengaluru, KA'),
        verification_status='Verified',
        status='Available'
    )
    db.session.add(eq)
    db.session.commit()

    img_url = data.get('image_url') or 'https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&q=80&w=800'
    db.session.add(EquipmentImage(equipment_id=eq.id, image_path=img_url))
    db.session.commit()

    return jsonify({'success': True, 'message': 'Equipment listed successfully', 'equipment_id': eq.id})

@app.route('/api/bookings', methods=['POST'])
def api_create_booking():
    if 'user_id' not in session or session.get('role') != 'farmer':
        return jsonify({'error': 'Only farmers can book equipment'}), 403
    data = request.json
    equipment_id = data.get('equipment_id')
    eq = Equipment.query.get_or_404(equipment_id)

    start_str = data.get('start_datetime')
    end_str = data.get('end_datetime')
    land_area = float(data.get('land_area', 2.0))

    overlapping = Booking.query.filter(
        Booking.equipment_id == equipment_id,
        Booking.status.in_(['CONFIRMED', 'ACTIVE', 'ACCEPTED', 'PENDING_OWNER']),
        Booking.start_datetime <= end_str,
        Booking.end_datetime >= start_str
    ).first()

    if overlapping:
        return jsonify({'error': 'This equipment is already booked or requested for the selected period.'}), 400

    unit_type = data.get('unit_type', 'hourly')
    if unit_type == 'daily':
        amount = eq.daily_rate * 1.0
    elif unit_type == 'acre':
        amount = eq.acre_rate * land_area
    else:
        amount = eq.hourly_rate * 8.0

    if data.get('delivery_required'):
        amount += eq.delivery_charge

    booking = Booking(
        equipment_id=eq.id,
        farmer_id=session['user_id'],
        owner_id=eq.owner_id,
        start_datetime=start_str,
        end_datetime=end_str,
        land_area=land_area,
        crop=data.get('crop', 'Paddy'),
        operation=data.get('operation', 'Land Preparation'),
        operator_required=data.get('operator_required', True),
        delivery_required=data.get('delivery_required', True),
        notes=data.get('notes', ''),
        amount=amount,
        status='PENDING_OWNER'
    )
    db.session.add(booking)
    db.session.commit()

    db.session.add(Notification(
        user_id=eq.owner_id, type='Booking',
        title='New Booking Request',
        message=f'New booking request for {eq.name} from {booking.farmer.name}.'
    ))
    db.session.commit()

    return jsonify({'success': True, 'message': 'Booking requested successfully', 'booking_id': booking.id, 'amount': amount})

@app.route('/api/bookings', methods=['GET'])
def api_get_bookings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    if user.role == 'farmer':
        bookings = Booking.query.filter_by(farmer_id=user.id).all()
    elif user.role == 'owner':
        bookings = Booking.query.filter_by(owner_id=user.id).all()
    else:
        bookings = Booking.query.all()

    result = []
    for b in bookings:
        result.append({
            'id': b.id,
            'equipment_name': b.equipment.name,
            'equipment_image': b.equipment.images[0].image_path if b.equipment.images else '',
            'farmer_name': b.farmer.name,
            'owner_name': b.owner.name,
            'start_datetime': b.start_datetime,
            'end_datetime': b.end_datetime,
            'land_area': b.land_area,
            'crop': b.crop,
            'operation': b.operation,
            'amount': b.amount,
            'status': b.status,
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(result)

@app.route('/api/bookings/<int:id>/accept', methods=['PUT'])
def api_accept_booking(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    b = Booking.query.get_or_404(id)
    if b.owner_id != session['user_id'] and session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    b.status = 'ACCEPTED'
    db.session.add(Notification(user_id=b.farmer_id, type='Booking', title='Booking Accepted', message=f'Your booking for {b.equipment.name} was accepted by owner. Please proceed to payment.'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking accepted'})

@app.route('/api/bookings/<int:id>/reject', methods=['PUT'])
def api_reject_booking(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    b = Booking.query.get_or_404(id)
    if b.owner_id != session['user_id'] and session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    b.status = 'REJECTED'
    db.session.add(Notification(user_id=b.farmer_id, type='Booking', title='Booking Rejected', message=f'Your booking for {b.equipment.name} was rejected by the owner.'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking rejected'})

@app.route('/api/bookings/<int:id>/complete', methods=['PUT'])
def api_complete_booking(id):
    b = Booking.query.get_or_404(id)
    b.status = 'COMPLETED'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking marked as completed'})

@app.route('/api/payments/simulate', methods=['POST'])
def api_simulate_payment():
    data = request.json
    booking_id = data.get('booking_id')
    b = Booking.query.get_or_404(booking_id)
    b.status = 'CONFIRMED'
    
    pay = Payment(booking_id=b.id, amount=b.amount, status='Completed', transaction_id=f'TXN{os.urandom(4).hex().upper()}')
    db.session.add(pay)
    db.session.add(Notification(user_id=b.owner_id, type='Payment', title='Payment Received', message=f'Payment of ₹{b.amount} received for booking #{b.id}.'))
    db.session.add(Notification(user_id=b.farmer_id, type='Payment', title='Booking Confirmed', message=f'Payment successful! Booking #{b.id} is now confirmed.'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Payment successful and booking confirmed!'})

@app.route('/api/advisor/recommend', methods=['POST'])
def api_advisor_recommend():
    data = request.json
    crop = data.get('crop', 'Paddy')
    operation = data.get('operation', 'Land Preparation')
    farm_size = float(data.get('farm_size', 5.0))

    recommendations = []
    if 'Plough' in operation or 'Land' in operation or 'Tilling' in operation:
        recommendations = [
            {'category': 'Tractors', 'reason': 'Essential for heavy traction and primary soil turning.', 'hp': '45 - 55 HP', 'unit': 'Per Acre', 'range': '₹1,000 - ₹1,400 / acre'},
            {'category': 'Rotavators', 'reason': 'Creates fine seedbed and pulverizes soil clods in single pass.', 'hp': '40 - 50 HP compatible', 'unit': 'Per Acre', 'range': '₹800 - ₹1,100 / acre'},
            {'category': 'Cultivators', 'reason': 'Deep soil loosening and weed eradication.', 'hp': '45 HP', 'unit': 'Per Hour', 'range': '₹500 - ₹700 / hour'}
        ]
    elif 'Harvest' in operation or 'Thresh' in operation:
        recommendations = [
            {'category': 'Harvesters', 'reason': 'Combines reaping, threshing, and cleaning into single efficient operation.', 'hp': '75 - 100+ HP', 'unit': 'Per Acre', 'range': '₹2,000 - ₹2,500 / acre'}
        ]
    elif 'Irrigat' in operation or 'Pump' in operation:
        recommendations = [
            {'category': 'Pumps', 'reason': 'High volume water discharge for timely irrigation.', 'hp': '5 - 10 HP', 'unit': 'Per Day', 'range': '₹1,200 - ₹1,800 / day'}
        ]
    else:
        recommendations = [
            {'category': 'Tractors', 'reason': 'General utility and hauling across farm operations.', 'hp': '45 HP', 'unit': 'Per Hour', 'range': '₹750 / hour'},
            {'category': 'Sprayers', 'reason': 'Uniform pesticide or nutrient application.', 'hp': 'Engine / Battery', 'unit': 'Per Acre', 'range': '₹400 / acre'}
        ]

    matched_equipment = []
    for rec in recommendations:
        eqs = Equipment.query.filter(Equipment.category.ilike(f"%{rec['category']}%"), Equipment.status == 'Available').limit(2).all()
        for eq in eqs:
            matched_equipment.append({
                'id': eq.id,
                'name': eq.name,
                'hourly_rate': eq.hourly_rate,
                'location': eq.location_text,
                'image': eq.images[0].image_path if eq.images else ''
            })

    return jsonify({
        'success': True,
        'crop': crop,
        'operation': operation,
        'farm_size': farm_size,
        'recommendations': recommendations,
        'matching_equipment': matched_equipment
    })

@app.route('/api/favorites', methods=['GET', 'POST'])
def api_favorites():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    if request.method == 'GET':
        favs = Favorite.query.filter_by(farmer_id=user_id).all()
        result = []
        for f in favs:
            eq = f.equipment
            result.append({
                'id': eq.id,
                'name': eq.name,
                'category': eq.category,
                'hourly_rate': eq.hourly_rate,
                'location_text': eq.location_text,
                'image': eq.images[0].image_path if eq.images else ''
            })
        return jsonify(result)
    elif request.method == 'POST':
        data = request.json
        eq_id = data.get('equipment_id')
        existing = Favorite.query.filter_by(farmer_id=user_id, equipment_id=eq_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'success': True, 'favorited': False, 'message': 'Removed from favorites'})
        else:
            db.session.add(Favorite(farmer_id=user_id, equipment_id=eq_id))
            db.session.commit()
            return jsonify({'success': True, 'favorited': True, 'message': 'Added to favorites'})

@app.route('/api/messages', methods=['GET', 'POST'])
def api_messages():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = session['user_id']
    if request.method == 'GET':
        msgs = Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).order_by(Message.created_at.desc()).all()
        result = []
        for m in msgs:
            result.append({
                'id': m.id,
                'sender_name': m.sender.name,
                'message': m.message,
                'created_at': m.created_at.strftime('%m-%d %H:%M')
            })
        return jsonify(result)
    elif request.method == 'POST':
        data = request.json
        receiver_id = data.get('receiver_id', 2)
        msg = Message(sender_id=user_id, receiver_id=receiver_id, message=data.get('message'))
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message sent'})

@app.route('/api/notifications', methods=['GET'])
def api_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    notifs = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all()
    return jsonify([{'id': n.id, 'title': n.title, 'message': n.message, 'read': n.read, 'created_at': n.created_at.strftime('%m-%d %H:%M')} for n in notifs])

@app.route('/api/reviews', methods=['POST'])
def api_reviews():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    booking_id = data.get('booking_id')
    b = Booking.query.get_or_404(booking_id)
    reviewee_id = b.owner_id if session['user_id'] == b.farmer_id else b.farmer_id
    
    rev = Review(
        booking_id=booking_id,
        reviewer_id=session['user_id'],
        reviewee_id=reviewee_id,
        rating=data.get('rating', 5),
        comment=data.get('comment', 'Great service!')
    )
    db.session.add(rev)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Review submitted successfully'})

@app.route('/api/disputes', methods=['GET', 'POST'])
def api_disputes():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if request.method == 'GET':
        disps = Dispute.query.all() if session.get('role') == 'admin' else Dispute.query.filter_by(raised_by=session['user_id']).all()
        return jsonify([{
            'id': d.id, 'booking_id': d.booking_id, 'reason': d.reason, 'description': d.description, 'status': d.status, 'created_at': d.created_at.strftime('%Y-%m-%d')
        } for d in disps])
    elif request.method == 'POST':
        data = request.json
        disp = Dispute(
            booking_id=data.get('booking_id'),
            raised_by=session['user_id'],
            reason=data.get('reason', 'Equipment Issue'),
            description=data.get('description', '')
        )
        db.session.add(disp)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dispute raised successfully'})

@app.route('/api/admin/dashboard', methods=['GET'])
def api_admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify({
        'total_users': User.query.count(),
        'total_farmers': User.query.filter_by(role='farmer').count(),
        'total_owners': User.query.filter_by(role='owner').count(),
        'total_equipment': Equipment.query.count(),
        'active_bookings': Booking.query.filter_by(status='CONFIRMED').count(),
        'completed_bookings': Booking.query.filter_by(status='COMPLETED').count(),
        'total_revenue': sum([p.amount for p in Payment.query.all()]),
        'open_disputes': Dispute.query.filter_by(status='OPEN').count()
    })

@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    users = User.query.all()
    return jsonify([{
        'id': u.id, 'name': u.name, 'email': u.email, 'phone': u.phone, 'role': u.role, 'state': u.state, 'is_verified': u.is_verified
    } for u in users])


# ==========================================
# FRONTEND HTML VIEW ROUTE
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')


# ==========================================
# TEMPLATE GENERATOR (templates/index.html)
# ==========================================

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriShare India — Agricultural Equipment Sharing Marketplace</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        agri: {
                            50: '#f0fdf4',
                            100: '#dcfce7',
                            600: '#16a34a',
                            700: '#15803d',
                            800: '#166534',
                            900: '#1b4d3e',
                            950: '#0f2922'
                        }
                    }
                }
            }
        }
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; }
        .hero-bg {
            background: linear-gradient(rgba(15, 41, 34, 0.85), rgba(15, 41, 34, 0.7)), url('https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&q=80&w=1600');
            background-size: cover;
            background-position: center;
        }
        .accordion-content { transition: max-height 0.3s ease-out; overflow: hidden; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col">

    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <div class="flex items-center space-x-3 cursor-pointer" onclick="router('home')">
                <div class="bg-agri-900 text-white p-2.5 rounded-xl shadow-md">
                    <i class="fa-solid fa-tractor text-xl"></i>
                </div>
                <div>
                    <span class="text-xl font-bold text-agri-900 tracking-tight block leading-none">AgriShare India</span>
                    <span class="text-[10px] font-semibold text-agri-700 tracking-widest uppercase block mt-1">Farm Equipment Marketplace</span>
                </div>
            </div>

            <nav class="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-700">
                <a href="#home" onclick="router('home')" class="hover:text-agri-800 transition">Home</a>
                <a href="#how-it-works" onclick="router('home'); scrollToSection('how-it-works')" class="hover:text-agri-800 transition">How it works</a>
                <a href="#farmers" onclick="router('home'); scrollToSection('farmers')" class="hover:text-agri-800 transition">For Farmers</a>
                <a href="#owners" onclick="router('home'); scrollToSection('owners')" class="hover:text-agri-800 transition">For Owners</a>
                <a href="#faq" onclick="router('home'); scrollToSection('faq')" class="hover:text-agri-800 transition">FAQ</a>
            </nav>

            <div class="flex items-center space-x-3" id="auth-nav-container">
                <button onclick="openModal('loginModal')" class="px-4 py-2 text-sm font-semibold text-agri-900 hover:text-agri-700 transition">
                    <i class="fa-regular fa-user mr-1.5"></i> Login
                </button>
                <button onclick="openModal('signupModal')" class="bg-agri-600 hover:bg-agri-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-sm transition flex items-center">
                    <i class="fa-solid fa-user-plus mr-1.5"></i> Sign Up
                </button>
            </div>
        </div>
    </header>

    <main id="app-container" class="flex-grow">
    </main>

    <footer class="bg-agri-950 text-slate-300 py-12 border-t border-slate-800 mt-auto">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                <div>
                    <div class="flex items-center space-x-3 mb-4">
                        <div class="bg-agri-600 text-white p-2 rounded-lg">
                            <i class="fa-solid fa-tractor"></i>
                        </div>
                        <span class="text-lg font-bold text-white">AgriShare India</span>
                    </div>
                    <p class="text-sm text-slate-400 mb-4">Connecting Indian farmers with equipment owners to make machinery discovery, booking and management simple and accessible.</p>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Quick Links</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="#" onclick="router('marketplace')" class="hover:text-white transition">Browse Marketplace</a></li>
                        <li><a href="#" onclick="router('advisor')" class="hover:text-white transition">Farm Equipment Advisor</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Policies & Support</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="#" class="hover:text-white transition">Privacy Policy</a></li>
                        <li><a href="#" class="hover:text-white transition">Terms of Service</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Demo Credentials</h4>
                    <p class="text-xs text-slate-400 mb-2">Farmer: farmer@demo.local / farmer123</p>
                    <p class="text-xs text-slate-400 mb-2">Owner: owner@demo.local / owner123</p>
                    <p class="text-xs text-slate-400">Admin: admin@demo.local / admin123</p>
                </div>
            </div>
            <div class="border-t border-slate-800 pt-6 text-xs text-slate-500">
                <p>&copy; 2026 AgriShare India. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <div id="loginModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <button onclick="closeModal('loginModal')" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            <h3 class="text-2xl font-bold text-agri-900 mb-1">Welcome Back</h3>
            <form onsubmit="handleLogin(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Email Address</label>
                    <input type="email" id="loginEmail" required class="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm" placeholder="farmer@demo.local">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Password</label>
                    <input type="password" id="loginPassword" required class="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm" placeholder="••••••••">
                </div>
                <button type="submit" class="w-full bg-agri-600 hover:bg-agri-700 text-white font-semibold py-3 rounded-xl transition">Login Securely</button>
            </form>
        </div>
    </div>

    <div id="signupModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
            <button onclick="closeModal('signupModal')" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            <h3 class="text-2xl font-bold text-agri-900 mb-1">Join AgriShare India</h3>
            <form onsubmit="handleSignup(event)" class="space-y-3">
                <input type="hidden" id="signupRole" value="farmer">
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-[11px] font-semibold text-slate-700 uppercase mb-1">Full Name</label>
                        <input type="text" id="signupName" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm" placeholder="Rajesh Kumar">
                    </div>
                    <div>
                        <label class="block text-[11px] font-semibold text-slate-700 uppercase mb-1">Mobile Number</label>
                        <input type="text" id="signupPhone" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm" placeholder="9876543210">
                    </div>
                </div>
                <div>
                    <label class="block text-[11px] font-semibold text-slate-700 uppercase mb-1">Email Address</label>
                    <input type="email" id="signupEmail" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm" placeholder="rajesh@demo.local">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-[11px] font-semibold text-slate-700 uppercase mb-1">Password</label>
                        <input type="password" id="signupPassword" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm" placeholder="••••••••">
                    </div>
                    <div>
                        <label class="block text-[11px] font-semibold text-slate-700 uppercase mb-1">District</label>
                        <input type="text" id="signupDistrict" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm" placeholder="Mandya, KA">
                    </div>
                </div>
                <button type="submit" class="w-full bg-agri-600 hover:bg-agri-700 text-white font-semibold py-3 rounded-xl transition mt-2">Create Account</button>
            </form>
        </div>
    </div>

    <script>
        let currentUser = null;
        async function checkAuth() {
            try {
                const res = await fetch('/api/auth/me');
                const data = await res.json();
                currentUser = data.user;
                updateAuthNav();
            } catch (e) { console.error(e); }
        }
        function updateAuthNav() {
            const container = document.getElementById('auth-nav-container');
            if (currentUser) {
                let dashUrl = currentUser.role === 'farmer' ? "router('farmer-dashboard')" : (currentUser.role === 'owner' ? "router('owner-dashboard')" : "router('admin-dashboard')");
                container.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <button onclick="${dashUrl}" class="bg-agri-50 text-agri-900 px-4 py-2 rounded-xl text-sm font-bold border border-agri-200 flex items-center space-x-2">
                            <i class="fa-solid fa-gauge-high"></i>
                            <span>${currentUser.name} (${currentUser.role.toUpperCase()})</span>
                        </button>
                        <button onclick="logout()" class="text-slate-500 hover:text-red-600 px-2 py-1 text-sm"><i class="fa-solid fa-right-from-bracket"></i></button>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <button onclick="openModal('loginModal')" class="px-4 py-2 text-sm font-semibold text-agri-900 hover:text-agri-700 transition">
                        <i class="fa-regular fa-user mr-1.5"></i> Login
                    </button>
                    <button onclick="openModal('signupModal')" class="bg-agri-600 hover:bg-agri-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-sm transition flex items-center">
                        <i class="fa-solid fa-user-plus mr-1.5"></i> Sign Up
                    </button>
                `;
            }
        }
        function openModal(id) { document.getElementById(id).classList.remove('hidden'); }
        function closeModal(id) { document.getElementById(id).classList.add('hidden'); }
        async function handleLogin(e) {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            const data = await res.json();
            if(res.ok) {
                currentUser = data.user;
                closeModal('loginModal');
                updateAuthNav();
                if(currentUser.role === 'farmer') router('farmer-dashboard');
                else if(currentUser.role === 'owner') router('owner-dashboard');
                else router('admin-dashboard');
            } else { alert(data.error || 'Login failed'); }
        }
        async function handleSignup(e) {
            e.preventDefault();
            const payload = {
                name: document.getElementById('signupName').value,
                phone: document.getElementById('signupPhone').value,
                email: document.getElementById('signupEmail').value,
                password: document.getElementById('signupPassword').value,
                district: document.getElementById('signupDistrict').value,
                role: document.getElementById('signupRole').value,
                state: 'Karnataka', village: 'Rural', city: 'Bengaluru', pincode: '560001'
            };
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if(res.ok) {
                currentUser = data.user;
                closeModal('signupModal');
                updateAuthNav();
                if(currentUser.role === 'farmer') router('farmer-dashboard');
                else router('owner-dashboard');
            } else { alert(data.error || 'Signup failed'); }
        }
        async function logout() {
            await fetch('/api/auth/logout', {method: 'POST'});
            currentUser = null;
            updateAuthNav();
            router('home');
        }
        function scrollToSection(id) {
            const el = document.getElementById(id);
            if(el) el.scrollIntoView({behavior: 'smooth'});
        }
        function router(view, param) {
            window.scrollTo(0,0);
            const container = document.getElementById('app-container');
            if(view === 'home') {
                container.innerHTML = renderHome();
            } else if(view === 'marketplace') {
                container.innerHTML = renderMarketplace();
                loadMarketplaceEquipment(param);
            } else if(view === 'equipment-detail') {
                container.innerHTML = renderEquipmentDetail(param);
                loadEquipmentDetailData(param);
            } else if(view === 'farmer-dashboard') {
                container.innerHTML = renderFarmerDashboard();
                loadFarmerDashboardData();
            } else if(view === 'owner-dashboard') {
                container.innerHTML = renderOwnerDashboard();
                loadOwnerDashboardData();
            } else if(view === 'admin-dashboard') {
                container.innerHTML = renderAdminDashboard();
                loadAdminDashboardData();
            } else if(view === 'advisor') {
                container.innerHTML = renderAdvisor();
            }
        }
        function renderHome() {
            return `
                <section class="hero-bg text-white py-20 px-4 sm:px-6 lg:px-8">
                    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                        <div class="lg:col-span-7">
                            <span class="text-xs uppercase tracking-widest font-semibold text-agri-100 bg-agri-800/80 px-3 py-1 rounded-md inline-block mb-4">AGRICULTURAL EQUIPMENT SHARING</span>
                            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight mb-6">
                                <span class="text-white block">Share machines.</span>
                                <span class="text-agri-400 block">Grow more.</span>
                            </h1>
                            <p class="text-lg text-slate-200 mb-8 max-w-xl">
                                Find the machinery you need. Rent out the machinery you own. AgriShare India connects farmers with equipment owners, making agricultural machinery easier to discover, book and manage.
                            </p>
                            <div class="flex flex-wrap gap-4 mb-8">
                                <button onclick="router('marketplace')" class="bg-agri-600 hover:bg-agri-700 text-white font-bold px-8 py-4 rounded-xl shadow-lg transition flex items-center">
                                    <i class="fa-solid fa-magnifying-glass mr-2"></i> Find Equipment
                                </button>
                                <button onclick="openModal('signupModal')" class="bg-white hover:bg-slate-100 text-agri-900 border-2 border-agri-600 font-bold px-8 py-4 rounded-xl shadow-sm transition flex items-center">
                                    <i class="fa-solid fa-tractor mr-2"></i> List Your Equipment
                                </button>
                            </div>
                        </div>
                    </div>
                </section>
                <div class="py-12 bg-white text-center">
                    <h2 class="text-2xl font-bold text-agri-900 mb-4">Explore AgriShare Marketplace</h2>
                    <button onclick="router('marketplace')" class="bg-agri-600 text-white px-6 py-3 rounded-xl font-bold">Browse All Equipment</button>
                </div>
            `;
        }
        function renderMarketplace() {
            return `
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                        <div>
                            <h1 class="text-3xl font-extrabold text-agri-900">Equipment Marketplace</h1>
                            <p class="text-sm text-slate-600 mt-1">Discover verified agricultural machinery available for rent near you.</p>
                        </div>
                        <div class="flex items-center space-x-3 w-full md:w-auto">
                            <input type="text" id="searchInput" onkeyup="filterEquipment()" placeholder="Search equipment..." class="px-4 py-2.5 rounded-xl border border-slate-300 text-sm w-full md:w-72">
                            <select id="categoryFilter" onchange="filterEquipment()" class="px-4 py-2.5 rounded-xl border border-slate-300 text-sm bg-white">
                                <option value="All">All Categories</option>
                                <option value="Tractors">Tractors</option>
                                <option value="Rotavators">Rotavators</option>
                                <option value="Harvesters">Harvesters</option>
                                <option value="Pumps">Pumps</option>
                            </select>
                        </div>
                    </div>
                    <div id="equipmentGrid" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6"></div>
                </div>
            `;
        }
        let allEquipmentCache = [];
        async function loadMarketplaceEquipment(preselectCategory) {
            try {
                const res = await fetch('/api/equipment');
                allEquipmentCache = await res.json();
                if(preselectCategory) {
                    const sel = document.getElementById('categoryFilter');
                    if(sel) sel.value = preselectCategory;
                }
                filterEquipment();
            } catch(e) { console.error(e); }
        }
        function filterEquipment() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const cat = document.getElementById('categoryFilter').value;
            const grid = document.getElementById('equipmentGrid');
            const filtered = allEquipmentCache.filter(eq => {
                const matchesCat = (cat === 'All' || eq.category.toLowerCase().includes(cat.toLowerCase()));
                const matchesSearch = eq.name.toLowerCase().includes(search) || eq.brand.toLowerCase().includes(search);
                return matchesCat && matchesSearch;
            });
            if(filtered.length === 0) {
                grid.innerHTML = `<div class="col-span-full py-12 text-center text-slate-500 bg-white rounded-3xl border border-slate-200">No equipment found matching criteria.</div>`;
                return;
            }
            grid.innerHTML = filtered.map(eq => `
                <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="relative h-48 bg-slate-100">
                            <img src="${eq.image}" class="w-full h-full object-cover">
                            <span class="absolute top-3 left-3 bg-agri-900 text-white text-[10px] font-bold px-2.5 py-1 rounded-md uppercase">${eq.category}</span>
                        </div>
                        <div class="p-5">
                            <h3 class="font-bold text-slate-900 text-base mb-1">${eq.name}</h3>
                            <p class="text-xs text-slate-500 mb-3"><i class="fa-solid fa-location-dot mr-1 text-agri-600"></i>${eq.location_text}</p>
                            <span class="text-lg font-extrabold text-agri-900">₹${eq.hourly_rate}</span><span class="text-xs text-slate-500"> / hour</span>
                        </div>
                    </div>
                    <div class="p-5 pt-0 grid grid-cols-2 gap-2">
                        <button onclick="router('equipment-detail', ${eq.id})" class="bg-slate-100 text-slate-800 font-semibold py-2.5 rounded-xl text-xs">View Details</button>
                        <button onclick="router('equipment-detail', ${eq.id})" class="bg-agri-600 text-white font-semibold py-2.5 rounded-xl text-xs">Book Now</button>
                    </div>
                </div>
            `).join('');
        }
        function renderEquipmentDetail(id) { return `<div class="max-w-7xl mx-auto px-4 py-8" id="equipmentDetailContainer"><div class="animate-pulse bg-white p-8 rounded-3xl h-96">Loading details...</div></div>`; }
        async function loadEquipmentDetailData(id) {
            const res = await fetch(`/api/equipment/${id}`);
            const eq = await res.json();
            document.getElementById('equipmentDetailContainer').innerHTML = `
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div class="lg:col-span-2 bg-white p-6 rounded-3xl border border-slate-200">
                        <img src="${eq.images[0]}" class="w-full h-80 object-cover rounded-2xl mb-4">
                        <h1 class="text-3xl font-extrabold text-agri-900 mb-2">${eq.name}</h1>
                        <p class="text-sm text-slate-700">${eq.description}</p>
                    </div>
                    <div>
                        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-lg sticky top-28">
                            <span class="text-2xl font-extrabold text-agri-900">₹${eq.hourly_rate}</span><span class="text-xs text-slate-500"> / hour</span>
                            <form onsubmit="handleBookingSubmit(event, ${eq.id})" class="space-y-4 mt-4">
                                <div><label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Start Date & Time</label><input type="datetime-local" id="bookStart" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm"></div>
                                <div><label class="block text-xs font-semibold text-slate-700 uppercase mb-1">End Date & Time</label><input type="datetime-local" id="bookEnd" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm"></div>
                                <button type="submit" class="w-full bg-agri-600 text-white font-bold py-3.5 rounded-xl">Request Booking</button>
                            </form>
                        </div>
                    </div>
                </div>
            `;
        }
        async function handleBookingSubmit(e, equipmentId) {
            e.preventDefault();
            if(!currentUser) { alert('Please login first.'); openModal('loginModal'); return; }
            const payload = {
                equipment_id: equipmentId,
                start_datetime: document.getElementById('bookStart').value.replace('T', ' '),
                end_datetime: document.getElementById('bookEnd').value.replace('T', ' '),
                land_area: 2.0, crop: 'Paddy', operation: 'Ploughing'
            };
            const res = await fetch('/api/bookings', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            const data = await res.json();
            if(res.ok) { alert('Booking requested successfully!'); router('farmer-dashboard'); } else { alert(data.error); }
        }
        function renderFarmerDashboard() { return `<div class="max-w-7xl mx-auto px-4 py-8" id="farmerContentArea">Loading...</div>`; }
        async function loadFarmerDashboardData() {
            const res = await fetch('/api/bookings');
            const bookings = await res.json();
            document.getElementById('farmerContentArea').innerHTML = `
                <div class="bg-white p-6 rounded-3xl border border-slate-200">
                    <h3 class="font-bold text-agri-900 text-lg mb-4">My Bookings</h3>
                    ${bookings.map(b => `<div class="bg-slate-50 p-4 rounded-xl mb-3 flex justify-between"><span>${b.equipment_name} (${b.status})</span><span class="font-bold">₹${b.amount}</span></div>`).join('')}
                </div>
            `;
        }
        function renderOwnerDashboard() { return `<div class="max-w-7xl mx-auto px-4 py-8" id="ownerContentArea">Loading owner panel...</div>`; }
        async function loadOwnerDashboardData() {
            const res = await fetch('/api/bookings');
            const bookings = await res.json();
            document.getElementById('ownerContentArea').innerHTML = `
                <div class="bg-white p-6 rounded-3xl border border-slate-200">
                    <h3 class="font-bold text-agri-900 text-lg mb-4">Owner Requests</h3>
                    ${bookings.map(b => `<div class="bg-slate-50 p-4 rounded-xl mb-3 flex justify-between"><span>${b.equipment_name} -${b.status}</span></div>`).join('')}
                </div>
            `;
        }
        function renderAdminDashboard() { return `<div class="max-w-7xl mx-auto px-4 py-8" id="adminContentArea">Admin Panel</div>`; }
        async function loadAdminDashboardData() {}
        function renderAdvisor() { return `<div class="max-w-4xl mx-auto px-4 py-12 text-center"><h1 class="text-3xl font-bold">Equipment Advisor</h1></div>`; }
        window.onload = function() { checkAuth(); router('home'); }
    </script>
</body>
</html>
"""

with open(os.path.join(os.path.dirname(__file__), 'templates', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(INDEX_HTML)

# ==========================================
# CLI SEED COMMAND / RUNNER
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        seed_database()
        print("Database seeded successfully with realistic Indian agricultural demo data!")
    app.run(host='0.0.0.0', port=5000, debug=True)
