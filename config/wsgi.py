import os
# import newrelic.agent
from django.core.wsgi import get_wsgi_application
# newrelic.agent.initialize('.newrelic.ini')
# newrelic.agent.register_application()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
