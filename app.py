from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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
import time
import logging
from sqlalchemy.exc import OperationalError

# Import from extensions and config
from extensions import db, session as sess
from config import Config, MABATI_OPTIONS, ROOFING_ESSENTIALS, KENYAN_COUNTIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
sess.init_app(app)

# Configure Cloudinary
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET'],
    secure=True
)

# Import models
from models import Admin, Profile, Service, Project, Inquiry, Setting

# Database initialization with retry
def init_database():
    """Initialize database with retry logic"""
    with app.app_context():
        max_retries = 10
        for attempt in range(max_retries):
            try:
                db.create_all()
                logger.info(f"✅ Database connected successfully (attempt {attempt + 1})")
                
                # Check if we need to create default settings
                if not Setting.query.filter_by(key='admin_count').first():
                    Setting.set('admin_count', 0)
                    Setting.set('max_admins', app.config['MAX_ADMINS'])
                    Setting.set('site_name', 'Tonnie Roofing')
                    Setting.set('version', '1.0.0')
                    logger.info("✅ Default settings created")
                break
            except OperationalError as e:
                logger.warning(f"⏳ Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    logger.error("❌ Could not connect to database after multiple attempts")
                    # Don't exit - app will still try to run with limited functionality

# Run database initialization
init_database()

# ========== AUTHENTICATION DECORATOR ==========
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            logger.info("❌ No session found, redirecting to login")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== HEALTH CHECK ==========
@app.route('/health')
def health():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })

# ========== PUBLIC ROUTES ==========
@app.route('/')
def index():
    # This will be populated with actual data later
    return render_template('index.html', 
                         profile={}, 
                         services=[],
                         projects=[],
                         mabati_options=MABATI_OPTIONS)

@app.route('/services')
def services():
    return render_template('services.html', 
                         profile={}, 
                         services=[],
                         mabati_options=MABATI_OPTIONS)

@app.route('/projects')
def projects():
    service = request.args.get('service', 'all')
    return render_template('projects.html', 
                         profile={}, 
                         projects=[],
                         service=service,
                         counties=KENYAN_COUNTIES)

@app.route('/project')
def project_detail():
    project_id = request.args.get('id')
    return render_template('project.html', 
                         profile={}, 
                         project=None)

@app.route('/profile')
def company_profile():
    return render_template('profile.html', 
                         profile={}, 
                         services=[])

@app.route('/contact')
def contact():
    service = request.args.get('service', 'general')
    return render_template('contact.html', 
                         profile={}, 
                         service=service,
                         counties=KENYAN_COUNTIES,
                         mabati_options=MABATI_OPTIONS,
                         roofing_essentials=ROOFING_ESSENTIALS)

# ========== ADMIN AUTH ROUTES ==========
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.info(f"🔐 Login attempt - Username: {username}")
        
        # Simple hardcoded admin for testing (REMOVE IN PRODUCTION)
        if username == 'antony' and password == 'antony123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_name'] = 'Antony Mutia'
            session.permanent = True
            logger.info(f"✅ Login successful for: {username}")
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/login.html', error='Invalid credentials')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    username = session.get('admin_username', 'Unknown')
    session.clear()
    logger.info(f"👋 Logout for: {username}")
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html', 
                         profile={},
                         stats={
                             'projects': 0,
                             'inquiries': 0,
                             'services': 4,
                             'admins': 1
                         })

@app.route('/admin/projects')
@admin_required
def admin_projects():
    return render_template('admin/projects.html', 
                         projects=[],
                         services=[])

@app.route('/admin/project-edit', methods=['GET', 'POST'])
@admin_required
def admin_project_edit():
    project_id = request.args.get('id')
    return render_template('admin/project-edit.html',
                         project=None,
                         services=[],
                         counties=KENYAN_COUNTIES,
                         mabati_options=MABATI_OPTIONS,
                         roofing_essentials=ROOFING_ESSENTIALS,
                         cloudinary_cloud_name=app.config['CLOUDINARY_CLOUD_NAME'])

@app.route('/admin/services')
@admin_required
def admin_services():
    return render_template('admin/services.html', services=[])

@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    return render_template('admin/profile.html', 
                         profile={},
                         counties=KENYAN_COUNTIES)

@app.route('/admin/inquiries')
@admin_required
def admin_inquiries():
    return render_template('admin/inquiries.html', inquiries=[])

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return render_template('admin/analytics.html', visits={})

# ========== CLOUDINARY API ROUTES ==========
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
    
    try:
        upload_options = {
            'folder': f'tonnie-roofing/{folder}',
            'resource_type': 'image',
            'overwrite': True
        }
        if public_id:
            upload_options['public_id'] = public_id
        
        result = cloudinary.uploader.upload(file, **upload_options)
        return jsonify({
            'success': True,
            'public_id': result['public_id'],
            'url': result['secure_url']
        })
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/admin/delete-image', methods=['POST'])
@admin_required
def delete_image():
    data = request.get_json()
    public_id = data.get('public_id')
    
    if not public_id:
        return jsonify({'error': 'No public_id provided'}), 400
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result['result'] == 'ok':
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Delete failed'}), 500
    except Exception as e:
        logger.error(f"Cloudinary delete error: {e}")
        return jsonify({'error': 'Delete failed'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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
import time
import logging
from sqlalchemy.exc import OperationalError

# Import from extensions and config
from extensions import db, session as sess
from config import Config, MABATI_OPTIONS, ROOFING_ESSENTIALS, KENYAN_COUNTIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
sess.init_app(app)

# Configure Cloudinary
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET'],
    secure=True
)

# Import models
from models import Admin, Profile, Service, Project, Inquiry, Setting

# Database initialization with retry
def init_database():
    """Initialize database with retry logic"""
    with app.app_context():
        max_retries = 10
        for attempt in range(max_retries):
            try:
                db.create_all()
                logger.info(f"✅ Database connected successfully (attempt {attempt + 1})")
                
                # Check if we need to create default settings
                if not Setting.query.filter_by(key='admin_count').first():
                    Setting.set('admin_count', 0)
                    Setting.set('max_admins', app.config['MAX_ADMINS'])
                    Setting.set('site_name', 'Tonnie Roofing')
                    Setting.set('version', '1.0.0')
                    logger.info("✅ Default settings created")
                break
            except OperationalError as e:
                logger.warning(f"⏳ Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    logger.error("❌ Could not connect to database after multiple attempts")
                    # Don't exit - app will still try to run with limited functionality

# Run database initialization
init_database()

# ========== AUTHENTICATION DECORATOR ==========
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            logger.info("❌ No session found, redirecting to login")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== HEALTH CHECK ==========
@app.route('/health')
def health():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })

# ========== PUBLIC ROUTES ==========
@app.route('/')
def index():
    # This will be populated with actual data later
    return render_template('index.html', 
                         profile={}, 
                         services=[],
                         projects=[],
                         mabati_options=MABATI_OPTIONS)

@app.route('/services')
def services():
    return render_template('services.html', 
                         profile={}, 
                         services=[],
                         mabati_options=MABATI_OPTIONS)

@app.route('/projects')
def projects():
    service = request.args.get('service', 'all')
    return render_template('projects.html', 
                         profile={}, 
                         projects=[],
                         service=service,
                         counties=KENYAN_COUNTIES)

@app.route('/project')
def project_detail():
    project_id = request.args.get('id')
    return render_template('project.html', 
                         profile={}, 
                         project=None)

@app.route('/profile')
def company_profile():
    return render_template('profile.html', 
                         profile={}, 
                         services=[])

@app.route('/contact')
def contact():
    service = request.args.get('service', 'general')
    return render_template('contact.html', 
                         profile={}, 
                         service=service,
                         counties=KENYAN_COUNTIES,
                         mabati_options=MABATI_OPTIONS,
                         roofing_essentials=ROOFING_ESSENTIALS)

# ========== ADMIN AUTH ROUTES ==========
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.info(f"🔐 Login attempt - Username: {username}")
        
        # Simple hardcoded admin for testing (REMOVE IN PRODUCTION)
        if username == 'antony' and password == 'antony123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_name'] = 'Antony Mutia'
            session.permanent = True
            logger.info(f"✅ Login successful for: {username}")
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/login.html', error='Invalid credentials')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    username = session.get('admin_username', 'Unknown')
    session.clear()
    logger.info(f"👋 Logout for: {username}")
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html', 
                         profile={},
                         stats={
                             'projects': 0,
                             'inquiries': 0,
                             'services': 4,
                             'admins': 1
                         })

@app.route('/admin/projects')
@admin_required
def admin_projects():
    return render_template('admin/projects.html', 
                         projects=[],
                         services=[])

@app.route('/admin/project-edit', methods=['GET', 'POST'])
@admin_required
def admin_project_edit():
    project_id = request.args.get('id')
    return render_template('admin/project-edit.html',
                         project=None,
                         services=[],
                         counties=KENYAN_COUNTIES,
                         mabati_options=MABATI_OPTIONS,
                         roofing_essentials=ROOFING_ESSENTIALS,
                         cloudinary_cloud_name=app.config['CLOUDINARY_CLOUD_NAME'])

@app.route('/admin/services')
@admin_required
def admin_services():
    return render_template('admin/services.html', services=[])

@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    return render_template('admin/profile.html', 
                         profile={},
                         counties=KENYAN_COUNTIES)

@app.route('/admin/inquiries')
@admin_required
def admin_inquiries():
    return render_template('admin/inquiries.html', inquiries=[])

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return render_template('admin/analytics.html', visits={})

# ========== CLOUDINARY API ROUTES ==========
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
    
    try:
        upload_options = {
            'folder': f'tonnie-roofing/{folder}',
            'resource_type': 'image',
            'overwrite': True
        }
        if public_id:
            upload_options['public_id'] = public_id
        
        result = cloudinary.uploader.upload(file, **upload_options)
        return jsonify({
            'success': True,
            'public_id': result['public_id'],
            'url': result['secure_url']
        })
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/admin/delete-image', methods=['POST'])
@admin_required
def delete_image():
    data = request.get_json()
    public_id = data.get('public_id')
    
    if not public_id:
        return jsonify({'error': 'No public_id provided'}), 400
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result['result'] == 'ok':
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Delete failed'}), 500
    except Exception as e:
        logger.error(f"Cloudinary delete error: {e}")
        return jsonify({'error': 'Delete failed'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
    app.run(debug=False, host='0.0.0.0', port=port)
