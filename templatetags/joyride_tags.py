import re

from django import template

from joyride import settings
from joyride.utils import absolute_url
from joyride.models import JoyRide

register = template.Library()


def _get_joyride_context():
    context = {
        'JOYRIDE_CSS_URL': absolute_url('joyride/css/joyride-2.1.css'),
        }
    if settings.JOYRIDE_JQUERY_URL is not None:
        context['JOYRIDE_JQUERY_URL'] = absolute_url(settings.JOYRIDE_JQUERY_URL)
    if settings.JOYRIDE_JQUERY_MODERNIZR_URL:
        context['JOYRIDE_JQUERY_MODERNIZR_URL'] = absolute_url(settings.JOYRIDE_JQUERY_MODERNIZR_URL)
    if settings.JOYRIDE_JQUERY_COOKIE_URL:
        context['JOYRIDE_JQUERY_COOKIE_URL'] = absolute_url(settings.JOYRIDE_JQUERY_COOKIE_URL)
    JOYRIDE_LIB_URL = settings.JOYRIDE_LIB_URL
    if not JOYRIDE_LIB_URL:
        JOYRIDE_LIB_URL = settings.JOYRIDE_LIB
    context['JOYRIDE_LIB_URL'] = absolute_url(JOYRIDE_LIB_URL)
    return context
register._joyride_context = _get_joyride_context()


@register.inclusion_tag('joyride/include_all.html')
def joyride_media(no_jquery=False, no_jquery_modernizr=False, no_jquery_cookie=False):
    include_jquery = not bool(no_jquery) and settings.JOYRIDE_JQUERY_URL is not None
    include_jquery_modernizr = not bool(no_jquery_modernizr) and settings.JOYRIDE_JQUERY_MODERNIZR_URL is not None
    include_jquery_cookie = not bool(no_jquery_cookie) and settings.JOYRIDE_JQUERY_COOKIE_URL is not None
    return dict(
        register._joyride_context,
        include_jquery=include_jquery,
        include_jquery_modernizr=include_jquery_modernizr,
        include_jquery_cookie=include_jquery_cookie
    )


@register.inclusion_tag('joyride/include_js.html')
def joyride_js(no_jquery=False, no_jquery_modernizr=False, no_jquery_cookie=False):
    include_jquery = not bool(no_jquery) and settings.JOYRIDE_JQUERY_URL is not None
    include_jquery_modernizr = not bool(no_jquery_modernizr) and settings.JOYRIDE_JQUERY_MODERNIZR_URL is not None
    include_jquery_cookie = not bool(no_jquery_cookie) and settings.JOYRIDE_JQUERY_COOKIE_URL is not None
    return dict(
        register._joyride_context,
        include_jquery=include_jquery,
        include_jquery_modernizr=include_jquery_modernizr,
        include_jquery_cookie=include_jquery_cookie
    )


@register.inclusion_tag('joyride/include_css.html')
def joyride_css():
    return register._joyride_context


@register.inclusion_tag('joyride/joyrides.html', takes_context=True)
def include_joyrides(context, joyrides):
    context.update({'joyrides': joyrides})
    return context


@register.inclusion_tag('joyride/joyride.html', takes_context=True)
def include_joyride(context, joyride):
    context.update({'joyride': joyride})
    return context


@register.assignment_tag
def get_joyrides(url_path=None, for_user=None, exclude_viewed=True):
    qs = JoyRide.objects.get_joyrides(
        url_path=url_path, for_user=for_user, exclude_viewed=exclude_viewed)
    return qs
    
    
@register.assignment_tag
def get_joyride(slug, url_path=None, for_user=None, viewed=False):
    return JoyRide.objects.get_joyride(
        slug, url_path=url_path, for_user=for_user, viewed=viewed)
