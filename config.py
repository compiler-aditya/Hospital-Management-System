import os
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    database_url = os.environ.get('DATABASE_URL', '')
    
    if database_url:
        # Convert to pg8000 dialect
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
        
        # Remove ALL query parameters from URL (pg8000 handles ssl via connect_args)
        parsed = urlparse(database_url)
        clean_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '', '', ''  # remove params, query, fragment
        ))
        
        SQLALCHEMY_DATABASE_URI = clean_url
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {
                'ssl_context': True  # enables SSL for Neon
            }
        }
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'hospital.db')
        SQLALCHEMY_ENGINE_OPTIONS = {}
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False