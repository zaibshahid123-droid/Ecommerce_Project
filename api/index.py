import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mongo_crud_project.settings')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()