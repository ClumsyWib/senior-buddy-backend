from decouple import config
import pymysql
pymysql.install_as_MySQLdb()

from pathlib import Path

# =====================================================
# SENIOR BUDDY — settings.py
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------
# SECURITY
# Change SECRET_KEY before going live — never share it
# -------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='yuvi')

# Set to False before going live
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.railway.app']
    # Add your IP here if testing from Android device on same WiFi
    # e.g. '192.168.1.10',



# -------------------------------------------------------
# INSTALLED APPS
# jazzmin must come before django.contrib.admin
# -------------------------------------------------------
INSTALLED_APPS = [
    'jazzmin',                              # Admin UI skin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',                           # Django REST Framework
    'rest_framework_simplejwt',                 # JWT tokens for Android login
    'rest_framework_simplejwt.token_blacklist', # For logout functionality
    'corsheaders',                              # Allow Android app to connect
    'drf_spectacular',                          # Auto API documentation

    # Our app
    'senior_buddy',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',    # Must be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'senior_buddy_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'senior_buddy_project.wsgi.application'


# -------------------------------------------------------
# DATABASE — MySQL
# Change PASSWORD to your MySQL root password
# -------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'senior_buddy_db',
        'USER':     'root',
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),   # ← Change this to your MySQL root password
        'HOST':     'localhost',
        'PORT':     '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# -------------------------------------------------------
# CUSTOM USER MODEL
# Tells Django to use our User model instead of its own
# -------------------------------------------------------
AUTH_USER_MODEL = 'senior_buddy.User'


# -------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------------------------------------------
# INTERNATIONALISATION
# -------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'    # IST — change if needed
USE_I18N      = True
USE_TZ        = False 


# -------------------------------------------------------
# STATIC FILES
# -------------------------------------------------------
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -------------------------------------------------------
# DJANGO REST FRAMEWORK
# -------------------------------------------------------
REST_FRAMEWORK = {
    # All endpoints require login by default
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Auto API documentation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Pagination — returns 20 results per page
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}


# -------------------------------------------------------
# JWT TOKEN SETTINGS
# Access token lasts 1 day, refresh token lasts 7 days
# Android stores the access token and uses it in headers
# -------------------------------------------------------
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES':      ('Bearer',),
}


# -------------------------------------------------------
# CORS — Allows Android app to call the API
# During development, allow all origins
# -------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True    # Change to False in production


# -------------------------------------------------------
# API DOCUMENTATION
# Visit http://127.0.0.1:8000/api/schema/swagger/
# -------------------------------------------------------
SPECTACULAR_SETTINGS = {
    'TITLE':       'Senior Buddy API',
    'DESCRIPTION': 'Backend API for the Senior Buddy eldercare app',
    'VERSION':     '1.0.0',
}


# -------------------------------------------------------
# JAZZMIN — Admin Panel UI
# -------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title":        "Senior Buddy Admin",
    "site_header":       "Senior Buddy",
    "site_brand":        "Senior Buddy",
    "welcome_sign":      "Welcome to Senior Buddy Admin Panel",
    "copyright":         "Senior Buddy",

    "topmenu_links": [
        {"name": "Home",   "url": "admin:index"},
        {"name": "Users",  "url": "admin:senior_buddy_user_changelist"},
        {"name": "SOS",    "url": "admin:senior_buddy_sosrequest_changelist"},
        {"name": "Events", "url": "admin:senior_buddy_communityevent_changelist"},
    ],

    "order_with_respect_to": [
        "senior_buddy.user", "senior_buddy.role", "senior_buddy.userrole",
        "senior_buddy.seniorprofile", "senior_buddy.caregiverprofile",
        "senior_buddy.familyprofile", "senior_buddy.volunteerprofile",
        "senior_buddy.seniorcaregiver", "senior_buddy.seniorfamily",
        "senior_buddy.seniorvolunteer", "senior_buddy.doctor",
        "senior_buddy.seniordoctor", "senior_buddy.reminder",
        "senior_buddy.healthnote", "senior_buddy.sosrequest",
        "senior_buddy.communityevent", "senior_buddy.eventattendance",
        "senior_buddy.chatmessage", "senior_buddy.activitylog",
    ],

    "icons": {
        "senior_buddy.user":             "fas fa-user",
        "senior_buddy.role":             "fas fa-id-badge",
        "senior_buddy.userrole":         "fas fa-user-tag",
        "senior_buddy.seniorprofile":    "fas fa-user-circle",
        "senior_buddy.caregiverprofile": "fas fa-user-nurse",
        "senior_buddy.familyprofile":    "fas fa-home",
        "senior_buddy.volunteerprofile": "fas fa-hands-helping",
        "senior_buddy.seniorcaregiver":  "fas fa-link",
        "senior_buddy.seniorfamily":     "fas fa-heart",
        "senior_buddy.seniorvolunteer":  "fas fa-handshake",
        "senior_buddy.doctor":           "fas fa-user-md",
        "senior_buddy.seniordoctor":     "fas fa-stethoscope",
        "senior_buddy.reminder":         "fas fa-bell",
        "senior_buddy.healthnote":       "fas fa-notes-medical",
        "senior_buddy.sosrequest":       "fas fa-ambulance",
        "senior_buddy.communityevent":   "fas fa-calendar-alt",
        "senior_buddy.eventattendance":  "fas fa-clipboard-check",
        "senior_buddy.chatmessage":      "fas fa-comments",
        "senior_buddy.activitylog":      "fas fa-history",
    },

    "default_icon_parents":  "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "show_sidebar":           True,
    "navigation_expanded":    True,
    "related_modal_active":   True,
    "show_ui_builder":        False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-indigo",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "minty",
    "dark_mode_theme": None,
    "button_classes": {
        "primary":   "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
}
# Static files for Railway
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
