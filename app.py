from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import secrets
import uuid
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tonnie-roofing-secret-key-change-this')

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Database file path - use absolute path for Render
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.json')

# Kenyan counties list
KENYAN_COUNTIES = [
    "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo Marakwet", "Embu", "Garissa",
    "Homa Bay", "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi",
    "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu",
    "Machakos", "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa",
    "Murang'a", "Nairobi", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua",
    "Nyeri", "Samburu", "Siaya", "Taita Taveta", "Tana River", "Tharaka Nithi",
    "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
]

# Mabati options
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

# Roofing essentials
ROOFING_ESSENTIALS = [
    "Half Round Gutters - 0.45mm", "Half Round Gutters - 0.5mm",
    "Box Gutters - 0.5mm", "Box Gutters - 0.6mm", "Ogee Gutters",
    "Ridge Cap - Standard 150mm", "Ridge Cap - Wide 200mm",
    "Ridge Cap - Ventilated", "Ridge Cap - Decorative",
    "Wall Flashing - 0.4mm", "Barge Flashing - 0.4mm", "Valley Flashing - 0.5mm",
    "Apron Flashing", "Step Flashing",
    "Insulated Panel - 25mm", "Insulated Panel - 50mm", "Insulated Panel - 75mm", "Insulated Panel - 100mm"
]

# Database helper functions
def read_db():
    """Read data from JSON database"""
    try:
        if not os.path.exists(DB_PATH):
            print(f"Database file not found at {DB_PATH}, creating default...")
            # Create default database structure with Antony as default admin
            default_db = {
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
                    "admin_count": 1,
                    "max_admins": 2
                },
                "mabati_options": MABATI_OPTIONS,
                "roofing_essentials": ROOFING_ESSENTIALS,
                "kenyan_counties": KENYAN_COUNTIES
            }
            write_db(default_db)
            return default_db
        
        with open(DB_PATH, 'r') as f:
            data = json.load(f)
            print(f"Database read successfully. Admins: {len(data.get('admins', []))}")
            return data
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error at line {e.lineno}, column {e.colno}: {e.msg}")
        print(f"Error position: {e.pos}")
        # Return minimal working data
        return {
            "admins": [{
                "id": "admin_001",
                "username": "antony",
                "password": "antony123",
                "full_name": "Antony Mutia",
                "email": "antonymutie7@gmail.com",
                "created_at": datetime.now().isoformat()
            }],
            "settings": {"admin_count": 1, "max_admins": 2},
            "profile": {},
            "services": [],
            "projects": [],
            "inquiries": [],
            "visits": {}
        }
    except Exception as e:
        print(f"❌ Error reading database: {str(e)}")
        return {
            "admins": [{
                "id": "admin_001",
                "username": "antony",
                "password": "antony123",
                "full_name": "Antony Mutia",
                "email": "antonymutie7@gmail.com",
                "created_at": datetime.now().isoformat()
            }],
            "settings": {"admin_count": 1, "max_admins": 2},
            "profile": {},
            "services": [],
            "projects": [],
            "inquiries": [],
            "visits": {}
        }

def write_db(data):
    """Write data to JSON database"""
    try:
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Database written successfully. Admins: {len(data.get('admins', []))}")
        return True
    except Exception as e:
        print(f"❌ Error writing database: {str(e)}")
        return False

# Cloudinary helper functions
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

def upload_to_cloudinary(file, folder, public_id=None):
    """Upload file to Cloudinary and return public_id"""
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

# Update image URLs in database
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

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== PUBLIC ROUTES ====================

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

# ==================== ADMIN AUTH ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    data = read_db()
    
    # Ensure admin_count matches actual admins
    data['settings']['admin_count'] = len(data.get('admins', []))
    write_db(data)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt - Username: {username}")
        print(f"Current admins in DB: {len(data.get('admins', []))}")
        
        # Check credentials
        for admin in data.get('admins', []):
            print(f"Checking against: {admin['username']}")
            if admin['username'] == username and admin['password'] == password:
                session['admin_logged_in'] = True
                session['admin_id'] = admin['id']
                session['admin_username'] = username
                session['admin_name'] = admin.get('full_name', username)
                print(f"✅ Login successful for: {username}")
                return redirect(url_for('admin_dashboard'))
        
        print(f"❌ Login failed for: {username}")
        return render_template('admin/login.html', 
                             error='Invalid username or password',
                             admin_count=data['settings']['admin_count'], 
                             max_admins=data['settings']['max_admins'])
    
    # Check for success message from account creation
    account_created = request.args.get('account') == 'created'
    
    return render_template('admin/login.html', 
                         admin_count=data['settings']['admin_count'], 
                         max_admins=data['settings']['max_admins'],
                         account_created=account_created)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/create-account', methods=['GET', 'POST'])
def admin_create_account():
    data = read_db()
    
    if data['settings']['admin_count'] >= data['settings']['max_admins']:
        return render_template('admin/create-account.html', max_reached=True)
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            password = request.form.get('password')
            full_name = request.form.get('fullName')
            email = request.form.get('email')
            
            print(f"Creating account for: {username}")
            
            # Validate required fields
            if not all([username, password, full_name, email]):
                return render_template('admin/create-account.html', 
                                     error='All fields are required',
                                     current_count=data['settings']['admin_count'],
                                     max_count=data['settings']['max_admins'])
            
            # Check if username already exists
            for admin in data.get('admins', []):
                if admin['username'] == username:
                    return render_template('admin/create-account.html', 
                                         error='Username already exists',
                                         current_count=data['settings']['admin_count'],
                                         max_count=data['settings']['max_admins'])
            
            # Create new admin
            new_admin = {
                'id': str(uuid.uuid4()),
                'username': username,
                'password': password,
                'full_name': full_name,
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            
            # Add to database
            if 'admins' not in data:
                data['admins'] = []
            data['admins'].append(new_admin)
            data['settings']['admin_count'] = len(data['admins'])
            
            # Write to file
            if write_db(data):
                print(f"✅ Account created. New count: {data['settings']['admin_count']}")
                return redirect(url_for('admin_login', account='created'))
            else:
                return render_template('admin/create-account.html', 
                                     error='Failed to save account. Please try again.',
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

# ==================== ADMIN PROTECTED ROUTES ====================

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
        # Handle project save
        project_data = request.get_json()
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

# ==================== CLOUDINARY API ROUTES ====================

@app.route('/admin/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """Handle image upload to Cloudinary"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    folder = request.form.get('folder', 'misc')
    public_id = request.form.get('public_id', None)
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    result = upload_to_cloudinary(file, folder, public_id)
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
    """Delete image from Cloudinary"""
    data = request.get_json()
    public_id = data.get('public_id')
    
    if not public_id:
        return jsonify({'error': 'No public_id provided'}), 400
    
    success = delete_from_cloudinary(public_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Delete failed'}), 500

# ==================== DEBUG ROUTES (REMOVE IN PRODUCTION) ====================

@app.route('/debug/db-status')
def debug_db_status():
    """Check if database exists and has admins"""
    data = read_db()
    
    html = """
    <html>
    <head>
        <title>Database Debug</title>
        <style>
            body { font-family: Arial; padding: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #d97706; }
            .success { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
            pre { background: #f0f0f0; padding: 1rem; border-radius: 5px; overflow: auto; }
            .btn { display: inline-block; padding: 0.5rem 1rem; background: #d97706; color: white; text-decoration: none; border-radius: 5px; margin-right: 0.5rem; }
            .btn:hover { background: #b45f06; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Database Debug Info</h1>
    """
    
    html += f"<p><strong>Database path:</strong> {DB_PATH}</p>"
    html += f"<p><strong>File exists:</strong> {os.path.exists(DB_PATH)}</p>"
    
    try:
        admins = data.get('admins', [])
        html += f"<p><strong>Total admins in DB:</strong> {len(admins)}</p>"
        
        if admins:
            html += "<h2>Admins:</h2><ul>"
            for admin in admins:
                html += f"<li>👤 <strong>Username:</strong> {admin.get('username', 'N/A')} | <strong>Password:</strong> {admin.get('password', 'N/A')} | <strong>Name:</strong> {admin.get('full_name', 'N/A')}</li>"
            html += "</ul>"
        else:
            html += "<p class='error'>⚠️ No admins found in database!</p>"
        
        html += f"<p><strong>Admin count setting:</strong> {data.get('settings', {}).get('admin_count', 0)}</p>"
        html += f"<p><strong>Max admins:</strong> {data.get('settings', {}).get('max_admins', 2)}</p>"
        
    except Exception as e:
        html += f"<p class='error'>❌ Error reading data: {str(e)}</p>"
    
    html += """
        <div style="margin-top: 2rem;">
            <a href="/admin/login" class="btn">Go to Login</a>
            <a href="/debug/create-test-admin" class="btn">Create Test Admin</a>
            <a href="/debug/fix-admin" class="btn">Fix Antony Admin</a>
            <a href="/debug/reset-db" class="btn">Reset Database</a>
        </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/debug/create-test-admin')
def debug_create_test_admin():
    """Create a test admin account"""
    data = read_db()
    
    # Check if test admin already exists
    for admin in data.get('admins', []):
        if admin['username'] == 'test':
            return redirect('/debug/db-status')
    
    # Create test admin
    test_admin = {
        'id': str(uuid.uuid4()),
        'username': 'test',
        'password': 'test123',
        'full_name': 'Test User',
        'email': 'test@example.com',
        'created_at': datetime.now().isoformat()
    }
    
    if 'admins' not in data:
        data['admins'] = []
    data['admins'].append(test_admin)
    data['settings']['admin_count'] = len(data['admins'])
    write_db(data)
    
    return redirect('/debug/db-status')

@app.route('/debug/fix-admin')
def debug_fix_admin():
    """Force create Antony admin account"""
    data = read_db()
    
    # Remove any existing antony admin
    if 'admins' in data:
        data['admins'] = [a for a in data['admins'] if a.get('username') != 'antony']
    else:
        data['admins'] = []
    
    # Create fresh antony admin
    antony_admin = {
        'id': str(uuid.uuid4()),
        'username': 'antony',
        'password': 'antony123',
        'full_name': 'Antony Mutia',
        'email': 'antonymutie7@gmail.com',
        'created_at': datetime.now().isoformat()
    }
    
    data['admins'].append(antony_admin)
    data['settings']['admin_count'] = len(data['admins'])
    write_db(data)
    
    return redirect('/debug/db-status')

@app.route('/debug/reset-db')
def debug_reset_db():
    """Reset database to minimal working state"""
    # Create minimal working DB with Antony admin
    minimal_db = {
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
    
    if write_db(minimal_db):
        return redirect('/debug/db-status')
    else:
        return "❌ Failed to reset database"

@app.route('/debug/force-logout')
def force_logout():
    """Clear session and localStorage instructions"""
    session.clear()
    return '''
    <html>
    <head>
        <title>Session Cleared</title>
        <style>
            body { font-family: Arial; padding: 2rem; background: #f5f5f5; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #d97706; }
            .success { color: green; font-size: 1.2rem; margin: 1rem; }
            button { padding: 0.8rem 1.5rem; background: #d97706; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; }
            button:hover { background: #b45f06; }
            .steps { text-align: left; max-width: 400px; margin: 2rem auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Server Session Cleared</h1>
            <div class="success">Your admin session has been cleared from the server</div>
            <p>Now clear your browser's localStorage:</p>
            <div class="steps">
                <ol>
                    <li>Open Developer Tools (F12)</li>
                    <li>Go to Console tab</li>
                    <li>Type: <code>localStorage.clear()</code></li>
                    <li>Press Enter</li>
                    <li>Refresh this page</li>
                </ol>
            </div>
            <button onclick="localStorage.clear(); window.location.href='/admin/login'">
                Clear Local Storage & Go to Login
            </button>
            <p style="margin-top: 1rem;"><a href="/admin/login">Go to Login Page</a></p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
