# config.py
import os
from dotenv import load_dotenv

load_dotenv()

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

# Kenyan counties
KENYAN_COUNTIES = [
    "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo Marakwet", "Embu", "Garissa",
    "Homa Bay", "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi",
    "Kirinyaga", "Kisii", "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu",
    "Machakos", "Makueni", "Mandera", "Marsabit", "Meru", "Migori", "Mombasa",
    "Murang'a", "Nairobi", "Nakuru", "Nandi", "Narok", "Nyamira", "Nyandarua",
    "Nyeri", "Samburu", "Siaya", "Taita Taveta", "Tana River", "Tharaka Nithi",
    "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
]

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    if database_url and 'sslmode' not in database_url:
        database_url += '?sslmode=require'
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    # Admin
    MAX_ADMINS = int(os.getenv('MAX_ADMINS', 2))
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = '/tmp/flask-sessions'
