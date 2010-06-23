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


def mobile(request):
    """
    Identifies whether the user agent string is for a 'mobile' class
    device and assigns a 'mobile' context variable appropriately.

    """
    if request.GET.get('mobile', None):
        return {'mobile': True}

    agent = request.META['HTTP_USER_AGENT']
    mobile = False
    if (('AppleWebKit' in agent) and ('Mobile' in agent or 'Pre' in agent or 'webOS' in agent)) or ('Opera Mini' in agent):
        if 'iPad' not in agent: # but not the iPad
            mobile = True
    return {
        'mobile': mobile
    }
