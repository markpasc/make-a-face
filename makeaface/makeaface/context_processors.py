from django.conf import settings


def ganalytics(request):
    try:
        code = settings.GANALYTICS_CODE
    except AttributeError:
        return {}
    else:
        return {
            'ganalytics_code': code,
        }
