from extensions import db
from datetime import datetime
import uuid

def generate_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())[:8]

# ========== STATIC DATA LISTS ==========
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

ROOFING_ESSENTIALS = [
    "Half Round Gutters - 0.45mm", "Half Round Gutters - 0.5mm",
    "Box Gutters - 0.5mm", "Box Gutters - 0.6mm", "Ogee Gutters",
    "Ridge Cap - Standard 150mm", "Ridge Cap - Wide 200mm",
    "Ridge Cap - Ventilated", "Ridge Cap - Decorative",
    "Wall Flashing - 0.4mm", "Barge Flashing - 0.4mm", "Valley Flashing - 0.5mm",
    "Apron Flashing", "Step Flashing",
    "Insulated Panel - 25mm", "Insulated Panel - 50mm", "Insulated Panel - 75mm", "Insulated Panel - 100mm"
]

KENYAN_COUNTIES = [
    "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo Marakwet", "Embu", "Garissa",
    "Homa Bay", "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi",
    "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu",
    "Machakos", "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa",
    "Murang'a", "Nairobi", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua",
    "Nyeri", "Samburu", "Siaya", "Taita Taveta", "Tana River", "Tharaka Nithi",
    "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
]

# ========== DATABASE MODELS ==========

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Profile(db.Model):
    __tablename__ = 'profile'
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    company_name = db.Column(db.String(100), default='Tonnie Roofing')
    company_logo = db.Column(db.String(200))
    hero_image = db.Column(db.String(200))
    tagline = db.Column(db.String(200), default='Professional Roofing & Interior Design Services')
    description = db.Column(db.Text)
    active_since = db.Column(db.String(10), default='2015')
    
    # CEO details
    ceo_name = db.Column(db.String(100), default='Antony Mutia')
    ceo_photo = db.Column(db.String(200))
    ceo_title = db.Column(db.String(100), default='Founder & CEO')
    ceo_bio = db.Column(db.Text)
    ceo_phone = db.Column(db.String(20), default='0712454146')
    ceo_email = db.Column(db.String(100), default='antonymutie7@gmail.com')
    
    # Contact
    contact_phone = db.Column(db.String(20), default='0712454146')
    contact_whatsapp = db.Column(db.String(20), default='0712454146')
    contact_emergency = db.Column(db.String(20), default='0712454146')
    contact_email = db.Column(db.String(100), default='antonymutie7@gmail.com')
    contact_email2 = db.Column(db.String(100), default='info@tonnieroofing.co.ke')
    
    # Social media as JSON
    social = db.Column(db.JSON, default=[
        {'platform': 'Facebook', 'icon': '📘', 'url': 'https://facebook.com/tonnieroofing', 'app_url': 'fb://page/tonnieroofing', 'active': True},
        {'platform': 'TikTok', 'icon': '🎵', 'url': 'https://tiktok.com/@tonnieroofing', 'app_url': 'tiktok://@tonnieroofing', 'active': True},
        {'platform': 'Instagram', 'icon': '📷', 'url': 'https://instagram.com/tonnieroofing', 'app_url': 'instagram://user?username=tonnieroofing', 'active': True},
        {'platform': 'WhatsApp', 'icon': '💬', 'url': 'https://wa.me/254712454146', 'app_url': 'whatsapp://send?phone=254712454146', 'active': True}
    ])
    
    # Address
    address_street = db.Column(db.String(200), default='Kilimani Business Centre')
    address_city = db.Column(db.String(100), default='Nairobi')
    address_county = db.Column(db.String(100), default='Nairobi')
    address_country = db.Column(db.String(100), default='Kenya')
    address_po_box = db.Column(db.String(100), default='PO Box 12345-00100')
    
    # Hours
    hours_weekdays = db.Column(db.String(100), default='8:00 AM - 6:00 PM')
    hours_saturday = db.Column(db.String(100), default='9:00 AM - 3:00 PM')
    hours_sunday = db.Column(db.String(100), default='Closed')
    hours_emergency = db.Column(db.String(100), default='Call 0712454146')
    hours_repairs = db.Column(db.String(100), default='Monday to Friday, 8:00 AM - 6:00 PM')
    
    # Stats
    stats_projects = db.Column(db.Integer, default=250)
    stats_clients = db.Column(db.Integer, default=150)
    stats_years = db.Column(db.Integer, default=8)
    stats_workers = db.Column(db.Integer, default=25)
    stats_counties = db.Column(db.Integer, default=47)

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(10))
    image = db.Column(db.String(200))
    detail_image = db.Column(db.String(200))
    short_description = db.Column(db.String(200))
    full_description = db.Column(db.Text)
    features = db.Column(db.JSON, default=[])
    active = db.Column(db.Boolean, default=True)
    project_count = db.Column(db.Integer, default=0)
    inquiry_count = db.Column(db.Integer, default=0)
    image_count = db.Column(db.Integer, default=0)
    color = db.Column(db.String(10))
    order = db.Column(db.Integer, default=0)
    
    # Relationships
    projects = db.relationship('Project', backref='service_ref', lazy=True, cascade='all, delete-orphan')

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    service_id = db.Column(db.String(20), db.ForeignKey('services.id', ondelete='SET NULL'))
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    featured = db.Column(db.Boolean, default=False)
    short_description = db.Column(db.String(200))
    full_description = db.Column(db.Text)
    
    # Location
    location_county = db.Column(db.String(100))
    location_area = db.Column(db.String(100))
    location_exact = db.Column(db.String(200))
    location_landmark = db.Column(db.String(200))
    
    # Dates
    date_start = db.Column(db.String(20))
    date_end = db.Column(db.String(20))
    
    # Images (JSON array)
    images = db.Column(db.JSON, default=[])
    
    # Roofing specific
    roof_type = db.Column(db.String(50))
    roofing_sheets = db.Column(db.String(100))
    advantage = db.Column(db.String(200))
    warranty = db.Column(db.String(50))
    
    # Materials (JSON array)
    materials = db.Column(db.JSON, default=[])
    
    # Process steps (JSON array)
    process = db.Column(db.JSON, default=[])
    
    # Other
    property_type = db.Column(db.String(50))
    client_name = db.Column(db.String(100))
    project_value = db.Column(db.String(50))
    tags = db.Column(db.JSON, default=[])
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    service = db.Column(db.String(50))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    location_county = db.Column(db.String(100))
    location_area = db.Column(db.String(100))
    status = db.Column(db.String(20), default='unread')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    replied_at = db.Column(db.DateTime)

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    admin_count = db.Column(db.Integer, default=0)
    max_admins = db.Column(db.Integer, default=2)
    site_name = db.Column(db.String(100), default='Tonnie Roofing')
    site_url = db.Column(db.String(200))
    maintenance_mode = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(10), default='1.0.0')
    
    # Store these as JSON to keep them editable
    mabati_options = db.Column(db.JSON, default=MABATI_OPTIONS)
    roofing_essentials = db.Column(db.JSON, default=ROOFING_ESSENTIALS)
    kenyan_counties = db.Column(db.JSON, default=KENYAN_COUNTIES)