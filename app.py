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

# Database file path
DB_PATH = 'database.json'

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

# Mabati options (Actual roofing sheets only - Updated)
MABATI_OPTIONS = [
    "Dumu Zas - 28 Gauge",
    "Dumu Zas - 26 Gauge",
    "Dumu Zas - 30 Gauge",
    "Versatile - 28 Gauge",
    "Versatile - 26 Gauge",
    "Box Profile - 0.3mm",
    "Box Profile - 0.4mm",
    "Box Profile - 0.5mm",
    "Roman Tile - 28 Gauge",
    "Roman Tile - 26 Gauge",
    "Roman Tile - Color Coated",
    "Roman Tile - Jenga Tile",
    "Roman Tile - Modern Tile",
    "Roman Tile - Traditional",
    "Corrugated GCI - 28 Gauge",
    "Corrugated GCI - 26 Gauge",
    "Corrugated GCI - 30 Gauge",
    "Decra Tiles - Stone Coated",
    "Decra Tiles - Shake",
    "Decra Tiles - Tile",
    "Color Bond - 28 Gauge",
    "Color Bond - 26 Gauge",
    "Galvalume - 28 Gauge",
    "Galvalume - 26 Gauge",
    "Zincalume",
    "Heritage Shingles",
    "Others"
]

# Roofing essentials (Accessories)
ROOFING_ESSENTIALS = [
    "Half Round Gutters - 0.45mm",
    "Half Round Gutters - 0.5mm",
    "Box Gutters - 0.5mm",
    "Box Gutters - 0.6mm",
    "Ogee Gutters",
    "Ridge Cap - Standard 150mm",
    "Ridge Cap - Wide 200mm",
    "Ridge Cap - Ventilated",
    "Ridge Cap - Decorative",
    "Wall Flashing - 0.4mm",
    "Barge Flashing - 0.4mm",
    "Valley Flashing - 0.5mm",
    "Apron Flashing",
    "Step Flashing",
    "Insulated Panel - 25mm",
    "Insulated Panel - 50mm",
    "Insulated Panel - 75mm",
    "Insulated Panel - 100mm"
]

# Database helper functions
def read_db():
    """Read data from JSON database"""
    if not os.path.exists(DB_PATH):
        # Create default database structure
        default_db = {
            "admins": [],
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
                    "bio": "Antony Mutia is the founder and CEO of Tonnie Roofing, with extensive experience in the construction industry. His vision is to provide quality roofing and interior design services to Kenyan homeowners and businesses with integrity and excellence.",
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
                        "Roof inspections & assessments"
                    ],
                    "active": True,
                    "project_count": 0
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
                        "Space planning & design"
                    ],
                    "active": True,
                    "project_count": 0
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
                        "Regular maintenance packages"
                    ],
                    "active": True,
                    "project_count": 0
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
                        "Timeline projections"
                    ],
                    "active": True,
                    "project_count": 0
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
                "admin_count": 0,
                "max_admins": 2
            },
            "mabati_options": MABATI_OPTIONS,
            "roofing_essentials": ROOFING_ESSENTIALS,
            "kenyan_counties": KENYAN_COUNTIES
        }
        write_db(default_db)
        return default_db
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def write_db(data):
    """Write data to JSON database"""
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)

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

# Routes
@app.route('/')
def index():
    data = read_db()
    data = process_image_urls(data)
    featured_projects = [p for p in data['projects'] if p.get('featured', False)][:4]
    return render_template('index.html', 
                         profile=data['profile'], 
                         services=data['services'],
                         projects=featured_projects,
                         mabati_options=data.get('mabati_options', MABATI_OPTIONS))

@app.route('/services')
def services():
    data = read_db()
    data = process_image_urls(data)
    return render_template('services.html', 
                         profile=data['profile'], 
                         services=data['services'])

@app.route('/projects')
def projects():
    data = read_db()
    data = process_image_urls(data)
    service = request.args.get('service', 'all')
    return render_template('projects.html', 
                         profile=data['profile'], 
                         projects=data['projects'],
                         service=service,
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES))

@app.route('/project')
def project_detail():
    data = read_db()
    data = process_image_urls(data)
    project_id = request.args.get('id')
    project = None
    for p in data['projects']:
        if p['id'] == project_id:
            project = p
            break
    return render_template('project.html', 
                         profile=data['profile'], 
                         project=project)

@app.route('/profile')
def company_profile():
    data = read_db()
    data = process_image_urls(data)
    return render_template('profile.html', 
                         profile=data['profile'], 
                         services=data['services'])

@app.route('/contact')
def contact():
    data = read_db()
    service = request.args.get('service', 'general')
    return render_template('contact.html', 
                         profile=data['profile'], 
                         service=service,
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES),
                         mabati_options=data.get('mabati_options', MABATI_OPTIONS),
                         roofing_essentials=data.get('roofing_essentials', ROOFING_ESSENTIALS))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    data = read_db()
    
    # Check if auto-create admin from env vars
    if data['settings']['admin_count'] == 0 and os.getenv('ADMIN_USERNAME') and os.getenv('ADMIN_EMAIL'):
        # Auto-create first admin from environment variables
        new_admin = {
            'id': str(uuid.uuid4()),
            'username': os.getenv('ADMIN_USERNAME'),
            'password': os.getenv('ADMIN_PASSWORD_HASH', 'admin123'),  # In production, use hashed password
            'full_name': 'Antony Mutia',
            'email': os.getenv('ADMIN_EMAIL'),
            'created_at': datetime.now().isoformat()
        }
        data['admins'].append(new_admin)
        data['settings']['admin_count'] = 1
        write_db(data)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        for admin in data['admins']:
            if admin['username'] == username and admin['password'] == password:
                session['admin_logged_in'] = True
                session['admin_id'] = admin['id']
                session['admin_username'] = username
                session['admin_name'] = admin.get('full_name', username)
                return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/login.html', error='Invalid credentials', admin_count=data['settings']['admin_count'], max_admins=data['settings']['max_admins'])
    
    return render_template('admin/login.html', admin_count=data['settings']['admin_count'], max_admins=data['settings']['max_admins'])

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    data = read_db()
    return render_template('admin/dashboard.html', 
                         profile=data['profile'],
                         stats={
                             'projects': len(data['projects']),
                             'inquiries': len([i for i in data['inquiries'] if i.get('status') == 'unread']),
                             'services': len([s for s in data['services'] if s.get('active')]),
                             'admins': data['settings']['admin_count']
                         })

@app.route('/admin/projects')
@admin_required
def admin_projects():
    data = read_db()
    return render_template('admin/projects.html', 
                         projects=data['projects'],
                         services=data['services'])

@app.route('/admin/project-edit', methods=['GET', 'POST'])
@admin_required
def admin_project_edit():
    data = read_db()
    project_id = request.args.get('id')
    project = None
    
    if request.method == 'POST':
        # Handle project save
        project_data = request.get_json()
        # Process and save
        return jsonify({'success': True})
    
    if project_id:
        for p in data['projects']:
            if p['id'] == project_id:
                project = p
                break
    
    return render_template('admin/project-edit.html',
                         project=project,
                         services=data['services'],
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES),
                         mabati_options=data.get('mabati_options', MABATI_OPTIONS),
                         roofing_essentials=data.get('roofing_essentials', ROOFING_ESSENTIALS),
                         cloudinary_cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'))

@app.route('/admin/services')
@admin_required
def admin_services():
    data = read_db()
    return render_template('admin/services.html', services=data['services'])

@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    data = read_db()
    if request.method == 'POST':
        # Handle profile update
        profile_data = request.get_json()
        data['profile'].update(profile_data)
        write_db(data)
        return jsonify({'success': True})
    return render_template('admin/profile.html', 
                         profile=data['profile'],
                         counties=data.get('kenyan_counties', KENYAN_COUNTIES))

@app.route('/admin/inquiries')
@admin_required
def admin_inquiries():
    data = read_db()
    return render_template('admin/inquiries.html', inquiries=data['inquiries'])

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    data = read_db()
    return render_template('admin/analytics.html', visits=data['visits'])

@app.route('/admin/create-account', methods=['GET', 'POST'])
def admin_create_account():
    data = read_db()
    
    if data['settings']['admin_count'] >= data['settings']['max_admins']:
        return render_template('admin/create-account.html', max_reached=True)
    
    if request.method == 'POST':
        new_admin = {
            'id': str(uuid.uuid4()),
            'username': request.form.get('username'),
            'password': request.form.get('password'),  # In production, hash this
            'full_name': request.form.get('fullName'),
            'email': request.form.get('email'),
            'created_at': datetime.now().isoformat()
        }
        
        data['admins'].append(new_admin)
        data['settings']['admin_count'] += 1
        write_db(data)
        
        return redirect(url_for('admin_login'))
    
    return render_template('admin/create-account.html', 
                         max_reached=False,
                         current_count=data['settings']['admin_count'],
                         max_count=data['settings']['max_admins'])

# API Routes for Cloudinary
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

if __name__ == '__main__':

    @app.route('/debug/db-status')
def debug_db_status():
    """Check if database exists and has admins"""
    import os
    data = read_db()
    
    html = "<h1>🔍 Database Debug Info</h1>"
    html += f"<p>Database file exists: {os.path.exists(DB_PATH)}</p>"
    html += f"<p>Database path: {DB_PATH}</p>"
    
    try:
        html += f"<p>Total admins in DB: {len(data['admins'])}</p>"
        html += "<h2>Admins:</h2><ul>"
        for admin in data['admins']:
            html += f"<li>👤 Username: <strong>{admin['username']}</strong> | Password: {admin['password']} | Name: {admin.get('full_name', 'N/A')}</li>"
        html += "</ul>"
        
        html += f"<p>Admin count setting: {data['settings']['admin_count']}</p>"
        html += f"<p>Max admins: {data['settings']['max_admins']}</p>"
        
    except Exception as e:
        html += f"<p style='color:red'>Error reading data: {str(e)}</p>"
    
    html += "<p><a href='/admin/login'>Try Login</a> | <a href='/debug/create-test-admin'>Create Test Admin</a></p>"
    return html

@app.route('/debug/create-test-admin')
def debug_create_test_admin():
    """Create a test admin account"""
    data = read_db()
    
    # Check if test admin already exists
    for admin in data['admins']:
        if admin['username'] == 'test':
            return "Test admin already exists. Username: test, Password: test123"
    
    # Create test admin
    test_admin = {
        'id': str(uuid.uuid4()),
        'username': 'test',
        'password': 'test123',
        'full_name': 'Test User',
        'email': 'test@example.com',
        'created_at': datetime.now().isoformat()
    }
    
    data['admins'].append(test_admin)
    data['settings']['admin_count'] = len(data['admins'])
    write_db(data)
    
    return "✅ Test admin created! Username: test, Password: test123<br><a href='/debug/db-status'>Check DB Status</a>"

@app.route('/debug/fix-admin')
def debug_fix_admin():
    """Force create Antony admin account"""
    data = read_db()
    
    # Remove any existing antony admin
    data['admins'] = [a for a in data['admins'] if a['username'] != 'antony']
    
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
    
    return "✅ Antony admin created! Username: antony, Password: antony123<br><a href='/debug/db-status'>Check DB Status</a>"

@app.route('/debug/reset-db')
def debug_reset_db():
    """Reset database to minimal working state"""
    import os
    
    # Backup current DB
    if os.path.exists(DB_PATH):
        os.rename(DB_PATH, DB_PATH + '.backup')
    
    # Create minimal working DB
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
        "mabati_options": [],
        "roofing_essentials": [],
        "kenyan_counties": []
    }
    
    write_db(minimal_db)
    return "✅ Database reset with Antony admin! Username: antony, Password: antony123<br><a href='/debug/db-status'>Check DB Status</a>"
    app.run(debug=True)
