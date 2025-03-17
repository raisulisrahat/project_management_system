from django.utils import timezone
import pytz

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the timezone is set in the session
        timezone_str = request.session.get('django_timezone')
        if timezone_str:
            timezone.activate(pytz.timezone(timezone_str))
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
