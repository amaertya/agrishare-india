import os
import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agrishare-india-secret-key-2026'

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
    role = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    village = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, default=2022)
    horsepower = db.Column(db.Integer, default=45)
    condition = db.Column(db.String(30), default='Excellent')
    fuel_type = db.Column(db.String(30), default='Diesel')
    description = db.Column(db.Text, nullable=False)
    hourly_rate = db.Column(db.Float, default=750.0)
    daily_rate = db.Column(db.Float, default=5000.0)
    acre_rate = db.Column(db.Float, default=1200.0)
    deposit = db.Column(db.Float, default=2000.0)
    location_text = db.Column(db.String(100), default='Bengaluru Rural, KA')
    verification_status = db.Column(db.String(20), default='Verified')
    status = db.Column(db.String(20), default='Available')
    owner = db.relationship('User', backref='equipment_listings')

class EquipmentImage(db.Model):
    __tablename__ = 'equipment_images'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    equipment = db.relationship('Equipment', backref='images')

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_datetime = db.Column(db.String(30), nullable=False)
    end_datetime = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='PENDING_OWNER')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    equipment = db.relationship('Equipment', backref='bookings')

# ==========================================
# SEED SCRIPT
# ==========================================

def seed_database():
    db.drop_all()
    db.create_all()

    u_admin = User(name='Admin Officer', email='admin@demo.local', phone='9876543210', password_hash=generate_password_hash('admin123'), role='admin', state='Karnataka', district='Bengaluru', village='Hebbal', city='Bengaluru', pincode='560024', is_verified=True)
    u_farmer1 = User(name='Ramesh Gowda', email='farmer@demo.local', phone='9876543211', password_hash=generate_password_hash('farmer123'), role='farmer', state='Karnataka', district='Mandya', village='Srirangapatna', city='Mandya', pincode='571438', is_verified=True)
    u_owner1 = User(name='Suresh Reddy', email='owner@demo.local', phone='9876543212', password_hash=generate_password_hash('owner123'), role='owner', state='Karnataka', district='Bengaluru Rural', village='Devanahalli', city='Bengaluru', pincode='562110', is_verified=True)

    db.session.add_all([u_admin, u_farmer1, u_owner1])
    db.session.commit()

    eq1 = Equipment(owner_id=u_owner1.id, name='Mahindra 575 DI Tractor', category='Tractors', brand='Mahindra', model='575 DI', year=2023, horsepower=45, condition='Excellent', fuel_type='Diesel', description='Reliable 45HP tractor equipped with heavy-duty dual clutch.', hourly_rate=850.0, daily_rate=5500.0, acre_rate=1200.0, location_text='Devanahalli, Bengaluru Rural', verification_status='Verified', status='Available')
    eq2 = Equipment(owner_id=u_owner1.id, name='Shaktiman Rotary Tiller (Rotavator)', category='Rotavators', brand='Shaktiman', model='Regular Smart 6ft', year=2023, horsepower=50, condition='Like New', fuel_type='PTO Driven', description='High performance rotavator for fine seedbed preparation.', hourly_rate=600.0, daily_rate=3800.0, acre_rate=900.0, location_text='Devanahalli, Bengaluru Rural', verification_status='Verified', status='Available')
    eq3 = Equipment(owner_id=u_owner1.id, name='John Deere W70 Grain Harvester', category='Harvesters', brand='John Deere', model='W70 Multi-Crop', year=2024, horsepower=100, condition='Excellent', fuel_type='Diesel', description='Self-propelled multi-crop harvester.', hourly_rate=2500.0, daily_rate=18000.0, acre_rate=2200.0, location_text='Devanahalli, Bengaluru Rural', verification_status='Verified', status='Available')

    db.session.add_all([eq1, eq2, eq3])
    db.session.commit()

    db.session.add(EquipmentImage(equipment_id=eq1.id, image_path='https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&q=80&w=800'))
    db.session.add(EquipmentImage(equipment_id=eq2.id, image_path='https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?auto=format&fit=crop&q=80&w=800'))
    db.session.add(EquipmentImage(equipment_id=eq3.id, image_path='https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&q=80&w=800'))
    db.session.commit()


# ==========================================
# REST API ROUTES
# ==========================================

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({'error': 'Invalid email or password'}), 401
    session['user_id'] = user.id
    session['role'] = user.role
    return jsonify({'success': True, 'user': {'id': user.id, 'name': user.name, 'role': user.role, 'email': user.email}})

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({'user': None})
    user = User.query.get(session['user_id'])
    return jsonify({'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}})

@app.route('/api/equipment', methods=['GET'])
def api_get_equipment():
    category = request.args.get('category')
    search = request.args.get('search')
    query = Equipment.query.filter_by(status='Available')
    if category and category != 'All':
        query = query.filter(Equipment.category.ilike(f'%{category}%'))
    if search:
        query = query.filter(Equipment.name.ilike(f'%{search}%') | Equipment.brand.ilike(f'%{search}%'))
    
    equipments = query.all()
    result = []
    for eq in equipments:
        img = eq.images[0].image_path if eq.images else 'https://placehold.co/600x400/1b4d3e/ffffff?text=Equipment'
        result.append({
            'id': eq.id, 'name': eq.name, 'category': eq.category, 'brand': eq.brand,
            'hourly_rate': eq.hourly_rate, 'location_text': eq.location_text, 'image': img
        })
    return jsonify(result)

@app.route('/api/equipment/<int:id>', methods=['GET'])
def api_get_equipment_detail(id):
    eq = Equipment.query.get_or_404(id)
    images = [img.image_path for img in eq.images]
    if not images:
        images = ['https://placehold.co/800x600/1b4d3e/ffffff?text=Equipment']
    return jsonify({
        'id': eq.id, 'name': eq.name, 'category': eq.category, 'brand': eq.brand,
        'description': eq.description, 'hourly_rate': eq.hourly_rate, 'images': images,
        'owner': {'name': eq.owner.name, 'phone': eq.owner.phone}
    })

@app.route('/api/bookings', methods=['POST', 'GET'])
def api_bookings():
    if request.method == 'POST':
        if 'user_id' not in session:
            return jsonify({'error': 'Please login first'}), 401
        data = request.json
        eq = Equipment.query.get_or_404(data.get('equipment_id'))
        booking = Booking(
            equipment_id=eq.id, farmer_id=session['user_id'], owner_id=eq.owner_id,
            start_datetime=data.get('start_datetime'), end_datetime=data.get('end_datetime'),
            amount=eq.hourly_rate * 8.0, status='PENDING_OWNER'
        )
        db.session.add(booking)
        db.session.commit()
        return jsonify({'success': True, 'booking_id': booking.id})
    else:
        if 'user_id' not in session:
            return jsonify([])
        user_id = session['user_id']
        bookings = Booking.query.filter((Booking.farmer_id == user_id) | (Booking.owner_id == user_id)).all()
        return jsonify([{
            'id': b.id, 'equipment_name': b.equipment.name, 'amount': b.amount, 'status': b.status
        } for b in bookings])

@app.route('/api/advisor/recommend', methods=['POST'])
def api_advisor_recommend():
    data = request.json
    crop = data.get('crop', 'Paddy')
    operation = data.get('operation', 'Land Preparation')
    
    recommendations = []
    if 'Land' in operation or 'Plough' in operation:
        recommendations = [
            {'category': 'Tractors', 'reason': 'Essential for heavy traction and primary soil turning.', 'hp': '45 - 55 HP', 'range': '₹1,000 - ₹1,400 / acre'},
            {'category': 'Rotavators', 'reason': 'Creates fine seedbed and pulverizes soil clods.', 'hp': '40 - 50 HP', 'range': '₹800 - ₹1,100 / acre'}
        ]
    elif 'Harvest' in operation:
        recommendations = [
            {'category': 'Harvesters', 'reason': 'Combines reaping and threshing into one efficient step.', 'hp': '75 - 100+ HP', 'range': '₹2,000 - ₹2,500 / acre'}
        ]
    else:
        recommendations = [
            {'category': 'Tractors', 'reason': 'General utility across farm operations.', 'hp': '45 HP', 'range': '₹750 / hour'}
        ]
    return jsonify({'success': True, 'crop': crop, 'operation': operation, 'recommendations': recommendations})


# ==========================================
# FRONTEND HTML VIEW ROUTE
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')


# ==========================================
# TEMPLATES INDEX.HTML (Exact Matching UI)
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
                            50: '#f0fdf4', 100: '#dcfce7', 600: '#16a34a', 700: '#15803d', 800: '#166534', 900: '#1b4d3e', 950: '#0f2922'
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
            background: linear-gradient(rgba(15, 41, 34, 0.88), rgba(15, 41, 34, 0.78)), url('https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&q=80&w=1600');
            background-size: cover; background-position: center;
        }
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
                <a href="#" onclick="router('home')" class="hover:text-agri-800 transition">Home</a>
                <a href="#" onclick="router('marketplace')" class="hover:text-agri-800 transition">Browse Marketplace</a>
                <a href="#" onclick="router('advisor')" class="hover:text-agri-800 transition">Farm Equipment Advisor</a>
                <a href="#how-it-works" onclick="router('home'); scrollToSection('how-it-works')" class="hover:text-agri-800 transition">How it works</a>
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
                        <div class="bg-agri-600 text-white p-2 rounded-lg"><i class="fa-solid fa-tractor"></i></div>
                        <span class="text-lg font-bold text-white">AgriShare India</span>
                    </div>
                    <p class="text-sm text-slate-400 mb-4">Connecting Indian farmers with equipment owners to make machinery discovery, booking and management simple and accessible.</p>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Quick Links</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="#" onclick="router('marketplace')" class="hover:text-white transition">Browse Marketplace</a></li>
                        <li><a href="#" onclick="router('advisor')" class="hover:text-white transition">Farm Equipment Advisor</a></li>
                        <li><a href="#" onclick="openModal('loginModal')" class="hover:text-white transition">Farmer Login</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Policies & Support</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="#" class="hover:text-white transition">Privacy Policy</a></li>
                        <li><a href="#" class="hover:text-white transition">Terms of Service</a></li>
                        <li><a href="#" class="hover:text-white transition">Safety Guidelines</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Demo Credentials</h4>
                    <p class="text-xs text-slate-400 mb-2">Farmer: farmer@demo.local / farmer123</p>
                    <p class="text-xs text-slate-400">Owner: owner@demo.local / owner123</p>
                </div>
            </div>
            <div class="border-t border-slate-800 pt-6 flex flex-col md:flex-row items-center justify-between text-xs text-slate-500">
                <p>&copy; 2026 AgriShare India. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <!-- Modals -->
    <div id="loginModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <button onclick="closeModal('loginModal')" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            <h3 class="text-2xl font-bold text-agri-900 mb-1">Welcome Back</h3>
            <form onsubmit="handleLogin(event)" class="space-y-4 mt-4">
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
            <form onsubmit="closeModal('signupModal')" class="space-y-3 mt-4">
                <div>
                    <label class="block text-[11px] font-semibold text-slate-700 uppercase mb-1">Full Name</label>
                    <input type="text" required class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-sm" placeholder="Rajesh Kumar">
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
                container.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <span class="bg-agri-50 text-agri-900 px-4 py-2 rounded-xl text-sm font-bold border border-agri-200">
                            ${currentUser.name} (${currentUser.role.toUpperCase()})
                        </span>
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
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            const data = await res.json();
            if(res.ok) {
                currentUser = data.user;
                closeModal('loginModal');
                updateAuthNav();
                router('home');
            } else { alert(data.error || 'Login failed'); }
        }
        async function logout() {
            await fetch('/api/auth/logout', {method: 'POST'});
            currentUser = null;
            updateAuthNav();
            router('home');
        }
        function toggleFaq(button) {
            const content = button.nextElementSibling;
            const icon = button.querySelector('i');
            content.classList.toggle('hidden');
            icon.classList.toggle('rotate-180');
        }
        function scrollToSection(id) {
            const el = document.getElementById(id);
            if(el) el.scrollIntoView({behavior: 'smooth'});
        }

        // Router View Controller
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
                                Find the machinery you need. Rent out the machinery you own. AgriShare India connects farmers with equipment owners seamlessly.
                            </p>
                            <div class="flex flex-wrap gap-4 mb-8">
                                <button onclick="router('marketplace')" class="bg-agri-600 hover:bg-agri-700 text-white font-bold px-8 py-4 rounded-xl shadow-lg transition flex items-center">
                                    <i class="fa-solid fa-magnifying-glass mr-2"></i> Find Equipment
                                </button>
                                <button onclick="router('advisor')" class="bg-white hover:bg-slate-100 text-agri-900 border-2 border-agri-600 font-bold px-8 py-4 rounded-xl shadow-sm transition flex items-center">
                                    <i class="fa-solid fa-robot mr-2"></i> Try Farm Advisor
                                </button>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Top Feature Cards -->
                <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                        <div class="bg-agri-50/60 p-8 rounded-3xl border border-agri-100 shadow-sm flex items-center justify-between">
                            <div>
                                <span class="text-xs font-bold text-agri-700 uppercase tracking-wider block mb-1">SMART RECOMMENDATIONS</span>
                                <h2 class="text-2xl font-extrabold text-agri-900 mb-2">Farm Equipment Advisor</h2>
                                <p class="text-sm text-slate-600 mb-6 max-w-sm">Get personalized machinery recommendations based on crop, soil and farm size.</p>
                                <button onclick="router('advisor')" class="bg-agri-600 hover:bg-agri-700 text-white font-bold px-5 py-3 rounded-xl transition flex items-center text-sm shadow-sm">
                                    Try Farm Advisor <i class="fa-solid fa-arrow-right ml-2"></i>
                                </button>
                            </div>
                            <div class="hidden sm:flex items-center justify-center bg-agri-100 p-6 rounded-2xl text-agri-600">
                                <i class="fa-solid fa-robot text-5xl"></i>
                            </div>
                        </div>

                        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex items-center justify-between">
                            <div>
                                <span class="text-xs font-bold text-agri-700 uppercase tracking-wider block mb-1">TRUST & SAFETY</span>
                                <h2 class="text-2xl font-extrabold text-agri-900 mb-2">Why Choose AgriShare?</h2>
                                <p class="text-sm text-slate-600 mb-6 max-w-sm">Verified equipment, secure payment records, and trusted owner profiles.</p>
                                <div class="flex items-center space-x-6 text-sm font-semibold text-agri-800">
                                    <span><i class="fa-solid fa-check mr-1 text-agri-600"></i> Verified</span>
                                    <span><i class="fa-solid fa-lock mr-1 text-agri-600"></i> Secure</span>
                                    <span><i class="fa-solid fa-star mr-1 text-agri-600"></i> Rated</span>
                                </div>
                            </div>
                            <div class="hidden sm:flex items-center justify-center bg-slate-100 p-6 rounded-2xl text-slate-400">
                                <i class="fa-solid fa-shield-halved text-5xl"></i>
                            </div>
                        </div>
                    </div>

                    <!-- 3 Column Cards -->
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
                        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div>
                                <span class="text-xs font-bold text-agri-700 uppercase tracking-wider block mb-1">FOR FARMERS</span>
                                <h3 class="text-xl font-extrabold text-agri-900 mb-2">Need a machine for your next farming operation?</h3>
                                <p class="text-xs text-slate-600 mb-6">Access a wide range of agricultural machinery without the high cost of ownership. Compare, book and manage everything in one place.</p>
                                <ul class="space-y-3 text-xs font-medium text-slate-700 mb-8">
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Find tractors and implements</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Compare rental prices</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Check availability and distance</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Communicate with owners</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Manage bookings and payments</li>
                                </ul>
                            </div>
                            <button onclick="router('marketplace')" class="bg-agri-900 hover:bg-agri-950 text-white font-bold px-6 py-3.5 rounded-xl text-xs transition flex items-center justify-center">
                                Explore Equipment <i class="fa-solid fa-arrow-right ml-2"></i>
                            </button>
                        </div>

                        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div>
                                <span class="text-xs font-bold text-agri-700 uppercase tracking-wider block mb-1">FOR EQUIPMENT OWNERS</span>
                                <h3 class="text-xl font-extrabold text-agri-900 mb-2">Have machinery that isn't being used often?</h3>
                                <p class="text-xs text-slate-600 mb-6">List your equipment, set your price and availability, and start earning. Your machinery can work harder and generate income.</p>
                                <ul class="space-y-3 text-xs font-medium text-slate-700 mb-8">
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Create equipment listings</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Set your rental price</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Control availability</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Receive booking requests</li>
                                    <li class="flex items-center"><i class="fa-solid fa-check text-agri-600 mr-2.5"></i> Track earnings and performance</li>
                                </ul>
                            </div>
                            <button onclick="openModal('signupModal')" class="bg-agri-600 hover:bg-agri-700 text-white font-bold px-6 py-3.5 rounded-xl text-xs transition flex items-center justify-center">
                                List Your Equipment <i class="fa-solid fa-arrow-right ml-2"></i>
                            </button>
                        </div>

                        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div>
                                <span class="text-xs font-bold text-agri-700 uppercase tracking-wider block mb-1">MARKETPLACE</span>
                                <h3 class="text-xl font-extrabold text-agri-900 mb-2">Browse Our Marketplace</h3>
                                <p class="text-xs text-slate-600 mb-6">Find the right equipment for your needs across 12+ categories.</p>
                                <div class="grid grid-cols-2 gap-3 mb-8">
                                    <div onclick="router('marketplace', 'Tractors')" class="p-3 bg-slate-50 border border-slate-200 rounded-2xl text-center cursor-pointer hover:bg-agri-50 transition">
                                        <i class="fa-solid fa-tractor text-agri-800 text-lg block mb-1"></i>
                                        <span class="text-xs font-bold text-slate-800">Tractors</span>
                                    </div>
                                    <div onclick="router('marketplace', 'Rotavators')" class="p-3 bg-slate-50 border border-slate-200 rounded-2xl text-center cursor-pointer hover:bg-agri-50 transition">
                                        <i class="fa-solid fa-seedling text-agri-800 text-lg block mb-1"></i>
                                        <span class="text-xs font-bold text-slate-800">Rotavators</span>
                                    </div>
                                    <div onclick="router('marketplace', 'Harvesters')" class="p-3 bg-slate-50 border border-slate-200 rounded-2xl text-center cursor-pointer hover:bg-agri-50 transition">
                                        <i class="fa-solid fa-wheat-awn text-agri-800 text-lg block mb-1"></i>
                                        <span class="text-xs font-bold text-slate-800">Harvesters</span>
                                    </div>
                                    <div onclick="router('marketplace', 'Pumps')" class="p-3 bg-slate-50 border border-slate-200 rounded-2xl text-center cursor-pointer hover:bg-agri-50 transition">
                                        <i class="fa-solid fa-water text-agri-800 text-lg block mb-1"></i>
                                        <span class="text-xs font-bold text-slate-800">Pumps</span>
                                    </div>
                                </div>
                            </div>
                            <button onclick="router('marketplace')" class="bg-agri-50 hover:bg-agri-100 text-agri-900 font-bold px-6 py-3.5 rounded-xl text-xs border border-agri-200 transition flex items-center justify-center">
                                Browse All Equipment <i class="fa-solid fa-arrow-right ml-2"></i>
                            </button>
                        </div>
                    </div>
                </section>

                <!-- 5 Step How It Works Section -->
                <section id="how-it-works" class="py-16 bg-white border-t border-slate-200">
                    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                        <span class="text-xs font-bold text-agri-700 uppercase tracking-widest bg-agri-50 px-3 py-1 rounded-md">HOW IT WORKS</span>
                        <h2 class="text-3xl font-extrabold text-agri-900 mt-2 mb-2">Get started in 5 simple steps</h2>
                        <p class="text-slate-600 max-w-md mx-auto mb-12 text-sm">Finding or renting equipment is quick and easy.</p>
                        
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
                            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm text-center">
                                <div class="w-10 h-10 mx-auto bg-agri-900 text-white rounded-full flex items-center justify-center font-bold text-sm mb-4">01</div>
                                <i class="fa-solid fa-user-plus text-agri-600 text-2xl mb-3"></i>
                                <h4 class="font-bold text-slate-900 text-sm mb-1">Create account</h4>
                                <p class="text-xs text-slate-500">Sign up as a Farmer or Owner.</p>
                            </div>
                            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm text-center">
                                <div class="w-10 h-10 mx-auto bg-agri-900 text-white rounded-full flex items-center justify-center font-bold text-sm mb-4">02</div>
                                <i class="fa-solid fa-magnifying-glass text-agri-600 text-2xl mb-3"></i>
                                <h4 class="font-bold text-slate-900 text-sm mb-1">Find equipment</h4>
                                <p class="text-xs text-slate-500">Browse available machinery near you.</p>
                            </div>
                            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm text-center">
                                <div class="w-10 h-10 mx-auto bg-agri-900 text-white rounded-full flex items-center justify-center font-bold text-sm mb-4">03</div>
                                <i class="fa-solid fa-calendar-days text-agri-600 text-2xl mb-3"></i>
                                <h4 class="font-bold text-slate-900 text-sm mb-1">Choose date & time</h4>
                                <p class="text-xs text-slate-500">Select your rental period and send a request.</p>
                            </div>
                            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm text-center">
                                <div class="w-10 h-10 mx-auto bg-agri-900 text-white rounded-full flex items-center justify-center font-bold text-sm mb-4">04</div>
                                <i class="fa-solid fa-handshake text-agri-600 text-2xl mb-3"></i>
                                <h4 class="font-bold text-slate-900 text-sm mb-1">Owner responds</h4>
                                <p class="text-xs text-slate-500">Get confirmation and manage your booking.</p>
                            </div>
                            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm text-center">
                                <div class="w-10 h-10 mx-auto bg-agri-900 text-white rounded-full flex items-center justify-center font-bold text-sm mb-4">05</div>
                                <i class="fa-solid fa-circle-check text-agri-600 text-2xl mb-3"></i>
                                <h4 class="font-bold text-slate-900 text-sm mb-1">Complete rental</h4>
                                <p class="text-xs text-slate-500">Pay securely and rate the experience.</p>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- FAQ Section -->
                <section class="py-16 bg-slate-50 border-t border-slate-200">
                    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                        <span class="text-xs font-bold text-agri-700 uppercase tracking-widest bg-agri-50 px-3 py-1 rounded-md border border-agri-200">FAQ</span>
                        <h2 class="text-3xl font-extrabold text-agri-900 mt-2 mb-10">Frequently Asked Questions</h2>
                        
                        <div class="space-y-4 text-left">
                            <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                                <button onclick="toggleFaq(this)" class="w-full px-6 py-4 flex justify-between items-center font-bold text-slate-900 text-sm hover:bg-slate-50 transition">
                                    <span>How can small farmers share expensive equipment instead of owning it?</span>
                                    <i class="fa-solid fa-chevron-down text-slate-400 transition-transform"></i>
                                </button>
                                <div class="faq-content hidden px-6 pb-4 text-xs text-slate-600 leading-relaxed">
                                    Small farmers can rent high-value machinery like tractors, rotavators, and harvesters on an hourly or daily basis through AgriShare India, eliminating the heavy financial burden of purchasing and maintaining equipment outright.
                                </div>
                            </div>

                            <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                                <button onclick="toggleFaq(this)" class="w-full px-6 py-4 flex justify-between items-center font-bold text-slate-900 text-sm hover:bg-slate-50 transition">
                                    <span>How does AgriShare India work?</span>
                                    <i class="fa-solid fa-chevron-down text-slate-400 transition-transform"></i>
                                </button>
                                <div class="faq-content hidden px-6 pb-4 text-xs text-slate-600 leading-relaxed">
                                    Farmers browse available equipment, select dates, and send booking requests. Owners review and accept requests, allowing both parties to coordinate secure rentals and complete transactions smoothly.
                                </div>
                            </div>

                            <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                                <button onclick="toggleFaq(this)" class="w-full px-6 py-4 flex justify-between items-center font-bold text-slate-900 text-sm hover:bg-slate-50 transition">
                                    <span>Can equipment owners earn from unused machinery?</span>
                                    <i class="fa-solid fa-chevron-down text-slate-400 transition-transform"></i>
                                </button>
                                <div class="faq-content hidden px-6 pb-4 text-xs text-slate-600 leading-relaxed">
                                    Yes! Equipment owners can list their idle tractors and implements, set their own pricing rates and calendar availability, and earn steady supplementary income from bookings.
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
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

        function renderEquipmentDetail(id) { return `<div class="max-w-7xl mx-auto px-4 py-8" id="equipmentDetailContainer"><div class="bg-white p-8 rounded-3xl">Loading details...</div></div>`; }
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
                end_datetime: document.getElementById('bookEnd').value.replace('T', ' ')
            };
            const res = await fetch('/api/bookings', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            if(res.ok) { alert('Booking requested successfully!'); router('marketplace'); }
        }

        function renderAdvisor() {
            return `
                <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    <div class="text-center mb-8">
                        <span class="text-xs font-bold text-agri-700 tracking-widest uppercase bg-agri-100 px-3 py-1 rounded-md">SMART RECOMMENDATIONS</span>
                        <h1 class="text-3xl font-extrabold text-agri-900 mt-2">Farm Equipment Advisor</h1>
                        <p class="text-sm text-slate-600 mt-1">Get precise equipment recommendations based on your crop and farming operation.</p>
                    </div>

                    <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm mb-8">
                        <form onsubmit="handleAdvisorSubmit(event)" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Crop</label>
                                <select id="advCrop" class="w-full px-3 py-3 rounded-xl border border-slate-300 text-sm bg-white">
                                    <option value="Paddy">Paddy / Rice</option>
                                    <option value="Wheat">Wheat</option>
                                    <option value="Sugarcane">Sugarcane</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Farming Operation</label>
                                <select id="advOperation" class="w-full px-3 py-3 rounded-xl border border-slate-300 text-sm bg-white">
                                    <option value="Land Preparation">Land Preparation / Ploughing</option>
                                    <option value="Harvesting">Harvesting & Threshing</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">Farm Size (Acres)</label>
                                <input type="number" id="advSize" value="5" class="w-full px-3 py-3 rounded-xl border border-slate-300 text-sm">
                            </div>
                            <div class="sm:col-span-3">
                                <button type="submit" class="w-full bg-agri-600 hover:bg-agri-700 text-white font-bold py-3.5 rounded-xl transition shadow-sm">Get Recommendations</button>
                            </div>
                        </form>
                    </div>

                    <div id="advisorResults" class="space-y-6"></div>
                </div>
            `;
        }

        async function handleAdvisorSubmit(e) {
            e.preventDefault();
            const crop = document.getElementById('advCrop').value;
            const operation = document.getElementById('advOperation').value;

            const res = await fetch('/api/advisor/recommend', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({crop, operation})
            });
            const data = await res.json();
            const resultsDiv = document.getElementById('advisorResults');

            resultsDiv.innerHTML = `
                <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                    <h3 class="font-bold text-agri-900 text-lg mb-4">Recommended Machinery Categories for ${crop} (${operation})</h3>
                    <div class="space-y-4 mb-6">
                        ${data.recommendations.map(rec => `
                            <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div>
                                    <h4 class="font-bold text-agri-900 text-base flex items-center"><i class="fa-solid fa-tractor mr-2 text-agri-700"></i>${rec.category}</h4>
                                    <p class="text-xs text-slate-600 mt-1">${rec.reason}</p>
                                    <span class="inline-block mt-2 text-[11px] bg-agri-100 text-agri-800 font-semibold px-2.5 py-1 rounded-md">Power: ${rec.hp}</span>
                                </div>
                                <div class="text-right">
                                    <span class="text-sm font-extrabold text-agri-900 block">${rec.range}</span>
                                    <button onclick="router('marketplace', '${rec.category}')" class="mt-2 bg-agri-600 hover:bg-agri-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition">View ${rec.category}</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        window.onload = function() { checkAuth(); router('home'); }
    </script>
</body>
</html>
"""

with open(os.path.join(os.path.dirname(__file__), 'templates', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(INDEX_HTML)

if __name__ == '__main__':
    with app.app_context():
        seed_database()
        print("Database seeded successfully with exact screenshot layout restored!")
    app.run(host='0.0.0.0', port=5000, debug=True)
