from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import uuid
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
import tempfile
import hashlib
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ========== SESSION CONFIGURATION ==========
app.secret_key = os.getenv('SECRET_KEY', 'tonnie-roofing-fixed-secret-key-2026-change-this')

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = '/tmp/flask-sessions'
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['SESSION_KEY_PREFIX'] = 'tonnie_'

app.config['SESSION_COOKIE_NAME'] = 'tonnie_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

Session(app)

# ========== CLOUDINARY CONFIGURATION ==========
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# ========== DATABASE PATHS ==========
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
RUNTIME_DB_PATH = '/tmp/database.json'  # Writable location on Render
CLOUDINARY_DB_PATH = 'tonnie-roofing/database.json'  # Cloudinary public ID
TEMPLATE_DB_PATH = os.path.join(BASE_DIR, 'database.template.json')  # Backup template

# ========== KENYAN COUNTIES ==========
KENYAN_COUNTIES = [
    "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo Marakwet", "Embu", "Garissa",
    "Homa Bay", "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi",
    "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu",
    "Machakos", "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa",
    "Murang'a", "Nairobi", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua",
    "Nyeri", "Samburu", "Siaya", "Taita Taveta", "Tana River", "Tharaka Nithi",
    "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
]

# ========== MABATI OPTIONS ==========
MABATI_OPTIONS = [
    "Dumu Zas - 28 Gauge", "Dumu Zas - 26 Gauge", "Dumu Zas - 30 Gauge",
    "Versatile - 28 Gauge", "Versatile - 26 Gauge",
    "Box Profile - 0.3mm", "Box Profile - 0.4mm", "Box Profile - 0.5mm",
    "Roman Tile - 28 Gauge", "Roman Tile - 26 Gauge", "Roman Tile - Color Coated",
    "Roman Tile - Jenga Tile", "Roman Tile - Modern Tile", "Roman Tile - Traditional",
    "Corrugated GCI - 28 Gauge", "Corrugated GCI - 26 Gauge", "Corrugated GCI - 30 Gauge",
    "Decra Tiles - Stone Coated", "Decra Tiles - Shake", "Decra Tiles - Tile",
    "Color Bond - 28 Gauge", "Color Bond - 26 Gauge",
    "Galvalume - 28 Gauge", "Galvalume - 26 Gauge",
    "Zincalume", "Heritage Shingles", "Others"
]

# ========== ROOFING ESSENTIALS ==========
ROOFING_ESSENTIALS = [
    "Half Round Gutters - 0.45mm", "Half Round Gutters - 0.5mm",
    "Box Gutters - 0.5mm", "Box Gutters - 0.6mm", "Ogee Gutters",
    "Ridge Cap - Standard 150mm", "Ridge Cap - Wide 200mm",
    "Ridge Cap - Ventilated", "Ridge Cap - Decorative",
    "Wall Flashing - 0.4mm", "Barge Flashing - 0.4mm", "Valley Flashing - 0.5mm",
    "Apron Flashing", "Step Flashing",
    "Insulated Panel - 25mm", "Insulated Panel - 50mm", "Insulated Panel - 75mm", "Insulated Panel - 100mm"
]

# ========== CLOUDINARY DATABASE FUNCTIONS ==========

def download_from_cloudinary():
    """Download database from Cloudinary"""
    try:
        url = cloudinary.utils.cloudinary_url(
            CLOUDINARY_DB_PATH,
            resource_type='raw',
            secure=True
        )[0]
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Database downloaded from Cloudinary")
            return response.json()
        else:
            print(f"⚠️ No database found in Cloudinary (status: {response.status_code})")
            return None
    except Exception as e:
        print(f"⚠️ Could not download from Cloudinary: {e}")
        return None

def upload_to_cloudinary(data):
    """Upload database to Cloudinary"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = tmp.name
        
        result = cloudinary.uploader.upload(
            tmp_path,
            public_id=CLOUDINARY_DB_PATH,
            resource_type='raw',
            overwrite=True
        )
        os.unlink(tmp_path)
        print(f"✅ Database backed up to Cloudinary: {result['secure_url']}")
        return True
    except Exception as e:
        print(f"❌ Cloudinary backup failed: {e}")
        return False

def create_default_database():
    """Create default database structure"""
    print("📁 Creating new default database...")
    return {
        "admins": [
            {
                "id": "admin_001",
                "username": "antony",
                "password": "antony123",
                "full_name": "Antony Mutia",
                "email": "antonymutie7@gmail.com",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "admin_002",
                "username": "admin",
                "password": "admin123",
                "full_name": "Admin User",
                "email": "admin@tonnieroofing.co.ke",
                "created_at": datetime.now().isoformat()
            }
        ],
        "profile": {
            "company_name": "Tonnie Roofing",
            "company_logo": "tonnie-roofing/profile/logo",
            "hero_image": "tonnie-roofing/thumbnails/hero",
            "tagline": "Professional Roofing & Interior Design Services",
            "description": "Your trusted partner in quality construction. We provide professional roofing, interior design, and repair services across Kenya.",
            "ceo": {
                "name": "Antony Mutia",
                "photo": "tonnie-roofing/profile/ceo",
                "title": "Founder & CEO",
                "bio": "Antony Mutia is the founder and CEO of Tonnie Roofing, with extensive experience in the construction industry.",
                "phone": "0712454146",
                "email": "antonymutie7@gmail.com"
            },
            "active_since": "2015",
            "contact": {
                "phone": "0712454146",
                "whatsapp": "0712454146",
                "emergency": "0712454146",
                "email": "antonymutie7@gmail.com",
                "email2": "info@tonnieroofing.co.ke"
            },
            "social": [
                {"platform": "Facebook", "icon": "📘", "url": "https://facebook.com/tonnieroofing", "app_url": "fb://page/tonnieroofing", "active": True},
                {"platform": "TikTok", "icon": "🎵", "url": "https://tiktok.com/@tonnieroofing", "app_url": "tiktok://@tonnieroofing", "active": True},
                {"platform": "Instagram", "icon": "📷", "url": "https://instagram.com/tonnieroofing", "app_url": "instagram://user?username=tonnieroofing", "active": True},
                {"platform": "WhatsApp", "icon": "💬", "url": "https://wa.me/254712454146", "app_url": "whatsapp://send?phone=254712454146", "active": True}
            ],
            "address": {
                "street": "Kilimani Business Centre",
                "city": "Nairobi",
                "county": "Nairobi",
                "country": "Kenya",
                "po_box": "PO Box 12345-00100"
            },
            "hours": {
                "weekdays": "8:00 AM - 6:00 PM",
                "saturday": "9:00 AM - 3:00 PM",
                "sunday": "Closed",
                "emergency": "Call 0712454146",
                "repairs": "Monday to Friday, 8:00 AM - 6:00 PM"
            },
            "stats": {
                "projects_completed": 250,
                "happy_clients": 150,
                "years_experience": 8,
                "skilled_workers": 25,
                "counties_served": 47
            }
        },
        "services": [
            {
                "id": "serv_001",
                "name": "Roofing",
                "slug": "roofing",
                "icon": "🏠",
                "image": "tonnie-roofing/thumbnails/roofing",
                "detail_image": "tonnie-roofing/thumbnails/roofing-detail",
                "short_description": "Professional roof installation and maintenance",
                "full_description": "Complete roofing solutions for residential and commercial properties using quality Kenyan mabati.",
                "features": [
                    "New roof installation",
                    "Roof replacement & renovation",
                    "Leak repairs & maintenance",
                    "Roof inspections & assessments",
                    "Multiple mabati options"
                ],
                "active": True,
                "project_count": 24,
                "inquiry_count": 12,
                "image_count": 3,
                "color": "#0066cc",
                "order": 1
            },
            {
                "id": "serv_002",
                "name": "Interior Design",
                "slug": "interior",
                "icon": "✨",
                "image": "tonnie-roofing/thumbnails/interior",
                "detail_image": "tonnie-roofing/thumbnails/interior-detail",
                "short_description": "Modern interior design solutions",
                "full_description": "Transform your spaces with gypsum installations, custom fittings, and modern interior designs.",
                "features": [
                    "Gypsum ceiling installations",
                    "Custom wall fittings & partitions",
                    "Modern interior finishing",
                    "Space planning & design",
                    "Lighting design"
                ],
                "active": True,
                "project_count": 12,
                "inquiry_count": 8,
                "image_count": 2,
                "color": "#7b1fa2",
                "order": 2
            },
            {
                "id": "serv_003",
                "name": "Repairs",
                "slug": "repairs",
                "icon": "🔧",
                "image": "tonnie-roofing/thumbnails/repairs",
                "detail_image": "tonnie-roofing/thumbnails/repairs-detail",
                "short_description": "Professional repair services",
                "full_description": "Quick response and reliable repair services for roofing, ceilings, and structural issues.",
                "features": [
                    "Roof leak repairs",
                    "Ceiling & wall repairs",
                    "Structural damage fixes",
                    "Regular maintenance packages",
                    "Working days only (Mon-Fri)"
                ],
                "active": True,
                "project_count": 8,
                "inquiry_count": 15,
                "image_count": 2,
                "color": "#c62828",
                "order": 3
            },
            {
                "id": "serv_004",
                "name": "Quoting Service",
                "slug": "quoting",
                "icon": "📋",
                "image": "tonnie-roofing/thumbnails/quoting",
                "detail_image": "tonnie-roofing/thumbnails/quoting-detail",
                "short_description": "Detailed project quotes",
                "full_description": "Get accurate, detailed quotes for your roofing and interior design projects.",
                "features": [
                    "Detailed project assessment",
                    "Material quantity calculations",
                    "Labor cost estimation",
                    "Timeline projections",
                    "Free consultation (working days)"
                ],
                "active": True,
                "project_count": 4,
                "inquiry_count": 20,
                "image_count": 1,
                "color": "#ef6c00",
                "order": 4
            }
        ],
        "projects": [],
        "inquiries": [],
        "visits": {
            "total": 0,
            "monthly": {},
            "daily": {},
            "devices": {}
        },
        "settings": {
            "admin_count": 2,
            "max_admins": 2
        },
        "mabati_options": MABATI_OPTIONS,
        "roofing_essentials": ROOFING_ESSENTIALS,
        "kenyan_counties": KENYAN_COUNTIES
    }

def create_template_file():
    """Create a template database file in repo for initial deploy"""
    template_db = {
        "admins": [
            {
                "id": "admin_001",
                "username": "antony",
                "password": "antony123",
                "full_name": "Antony Mutia",
                "email": "antonymutie7@gmail.com",
                "created_at": datetime.now().isoformat()
            }
        ],
        "settings": {
            "admin_count": 1,
            "max_admins": 2
        },
        "profile": {},
        "services": [],
        "projects": [],
        "inquiries": [],
        "visits": {},
        "mabati_options": MABATI_OPTIONS,
        "roofing_essentials": ROOFING_ESSENTIALS,
        "kenyan_counties": KENYAN_COUNTIES
    }
    with open(TEMPLATE_DB_PATH, 'w') as f:
        json.dump(template_db, f, indent=2)
    return template_db

# ========== DATABASE READ/WRITE FUNCTIONS ==========

def read_db():
    """Read data from database - tries multiple sources in order"""
    data = None
    
    # 1. Try /tmp first (fastest, writable)
    if os.path.exists(RUNTIME_DB_PATH):
        try:
            with open(RUNTIME_DB_PATH, 'r') as f:
                data = json.load(f)
                print(f"✅ Database read from /tmp. Admins: {len(data.get('admins', []))}")
                return data
        except Exception as e:
            print(f"⚠️ Error reading from /tmp: {e}")
    
    # 2. Try Cloudinary (persistent storage)
    if not data:
        data = download_from_cloudinary()
        if data:
            print(f"✅ Database loaded from Cloudinary")
            # Cache to /tmp for next time
            try:
                with open(RUNTIME_DB_PATH, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Database cached to /tmp")
            except Exception as e:
                print(f"⚠️ Could not cache to /tmp: {e}")
            return data
    
    # 3. Try template file (initial deploy)
    if os.path.exists(TEMPLATE_DB_PATH):
        try:
            with open(TEMPLATE_DB_PATH, 'r') as f:
                data = json.load(f)
                print(f"✅ Database loaded from template file")
                # Save to /tmp and Cloudinary
                write_db(data)
                return data
        except Exception as e:
            print(f"⚠️ Error reading template: {e}")
    
    # 4. Create new database from scratch
    print("📁 Creating new database from scratch")
    data = create_default_database()
    write_db(data)
    return data

def write_db(data):
    """Write data to database - writes to /tmp AND Cloudinary"""
    success = False
    
    # Always write to /tmp (for immediate use)
    try:
        with open(RUNTIME_DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Database saved to /tmp")
        success = True
    except Exception as e:
        print(f"❌ Error writing to /tmp: {e}")
        success = False
    
    # Backup to Cloudinary (don't fail main operation if backup fails)
    try:
        upload_to_cloudinary(data)
    except Exception as e:
        print(f"⚠️ Cloudinary backup failed but continuing: {e}")
    
    return success

# ========== CLOUDINARY IMAGE HELPER FUNCTIONS ==========

def get_cloudinary_url(public_id, transformation=None):
    """Generate Cloudinary URL for an image"""
    if not public_id:
        return None
    if public_id.startswith('http'):
        return public_id
    options = {'secure': True}
    if transformation:
        options['transformation'] = transformation
    return cloudinary.CloudinaryImage(public_id).build_url(**options)

def upload_to_cloudinary_image(file, folder, public_id=None):
    """Upload image file to Cloudinary"""
    try:
        upload_options = {
            'folder': f'tonnie-roofing/{folder}',
            'resource_type': 'image',
            'overwrite': True
        }
        if public_id:
            upload_options['public_id'] = public_id
        
        result = cloudinary.uploader.upload(file, **upload_options)
        return {
            'public_id': result['public_id'],
            'url': result['secure_url']
        }
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None

def delete_from_cloudinary(public_id):
    """Delete image from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result['result'] == 'ok'
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False

def process_image_urls(data):
    """Convert Cloudinary public_ids to full URLs"""
    if 'profile' in data:
        profile = data['profile']
        if 'company_logo' in profile and profile['company_logo']:
            profile['company_logo_url'] = get_cloudinary_url(profile['company_logo'], {'width': 200, 'crop': 'scale'})
        if 'hero_image' in profile and profile['hero_image']:
            profile['hero_image_url'] = get_cloudinary_url(profile['hero_image'])
        if 'ceo' in profile and 'photo' in profile['ceo'] and profile['ceo']['photo']:
            profile['ceo']['photo_url'] = get_cloudinary_url(profile['ceo']['photo'], {'width': 400, 'height': 400, 'crop': 'fill'})
    
    if 'services' in data:
        for service in data['services']:
            if 'image' in service and service['image']:
                service['image_url'] = get_cloudinary_url(service['image'], {'width': 400, 'height': 200, 'crop': 'fill'})
            if 'detail_image' in service and service['detail_image']:
                service['detail_image_url'] = get_cloudinary_url(service['detail_image'], {'width': 600, 'height': 400, 'crop': 'fill'})
    
    if 'projects' in data:
        for project in data['projects']:
            if 'images' in project:
                for img in project['images']:
                    if 'path' in img and img['path']:
                        img['url'] = get_cloudinary_url(img['path'])
                    if 'thumbnail' in img and img['thumbnail']:
                        img['thumbnail_url'] = get_cloudinary_url(img['thumbnail'], {'width': 100, 'height': 70, 'crop': 'fill'})
    return data

# ========== AUTHENTICATION DECORATOR (TEMPORARILY DISABLED) ==========
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 🚫 TEMPORARILY DISABLED - No login required during migration
        # if not session.get('admin_logged_in'):
        #     print("❌ No session found, redirecting to login")
        #     return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== PUBLIC ROUTES ==========
@app.route('/')
def index():
    data = read_db()
    data = process_image_urls(data)
    featured_projects = [p for p in data.get('projects', []) if p.get('featured', False)][:4]
    return render_template('index.html', 
                         profile=data.get('profile', {}), 
                         services=data.get('services', []),
                         projects=featured_projects,
                         mabati_options=data.get('mabati_options', MABATI_OPTIONS))

@app.route('/services')
def services():
    data = read_db()
    data = process_image_urls(data)
    return render_template('services.html', 
                         profile=data.get('profile', {}), 
                         services=data.get('services', []))

@app.route('/projects')
def projects():
    data = read_db()
    data = process_image_urls(data)
    service = request.args.get('service', 'all')
    return render_template('projects.html', 
                         profile=data.get('profile', {}), 
                         projects=data.get('projects', []),
                         service=service,
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES))

@app.route('/project')
def project_detail():
    data = read_db()
    data = process_image_urls(data)
    project_id = request.args.get('id')
    project = None
    for p in data.get('projects', []):
        if p['id'] == project_id:
            project = p
            break
    return render_template('project.html', 
                         profile=data.get('profile', {}), 
                         project=project)

@app.route('/profile')
def company_profile():
    data = read_db()
    data = process_image_urls(data)
    return render_template('profile.html', 
                         profile=data.get('profile', {}), 
                         services=data.get('services', []))

@app.route('/contact')
def contact():
    data = read_db()
    service = request.args.get('service', 'general')
    return render_template('contact.html', 
                         profile=data.get('profile', {}), 
                         service=service,
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES),
                         mabati_options=data.get('mabati_options', MABATI_OPTIONS),
                         roofing_essentials=data.get('roofing_essentials', ROOFING_ESSENTIALS))

# ========== ADMIN ROUTES ==========
@app.route('/admin')
def admin_index():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    data = read_db()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"🔐 Login attempt - Username: {username}")
        
        # Find admin
        admin_user = None
        for admin in data.get('admins', []):
            if admin['username'] == username and admin['password'] == password:
                admin_user = admin
                break
        
        if admin_user:
            session.clear()
            session['admin_logged_in'] = True
            session['admin_id'] = admin_user['id']
            session['admin_username'] = username
            session['admin_name'] = admin_user.get('full_name', username)
            session.permanent = True
            
            print(f"✅ Login successful for: {username}")
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"❌ Login failed for: {username}")
            return render_template('admin/login.html', 
                                 error='Invalid username or password',
                                 admin_count=data['settings'].get('admin_count', 0), 
                                 max_admins=data['settings'].get('max_admins', 2))
    
    return render_template('admin/login.html', 
                         admin_count=data['settings'].get('admin_count', 0), 
                         max_admins=data['settings'].get('max_admins', 2))

@app.route('/admin/logout')
def admin_logout():
    username = session.get('admin_username', 'Unknown')
    session.clear()
    print(f"👋 Logout for: {username}")
    return redirect(url_for('admin_login'))

@app.route('/admin/create-account', methods=['GET', 'POST'])
def admin_create_account():
    data = read_db()
    
    if data['settings']['admin_count'] >= data['settings']['max_admins']:
        return render_template('admin/create-account.html', max_reached=True)
    
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            full_name = request.form.get('fullName')
            email = request.form.get('email')
            
            if not all([username, password, full_name, email]):
                return render_template('admin/create-account.html', 
                                     error='All fields are required',
                                     current_count=data['settings']['admin_count'],
                                     max_count=data['settings']['max_admins'])
            
            for admin in data.get('admins', []):
                if admin['username'] == username:
                    return render_template('admin/create-account.html', 
                                         error='Username already exists',
                                         current_count=data['settings']['admin_count'],
                                         max_count=data['settings']['max_admins'])
            
            new_admin = {
                'id': str(uuid.uuid4()),
                'username': username,
                'password': password,
                'full_name': full_name,
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            
            if 'admins' not in data:
                data['admins'] = []
            data['admins'].append(new_admin)
            data['settings']['admin_count'] = len(data['admins'])
            
            if write_db(data):
                print(f"✅ Account created for: {username}")
                return redirect(url_for('admin_login', account='created'))
            else:
                return render_template('admin/create-account.html', 
                                     error='Failed to save account',
                                     current_count=data['settings']['admin_count'],
                                     max_count=data['settings']['max_admins'])
            
        except Exception as e:
            print(f"❌ Error creating account: {str(e)}")
            return render_template('admin/create-account.html', 
                                 error=f'Error: {str(e)}',
                                 current_count=data['settings']['admin_count'],
                                 max_count=data['settings']['max_admins'])
    
    return render_template('admin/create-account.html', 
                         current_count=data['settings']['admin_count'],
                         max_count=data['settings']['max_admins'])

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    data = read_db()
    return render_template('admin/dashboard.html', 
                         profile=data.get('profile', {}),
                         stats={
                             'projects': len(data.get('projects', [])),
                             'inquiries': len([i for i in data.get('inquiries', []) if i.get('status') == 'unread']),
                             'services': len([s for s in data.get('services', []) if s.get('active')]),
                             'admins': data['settings']['admin_count']
                         })

@app.route('/admin/projects')
@admin_required
def admin_projects():
    data = read_db()
    return render_template('admin/projects.html', 
                         projects=data.get('projects', []),
                         services=data.get('services', []))

@app.route('/admin/project-edit', methods=['GET', 'POST'])
@admin_required
def admin_project_edit():
    data = read_db()
    project_id = request.args.get('id')
    project = None
    
    if request.method == 'POST':
        project_data = request.get_json()
        # Here you would save the project data
        # For now, just return success
        return jsonify({'success': True})
    
    if project_id:
        for p in data.get('projects', []):
            if p['id'] == project_id:
                project = p
                break
    
    return render_template('admin/project-edit.html',
                         project=project,
                         services=data.get('services', []),
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES),
                         mabati_options=data.get('mabati_options', MABATI_OPTIONS),
                         roofing_essentials=data.get('roofing_essentials', ROOFING_ESSENTIALS),
                         cloudinary_cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'))

@app.route('/admin/services')
@admin_required
def admin_services():
    data = read_db()
    return render_template('admin/services.html', services=data.get('services', []))

@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    data = read_db()
    if request.method == 'POST':
        profile_data = request.get_json()
        data['profile'].update(profile_data)
        write_db(data)
        return jsonify({'success': True})
    return render_template('admin/profile.html', 
                         profile=data.get('profile', {}),
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES))

@app.route('/admin/inquiries')
@admin_required
def admin_inquiries():
    data = read_db()
    return render_template('admin/inquiries.html', inquiries=data.get('inquiries', []))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    data = read_db()
    return render_template('admin/analytics.html', visits=data.get('visits', {}))

# ========== BACKUP ROUTE (Optional) ==========
@app.route('/admin/backup-db')
@admin_required
def backup_database():
    """Manually trigger database backup to Cloudinary"""
    data = read_db()
    if upload_to_cloudinary(data):
        return jsonify({"success": True, "message": "Database backed up to Cloudinary"})
    else:
        return jsonify({"success": False, "message": "Backup failed"}), 500

# ========== CLOUDINARY IMAGE API ROUTES ==========
@app.route('/admin/upload-image', methods=['POST'])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    folder = request.form.get('folder', 'misc')
    public_id = request.form.get('public_id', None)
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    result = upload_to_cloudinary_image(file, folder, public_id)
    if result:
        return jsonify({
            'success': True,
            'public_id': result['public_id'],
            'url': result['url']
        })
    else:
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/admin/delete-image', methods=['POST'])
@admin_required
def delete_image():
    data = request.get_json()
    public_id = data.get('public_id')
    
    if not public_id:
        return jsonify({'error': 'No public_id provided'}), 400
    
    success = delete_from_cloudinary(public_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Delete failed'}), 500

# ========== DEBUG ROUTES (Optional - Remove in Production) ==========
@app.route('/debug/db-status')
def debug_db_status():
    """Check database status"""
    data = read_db()
    return {
        'runtime_db_exists': os.path.exists(RUNTIME_DB_PATH),
        'template_db_exists': os.path.exists(TEMPLATE_DB_PATH),
        'admins_count': len(data.get('admins', [])),
        'admins': [{'username': a['username']} for a in data.get('admins', [])],
        'settings': data.get('settings', {})
    }

if __name__ == '__main__':
    # Create template file if it doesn't exist
    if not os.path.exists(TEMPLATE_DB_PATH):
        create_template_file()
    
    app.run(debug=True)
