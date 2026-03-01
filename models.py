"""Database models for Tonnie Roofing"""
from extensions import db
from datetime import datetime
import json

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), default='Tonnie Roofing')
    company_logo = db.Column(db.String(200))
    hero_image = db.Column(db.String(200))
    tagline = db.Column(db.String(200))
    description = db.Column(db.Text)
    active_since = db.Column(db.String(10), default='2015')
    
    # CEO Info
    ceo_name = db.Column(db.String(100))
    ceo_photo = db.Column(db.String(200))
    ceo_title = db.Column(db.String(100))
    ceo_bio = db.Column(db.Text)
    ceo_phone = db.Column(db.String(20))
    ceo_email = db.Column(db.String(100))
    
    # Contact
    contact_phone = db.Column(db.String(20))
    contact_whatsapp = db.Column(db.String(20))
    contact_emergency = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    contact_email2 = db.Column(db.String(100))
    
    # Address
    address_street = db.Column(db.String(200))
    address_city = db.Column(db.String(100))
    address_county = db.Column(db.String(100))
    address_country = db.Column(db.String(100))
    address_po_box = db.Column(db.String(100))
    
    # Hours
    hours_weekdays = db.Column(db.String(50))
    hours_saturday = db.Column(db.String(50))
    hours_sunday = db.Column(db.String(50))
    hours_emergency = db.Column(db.String(100))
    hours_repairs = db.Column(db.String(100))
    
    # Stats
    stats_projects = db.Column(db.Integer, default=0)
    stats_clients = db.Column(db.Integer, default=0)
    stats_years = db.Column(db.Integer, default=8)
    stats_workers = db.Column(db.Integer, default=0)
    stats_counties = db.Column(db.Integer, default=47)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'company_name': self.company_name,
            'company_logo': self.company_logo,
            'hero_image': self.hero_image,
            'tagline': self.tagline,
            'description': self.description,
            'active_since': self.active_since,
            'ceo': {
                'name': self.ceo_name,
                'photo': self.ceo_photo,
                'title': self.ceo_title,
                'bio': self.ceo_bio,
                'phone': self.ceo_phone,
                'email': self.ceo_email
            },
            'contact': {
                'phone': self.contact_phone,
                'whatsapp': self.contact_whatsapp,
                'emergency': self.contact_emergency,
                'email': self.contact_email,
                'email2': self.contact_email2
            },
            'address': {
                'street': self.address_street,
                'city': self.address_city,
                'county': self.address_county,
                'country': self.address_country,
                'po_box': self.address_po_box
            },
            'hours': {
                'weekdays': self.hours_weekdays,
                'saturday': self.hours_saturday,
                'sunday': self.hours_sunday,
                'emergency': self.hours_emergency,
                'repairs': self.hours_repairs
            },
            'stats': {
                'projects_completed': self.stats_projects,
                'happy_clients': self.stats_clients,
                'years_experience': self.stats_years,
                'skilled_workers': self.stats_workers,
                'counties_served': self.stats_counties
            }
        }

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(10))
    image = db.Column(db.String(200))
    detail_image = db.Column(db.String(200))
    short_description = db.Column(db.String(200))
    full_description = db.Column(db.Text)
    features = db.Column(db.JSON, default=list)
    active = db.Column(db.Boolean, default=True)
    project_count = db.Column(db.Integer, default=0)
    inquiry_count = db.Column(db.Integer, default=0)
    image_count = db.Column(db.Integer, default=0)
    color = db.Column(db.String(20))
    order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'icon': self.icon,
            'image': self.image,
            'detail_image': self.detail_image,
            'short_description': self.short_description,
            'full_description': self.full_description,
            'features': self.features,
            'active': self.active,
            'project_count': self.project_count,
            'inquiry_count': self.inquiry_count,
            'image_count': self.image_count,
            'color': self.color,
            'order': self.order
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.String(50), primary_key=True)
    service_id = db.Column(db.String(50), db.ForeignKey('services.id'))
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    featured = db.Column(db.Boolean, default=False)
    short_description = db.Column(db.String(300))
    full_description = db.Column(db.Text)
    
    # Location
    location_county = db.Column(db.String(100))
    location_area = db.Column(db.String(100))
    location_exact = db.Column(db.String(200))
    location_landmark = db.Column(db.String(200))
    
    # Dates
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    
    # Images (stored as JSON)
    images = db.Column(db.JSON, default=list)
    
    # Service specific fields (stored as JSON)
    details = db.Column(db.JSON, default=dict)
    
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = db.relationship('Service', backref='projects')
    
    def to_dict(self):
        service_name = self.service.name if self.service else None
        return {
            'id': self.id,
            'service_id': self.service_id,
            'service_name': service_name,
            'title': self.title,
            'slug': self.slug,
            'featured': self.featured,
            'short_description': self.short_description,
            'full_description': self.full_description,
            'location': {
                'county': self.location_county,
                'area': self.location_area,
                'exact': self.location_exact,
                'landmark': self.location_landmark
            },
            'dates': {
                'start': self.start_date,
                'end': self.end_date
            },
            'images': self.images,
            'details': self.details,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    service = db.Column(db.String(50))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    
    # Location
    location_county = db.Column(db.String(100))
    location_area = db.Column(db.String(100))
    
    status = db.Column(db.String(20), default='unread')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    replied_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'service': self.service,
            'subject': self.subject,
            'message': self.message,
            'location': {
                'county': self.location_county,
                'area': self.location_area
            },
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.JSON)
    
    @classmethod
    def get(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set(cls, key, value):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
