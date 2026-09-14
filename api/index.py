import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mongo_crud_project.settings')

import django
django.setup()

from django.core.management import call_command
try:
    call_command('collectstatic', interactive=False, verbosity=0)
except Exception as e:
    print(f"collectstatic warning: {e}")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()