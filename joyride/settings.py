from django.conf import settings

JOYRIDE_LIB = 'joyride/js/jquery.joyride-2.1.min.js'

JOYRIDE_JQUERY_URL = getattr(
    settings, 'JOYRIDE_JQUERY_URL',
    'joyride/js/jquery-1.10.1.min.js')
    
JOYRIDE_JQUERY_MODERNIZR_URL = getattr(
    settings, 'JOYRIDE_JQUERY_MODERNIZR_URL',
    'joyride/js/modernizr.mq.min.js')
    
JOYRIDE_JQUERY_COOKIE_URL = getattr(
    settings, 'JOYRIDE_JQUERY_COOKIE_URL',
    'joyride/js/jquery.cookie.min.js')
    
JOYRIDE_LIB_URL = getattr(
    settings, 'JOYRIDE_LIB_URL',
    JOYRIDE_LIB)

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
