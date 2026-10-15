from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY', default='change-me')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'apps.tenants',
    'apps.knowledge_bases',
    'apps.documents',
    'apps.retrieval',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = env('DATABASE_URL', default='sqlite:///')
if env.bool('USE_SQLITE', default=False) or DATABASE_URL.startswith('sqlite'):
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
else:
    DATABASES = {'default': env.db('DATABASE_URL')}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.tenants.authentication.ApiKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'RAG Core API',
    'DESCRIPTION': 'Multi-tenant knowledge ingestion and retrieval API.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

EMBEDDING_PROVIDER = env('EMBEDDING_PROVIDER', default='openai')
EMBEDDING_MODEL = env('EMBEDDING_MODEL', default='text-embedding-3-small')
EMBEDDING_API_URL = env('EMBEDDING_API_URL', default='https://api.openai.com/v1/embeddings')
EMBEDDING_API_KEY = env('EMBEDDING_API_KEY', default='')
EMBEDDING_DIMENSIONS = env.int('EMBEDDING_DIMENSIONS', default=1536)
EMBEDDING_TIMEOUT_SECONDS = env.int('EMBEDDING_TIMEOUT_SECONDS', default=30)
EMBEDDING_BATCH_SIZE = env.int('EMBEDDING_BATCH_SIZE', default=16)
MAX_UPLOAD_SIZE_MB = env.int('MAX_UPLOAD_SIZE_MB', default=20)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
DEFAULT_CHUNK_SIZE = env.int('DEFAULT_CHUNK_SIZE', default=500)
DEFAULT_CHUNK_OVERLAP = env.int('DEFAULT_CHUNK_OVERLAP', default=80)
DEFAULT_TOP_K = env.int('DEFAULT_TOP_K', default=5)
DEFAULT_SIMILARITY_THRESHOLD = env.float('DEFAULT_SIMILARITY_THRESHOLD', default=0.0)
API_KEY_PREFIX = env('API_KEY_PREFIX', default='rag_')
API_KEY_LENGTH = env.int('API_KEY_LENGTH', default=32)

UPLOAD_STORAGE_DIR = BASE_DIR / 'storage' / 'uploads'
UPLOAD_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
