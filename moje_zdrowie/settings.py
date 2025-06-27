"""
Poprawione ustawienia Django dla django-tenants
"""
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# WAŻNE: Dodaj localhost do ALLOWED_HOSTS
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'tenant1.localhost']

# Aplikacje shared (w public schema)
SHARED_APPS = [
    'django_tenants',  # MUSI być pierwsza!
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Twoje shared apps
    'customers',  # Model tenants
]

# Aplikacje tenant (w każdym tenant schema)
TENANT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Twoje tenant apps
    'accounts',
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # MUSI być pierwszy!
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# KLUCZOWE: Konfiguracja URL patterns
ROOT_URLCONF = 'moje_zdrowie.urls_public'  # Dla public schema (127.0.0.1:8000)

# Baza danych
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

# Konfiguracja tenants
TENANT_MODEL = 'customers.Client'
TENANT_DOMAIN_MODEL = 'customers.Domain'

# KLUCZOWE: Konfiguracja schematów
PUBLIC_SCHEMA_NAME = 'public'
PUBLIC_SCHEMA_URLCONF = 'moje_zdrowie.urls_public'    # URLs dla public schema
TENANT_URLCONF = 'moje_zdrowie.urls_tenant'           # URLs dla tenant schemas

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Dodaj ścieżkę do templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'moje_zdrowie.wsgi.application'

# Walidatory haseł
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internacjonalizacja
LANGUAGE_CODE = 'pl'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_TZ = True

# Statyczne pliki
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MEDIA files (opcjonalne)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ustawienia logowania
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Sesje
SESSION_COOKIE_AGE = 86400  # 24 godziny
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False



def patch_tenant_middleware():
    """Naprawa middleware django-tenants"""
    import django_tenants.middleware.main
    from django.conf import settings as django_settings
    
    original_process_request = django_tenants.middleware.main.TenantMainMiddleware.process_request
    
    def fixed_process_request(self, request):
        result = original_process_request(self, request)
        
        # FORCE ustaw URLconf jeśli nie został ustawiony
        if hasattr(request, 'tenant') and not getattr(request, 'urlconf', None):
            tenant = request.tenant
            public_schema = getattr(django_settings, 'PUBLIC_SCHEMA_NAME', 'public')
            
            if tenant.schema_name == public_schema:
                urlconf = getattr(django_settings, 'PUBLIC_SCHEMA_URLCONF', django_settings.ROOT_URLCONF)
            else:
                urlconf = getattr(django_settings, 'TENANT_URLCONF', django_settings.ROOT_URLCONF)
            
            request.urlconf = urlconf
            
            if DEBUG:
                print(f"🔧 FIXED: {request.META.get('HTTP_HOST')} -> {urlconf}")
        
        return result
    
    django_tenants.middleware.main.TenantMainMiddleware.process_request = fixed_process_request

# Uruchom patch
patch_tenant_middleware()