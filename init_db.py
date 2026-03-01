"""Initialize database tables"""
from app import app
from extensions import db
from models import Admin, Profile, Service, Project, Inquiry, Setting
import uuid
from datetime import datetime

def init_database():
    """Create tables and add initial data"""
    with app.app_context():
        # Create tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if settings exist
        if not Setting.query.filter_by(key='admin_count').first():
            Setting.set('admin_count', 0)
            Setting.set('max_admins', 2)
            Setting.set('site_name', 'Tonnie Roofing')
            Setting.set('version', '1.0.0')
            print("✅ Default settings created")
        
        # Check if services exist
        if Service.query.count() == 0:
            services = [
                {
                    'id': 'serv_001',
                    'name': 'Roofing',
                    'slug': 'roofing',
                    'icon': '🏠',
                    'short_description': 'Professional roof installation and maintenance',
                    'features': [
                        'New roof installation',
                        'Roof replacement & renovation',
                        'Leak repairs & maintenance',
                        'Roof inspections & assessments'
                    ],
                    'color': '#0066cc',
                    'order': 1
                },
                {
                    'id': 'serv_002',
                    'name': 'Interior Design',
                    'slug': 'interior',
                    'icon': '✨',
                    'short_description': 'Modern interior design solutions',
                    'features': [
                        'Gypsum ceiling installations',
                        'Custom wall fittings & partitions',
                        'Modern interior finishing',
                        'Space planning & design'
                    ],
                    'color': '#7b1fa2',
                    'order': 2
                },
                {
                    'id': 'serv_003',
                    'name': 'Repairs',
                    'slug': 'repairs',
                    'icon': '🔧',
                    'short_description': 'Professional repair services',
                    'features': [
                        'Roof leak repairs',
                        'Ceiling & wall repairs',
                        'Structural damage fixes',
                        'Regular maintenance packages'
                    ],
                    'color': '#c62828',
                    'order': 3
                },
                {
                    'id': 'serv_004',
                    'name': 'Quoting Service',
                    'slug': 'quoting',
                    'icon': '📋',
                    'short_description': 'Detailed project quotes',
                    'features': [
                        'Detailed project assessment',
                        'Material quantity calculations',
                        'Labor cost estimation',
                        'Timeline projections'
                    ],
                    'color': '#ef6c00',
                    'order': 4
                }
            ]
            
            for service_data in services:
                service = Service(**service_data)
                db.session.add(service)
            
            db.session.commit()
            print("✅ Default services created")

if __name__ == '__main__':
    init_database()
