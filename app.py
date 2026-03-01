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
from dotenv import load_dotenv

# Import database extensions and models
from extensions import db, migrate
from models import Admin, Profile, Service, Project, Inquiry, Setting
from models import MABATI_OPTIONS as DEFAULT_MABATI, ROOFING_ESSENTIALS as DEFAULT_ESSENTIALS, KENYAN_COUNTIES as DEFAULT_COUNTIES

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
session.init_app(app)
migrate.init_app(app, db)

# Import models
from models import Admin, Profile, Service, Project, Inquiry, Setting

# ========== CONFIGURATION ==========
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = '/tmp/flask-sessions'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tonnie.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
Session(app)
db.init_app(app)
migrate.init_app(app, db)

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# ========== HELPER FUNCTIONS ==========

def get_profile():
    """Get or create profile singleton"""
    profile = Profile.query.get(1)
    if not profile:
        profile = Profile(id=1)
        db.session.add(profile)
        db.session.commit()
    return profile

def get_settings():
    """Get or create settings singleton"""
    settings = Setting.query.get(1)
    if not settings:
        settings = Setting(id=1)
        db.session.add(settings)
        db.session.commit()
    return settings

def process_image_urls(profile=None, services=None, projects=None):
    """Add Cloudinary URLs to data"""
    if profile:
        if profile.company_logo:
            profile.company_logo_url = cloudinary.CloudinaryImage(profile.company_logo).build_url(width=200, crop='scale', secure=True)
        if profile.hero_image:
            profile.hero_image_url = cloudinary.CloudinaryImage(profile.hero_image).build_url(secure=True)
        if profile.ceo_photo:
            profile.ceo_photo_url = cloudinary.CloudinaryImage(profile.ceo_photo).build_url(width=400, height=400, crop='fill', secure=True)
    
    if services:
        for service in services:
            if service.image:
                service.image_url = cloudinary.CloudinaryImage(service.image).build_url(width=400, height=200, crop='fill', secure=True)
            if service.detail_image:
                service.detail_image_url = cloudinary.CloudinaryImage(service.detail_image).build_url(width=600, height=400, crop='fill', secure=True)
    
    if projects:
        for project in projects:
            if project.images:
                for img in project.images:
                    if img.get('path'):
                        img['url'] = cloudinary.CloudinaryImage(img['path']).build_url(secure=True)
                    if img.get('thumbnail'):
                        img['thumbnail_url'] = cloudinary.CloudinaryImage(img['thumbnail']).build_url(width=100, height=70, crop='fill', secure=True)
    return profile, services, projects

# ========== AUTHENTICATION (TEMPORARILY DISABLED) ==========
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TEMPORARILY DISABLED FOR MIGRATION
        # if not session.get('admin_logged_in'):
        #     return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== PUBLIC ROUTES ==========

@app.route('/')
def index():
    profile = get_profile()
    services = Service.query.filter_by(active=True).order_by(Service.order).all()
    projects = Project.query.filter_by(featured=True).limit(4).all()
    settings = get_settings()
    
    profile, services, projects = process_image_urls(profile, services, projects)
    
    return render_template('index.html',
                         profile=profile,
                         services=services,
                         projects=projects,
                         mabati_options=settings.mabati_options)

@app.route('/services')
def services():
    profile = get_profile()
    services = Service.query.filter_by(active=True).order_by(Service.order).all()
    profile, services, _ = process_image_urls(profile, services)
    
    return render_template('services.html',
                         profile=profile,
                         services=services)

@app.route('/projects')
def projects():
    profile = get_profile()
    service_filter = request.args.get('service', 'all')
    
    if service_filter == 'all':
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        projects = Project.query.join(Service).filter(Service.slug == service_filter).order_by(Project.created_at.desc()).all()
    
    services = Service.query.filter_by(active=True).all()
    settings = get_settings()
    profile, services, projects = process_image_urls(profile, services, projects)
    
    return render_template('projects.html',
                         profile=profile,
                         projects=projects,
                         services=services,
                         service=service_filter,
                         counties=settings.kenyan_counties)

@app.route('/project')
def project_detail():
    profile = get_profile()
    project_id = request.args.get('id')
    project = Project.query.get(project_id)
    services = Service.query.all()
    
    if not project:
        return redirect(url_for('projects'))
    
    profile, services, projects = process_image_urls(profile, services, [project])
    
    # Get related projects (same service, different)
    related = Project.query.filter(
        Project.service_id == project.service_id,
        Project.id != project.id
    ).limit(3).all()
    
    return render_template('project.html',
                         profile=profile,
                         project=project,
                         related=related)

@app.route('/profile')
def company_profile():
    profile = get_profile()
    services = Service.query.filter_by(active=True).all()
    profile, services, _ = process_image_urls(profile, services)
    
    return render_template('profile.html',
                         profile=profile,
                         services=services)

@app.route('/contact')
def contact():
    profile = get_profile()
    settings = get_settings()
    service = request.args.get('service', 'general')
    
    return render_template('contact.html',
                         profile=profile,
                         service=service,
                         counties=settings.kenyan_counties,
                         mabati_options=settings.mabati_options,
                         roofing_essentials=settings.roofing_essentials)

# ========== ADMIN ROUTES ==========

@app.route('/admin')
def admin_index():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    settings = get_settings()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        
        if admin:
            session.clear()
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['admin_username'] = username
            session['admin_name'] = admin.full_name
            session.permanent = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html',
                                 error='Invalid credentials',
                                 admin_count=settings.admin_count,
                                 max_admins=settings.max_admins)
    
    return render_template('admin/login.html',
                         admin_count=settings.admin_count,
                         max_admins=settings.max_admins)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ========== ADMIN DASHBOARD ==========

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    profile = get_profile()
    stats = {
        'projects': Project.query.count(),
        'inquiries': Inquiry.query.filter_by(status='unread').count(),
        'services': Service.query.filter_by(active=True).count(),
        'admins': Admin.query.count()
    }
    return render_template('admin/dashboard.html', profile=profile, stats=stats)

# ========== PROJECT MANAGEMENT ==========

@app.route('/admin/projects')
@admin_required
def admin_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    services = Service.query.all()
    return render_template('admin/projects.html', projects=projects, services=services)

@app.route('/admin/project-edit', methods=['GET', 'POST'])
@admin_required
def admin_project_edit():
    project_id = request.args.get('id')
    project = None
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            if project_id:
                project = Project.query.get(project_id)
            else:
                project = Project(id=str(uuid.uuid4())[:8])
            
            # Update project fields
            project.title = data.get('title')
            project.service_id = data.get('service_id')
            project.featured = data.get('featured', False)
            project.short_description = data.get('short_description')
            project.full_description = data.get('full_description')
            
            # Location
            location = data.get('location', {})
            project.location_county = location.get('county')
            project.location_area = location.get('area')
            project.location_exact = location.get('exact')
            project.location_landmark = location.get('landmark')
            
            # Dates
            dates = data.get('dates', {})
            project.date_start = dates.get('start')
            project.date_end = dates.get('end')
            
            # Images
            project.images = data.get('images', [])
            
            # Roofing specific
            project.roof_type = data.get('roof_type')
            project.roofing_sheets = data.get('roofing_sheets')
            project.advantage = data.get('advantage')
            project.warranty = data.get('warranty')
            
            # Materials and process
            project.materials = data.get('materials', [])
            project.process = data.get('process', [])
            
            # Other
            project.property_type = data.get('property_type')
            project.client_name = data.get('client_name')
            project.project_value = data.get('project_value')
            project.tags = data.get('tags', [])
            project.status = data.get('status', 'active')
            
            if not project_id:
                db.session.add(project)
            
            db.session.commit()
            return jsonify({'success': True, 'id': project.id})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request
    if project_id:
        project = Project.query.get(project_id)
    
    services = Service.query.all()
    settings = get_settings()
    
    return render_template('admin/project-edit.html',
                         project=project,
                         services=services,
                         counties=settings.kenyan_counties,
                         mabati_options=settings.mabati_options,
                         roofing_essentials=settings.roofing_essentials,
                         cloudinary_cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'))

@app.route('/admin/project-delete/<project_id>', methods=['POST'])
@admin_required
def admin_project_delete(project_id):
    try:
        project = Project.query.get(project_id)
        if project:
            db.session.delete(project)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== SERVICE MANAGEMENT ==========

@app.route('/admin/services')
@admin_required
def admin_services():
    services = Service.query.order_by(Service.order).all()
    return render_template('admin/services.html', services=services)

@app.route('/admin/service-edit', methods=['POST'])
@admin_required
def admin_service_edit():
    try:
        data = request.get_json()
        service_id = data.get('id')
        
        if service_id:
            service = Service.query.get(service_id)
        else:
            service = Service(id=str(uuid.uuid4())[:8])
            db.session.add(service)
        
        service.name = data.get('name')
        service.slug = data.get('slug')
        service.icon = data.get('icon')
        service.short_description = data.get('short_description')
        service.full_description = data.get('full_description')
        service.features = data.get('features', [])
        service.active = data.get('active', True)
        service.color = data.get('color')
        service.order = data.get('order', 0)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/service-delete/<service_id>', methods=['POST'])
@admin_required
def admin_service_delete(service_id):
    try:
        service = Service.query.get(service_id)
        if service:
            db.session.delete(service)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Service not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== PROFILE MANAGEMENT ==========

@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    profile = get_profile()
    settings = get_settings()
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Update profile fields
            profile.company_name = data.get('company_name')
            profile.tagline = data.get('tagline')
            profile.description = data.get('description')
            profile.active_since = data.get('active_since')
            
            # CEO info
            ceo = data.get('ceo', {})
            profile.ceo_name = ceo.get('name')
            profile.ceo_title = ceo.get('title')
            profile.ceo_bio = ceo.get('bio')
            profile.ceo_phone = ceo.get('phone')
            profile.ceo_email = ceo.get('email')
            
            # Contact
            contact = data.get('contact', {})
            profile.contact_phone = contact.get('phone')
            profile.contact_whatsapp = contact.get('whatsapp')
            profile.contact_emergency = contact.get('emergency')
            profile.contact_email = contact.get('email')
            profile.contact_email2 = contact.get('email2')
            
            # Social
            profile.social = data.get('social', [])
            
            # Address
            address = data.get('address', {})
            profile.address_street = address.get('street')
            profile.address_city = address.get('city')
            profile.address_county = address.get('county')
            profile.address_country = address.get('country')
            profile.address_po_box = address.get('po_box')
            
            # Hours
            hours = data.get('hours', {})
            profile.hours_weekdays = hours.get('weekdays')
            profile.hours_saturday = hours.get('saturday')
            profile.hours_sunday = hours.get('sunday')
            profile.hours_emergency = hours.get('emergency')
            profile.hours_repairs = hours.get('repairs')
            
            # Stats
            stats = data.get('stats', {})
            profile.stats_projects = stats.get('projects_completed')
            profile.stats_clients = stats.get('happy_clients')
            profile.stats_years = stats.get('years_experience')
            profile.stats_workers = stats.get('skilled_workers')
            profile.stats_counties = stats.get('counties_served')
            
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('admin/profile.html',
                         profile=profile,
                         counties=settings.kenyan_counties)

# ========== INQUIRY MANAGEMENT ==========

@app.route('/admin/inquiries')
@admin_required
def admin_inquiries():
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template('admin/inquiries.html', inquiries=inquiries)

@app.route('/admin/inquiry/<inquiry_id>', methods=['GET', 'POST'])
@admin_required
def admin_inquiry_detail(inquiry_id):
    inquiry = Inquiry.query.get(inquiry_id)
    
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')
        
        if action == 'mark_read':
            inquiry.status = 'read'
            inquiry.read_at = datetime.utcnow()
        elif action == 'mark_replied':
            inquiry.status = 'replied'
            inquiry.replied_at = datetime.utcnow()
        elif action == 'archive':
            inquiry.status = 'archived'
        
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify(inquiry.to_dict() if inquiry else {'error': 'Not found'})

# ========== ANALYTICS ==========

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    # Basic analytics from database
    total_projects = Project.query.count()
    total_inquiries = Inquiry.query.count()
    unread_inquiries = Inquiry.query.filter_by(status='unread').count()
    
    # Projects by service
    projects_by_service = db.session.query(
        Service.name, db.func.count(Project.id)
    ).join(Project, isouter=True).group_by(Service.id).all()
    
    return render_template('admin/analytics.html',
                         total_projects=total_projects,
                         total_inquiries=total_inquiries,
                         unread_inquiries=unread_inquiries,
                         projects_by_service=projects_by_service)

# ========== CLOUDINARY API ROUTES ==========

@app.route('/admin/upload-image', methods=['POST'])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    folder = request.form.get('folder', 'projects')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=f'tonnie-roofing/{folder}',
            resource_type='image',
            overwrite=True
        )
        return jsonify({
            'success': True,
            'public_id': result['public_id'],
            'url': result['secure_url']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': 'Delete failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== DATABASE INIT ==========

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    db.create_all()
    
    # Create default admin if none exists
    if Admin.query.count() == 0:
        admin = Admin(
            id='admin_001',
            username='antony',
            password='antony123',
            full_name='Antony Mutia',
            email='antonymutie7@gmail.com'
        )
        db.session.add(admin)
        
        admin2 = Admin(
            id='admin_002',
            username='admin',
            password='admin123',
            full_name='Admin User',
            email='admin@tonnieroofing.co.ke'
        )
        db.session.add(admin2)
    
    # Create default profile
    if Profile.query.count() == 0:
        profile = Profile(id=1)
        db.session.add(profile)
    
    # Create default settings
    if Setting.query.count() == 0:
        settings = Setting(id=1)
        db.session.add(settings)
    
    # Create default services
    if Service.query.count() == 0:
        services = [
            Service(
                id='serv_001', name='Roofing', slug='roofing', icon='🏠',
                color='#0066cc', order=1,
                short_description='Professional roof installation and maintenance',
                features=['New roof installation', 'Roof replacement', 'Leak repairs']
            ),
            Service(
                id='serv_002', name='Interior Design', slug='interior', icon='✨',
                color='#7b1fa2', order=2,
                short_description='Modern interior design solutions',
                features=['Gypsum ceilings', 'Wall partitions', 'Custom fittings']
            ),
            Service(
                id='serv_003', name='Repairs', slug='repairs', icon='🔧',
                color='#c62828', order=3,
                short_description='Professional repair services',
                features=['Roof leak repairs', 'Ceiling repairs', 'Maintenance']
            ),
            Service(
                id='serv_004', name='Quoting Service', slug='quoting', icon='📋',
                color='#ef6c00', order=4,
                short_description='Detailed project quotes',
                features=['Project assessment', 'Material calculation', 'Cost estimation']
            )
        ]
        db.session.add_all(services)
    
    db.session.commit()
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    app.run(debug=True)
