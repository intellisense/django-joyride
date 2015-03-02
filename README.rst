django-joyride
==============

A django application which gives flexibility to configure Guided Tours
on your site through admin panel.

-  This application is built on top of jQuery plugin `zurb-joyride <https://github.com/zurb/joyride>`__.

Installation
============

-  Install from PyPI with ``easy_install`` or ``pip``:

  ::

     pip install django-joyride

-  To use ``django-joyride`` in your Django project:

  1.  Add ``joyride`` to your ``INSTALLED_APPS`` setting.
  2.  Run ``syncdb`` command to initialise the ``joyride`` database tables
  3.  Run ``collectstatic`` command to collect the static files of joyride
      into ``STATIC_ROOT``

Configuration
=============

Available settings:

-  ``JOYRIDE_JQUERY_URL``
 -  Set this to different version of jquery in your static folder, If you
    wish to use a different version of jQuery, or host it yourself

-  e.g. ``JOYRIDE_JQUERY_URL = 'joyride/js/jquery.min.js'`` This will
   use the jQuery available at ``STATIC_URL/joyride/js/jquery.min.js``.   A relative ``JOYRIDE_JQUERY_URL`` is relative to ``STATIC_URL``.

 -  Set this to ``None`` if you have already included jQuery in your
    template so that ``joyride_media`` and ``joyride_js`` template tag
    should not include jQuery to avoid conflict.

  -  e.g. ``JOYRIDE_JQUERY_URL = None``

-  ``JOYRIDE_JQUERY_COOKIE_URL``
 -  Same settings as ``JOYRIDE_JQUERY_URL``, it decide whether to include
    or not to include the ``jquery.cookie.js``. This should be included
    if you are going to use the ``zurb-joyride`` option ``cookieMonster``

-  ``JOYRIDE_JQUERY_MODERNIZR_URL``
 -  Same settings as ``JOYRIDE_JQUERY_URL``, it decide whether to include
    or not to include the jquery modernizr.

-  ``JOYRIDE_LIB_URL``
 -  Set this to use latest version of ``zurb-joyride`` js library
    instead. This package already contains this library with some bug
    fixes. It is strongly suggested that you should not change this
    setting until ``zurb-joyride`` apply some fixes which I have posted
    there, check status of `Issue 161 <https://github.com/zurb/joyride/issues/161>`__    and `Issue 167 <https://github.com/zurb/joyride/issues/167>`__

Add joyride tours from admin
============================

-  The model and model fields are self explanatory. All model fields
   have help text for better understanding. Still if you want more
   documentation on it then check the comprehensive `documentation <http://zurb.com/playground/jquery-joyride-feature-tour-plugin>`__ on ``zurb-joyride``
-  Following model fields are extra and comes in handy:
 -  ``url_path``

  -  The url e.g. ``/about/`` or url regex ``/abc/\d+/`` of the page
     for which you are creating the joyride tour. Later on you can use
     this as a parameter in template tags to filter joyrides based on
     ``request.path``

 -  The **BOTTLENECK** of ``zurb-joyride``

  -  ``showJoyRideElement`` and ``showJoyRideElementOn`` fields
   -  Arrggh! it is not possible to use multiple joyrides on single page
      unless previous joyrides are destroyed. So in order to overcome
      that situation sometime you might want to activate the second
      joyride tour on some event. Lets say we want our second joyride to
      be activated when user ``click`` on some element whose id or class
      is ``abc`` then you need to set ``showJoyRideElement=#abc`` and
      ``showJoyRideElementOn=click``.
  -  ``destroy`` field
   -  IDs(slug) of joyrides which should be destroyed before invoking
      this joyride e.g. ``destroy=#abc, #cde``

Template Tags
=============

1. **Include The Media**

 -  Load the django-joyride template tags ``{% load joyride_tags %}``
 -  Include the media (css and js files) ``{% joyride_media %}``

  -  By default the ``joyride_media`` tag also includes ``jQuery``,
    ``jQuery Modernizer`` and ``jQuery Cookie`` based on the value of
    your ``JOYRIDE_JQUERY_URL``, ``JOYRIDE_JQUERY_MODERNIZR_URL`` and
    ``JOYRIDE_JQUERY_COOKIE_URL`` settings. To suppress the inclusion
    of these libraries (if you are already including it yourself), set
    these settings to ``None``.
    |
    If you prefer to link CSS and Javascript from different locations,
    the ``joyride_media`` tag can be replaced with two separate tags,
    ``joyride_css`` and ``joyride_js``. ``joyride_js`` accepts parameters
    to suppress jQuery, jQuery Modernizr and jQuery Cookie inclusion at
    template level also, just like ``joyride_media``

   -  e.g.
     ``{% joyride_js no_jquery="true" no_jquery_modernizr="true" %}``

1. **Include the joyride tour(s)**

 -  You need to use ``get_joyrides``, ``include_joyrides`` and
    ``get_joyride``, ``include_joyride`` to include multiple joyride
    tours or single joyride tour respectively in template.
 -  ``get_joyrides`` and ``get_joyride`` both tags accept parameters to
    filter the joyrides. Following filters are common in both:

  -  ``url_path`` filter joyrides by url path.
   -  e.g. ``{% get_joyrides url_path=request.path as joyrides %}``
   -  If you have left ``url_path`` empty while configuring joyride in
      admin then in order to get those joyride whose ``url_path`` is
      empty you would do ``{% get_joyrides url_path="" as joyrides %}``
  -  ``for_user`` filter joyrides by user if you are using
     ``JoyRideHistory`` model to keep track of joyrides with respect to
     user.
   -  e.g. ``{% get_joyrides for_user=request.user as joyrides %}`` #
      this will get all joyrides for user which are not viewed or
      cancelled by user.
  -  ``exclude_viewed`` (default=True) if you want to include all
     joyrides for user irrespective of seen/cancelled or not
   -  e.g.
    ``{% get_joyrides for_user=request.user exclude_viewed=False %}``
  -  ``slug`` only used with ``get_joyride`` to get single joyride.
   -  e.g. ``{% get_joyride "my-tour-slug" %}``

 -  Include Multiple joyrides

  ::

    {% get_joyrides as joyrides %}
    {% include_joyrides joyrides %}

 -  Include Single joyride

  ::

    {% get_joyride "my-tour-slug" as joyride %}
    {% include_joyride joyride %}

JoyRideHistory Model
====================

-  This model is only used if you have registered users on your site and
   you want to keep track of joyrides which are already viewed by user
   so that those joyrides should never be shown to user again. It is up
   to you how you are going to make use of this table. Below is an
   example:
   |
   Set ``postRideCallback=mark_viewed_joyride`` (A method to call once the
   tour closes (cancelled or complete)) in admin. Write the javascript
   callback ``mark_viewed_joyride`` some where in your template:
     ::
         function mark_joyride(index, tip, id){             $.ajax({                 url: '{% url mark_joyride %}',                 data: {"slug": id},                 dataType: 'text',                 success: function(){                     $("#"+id).remove(); // remove the element also from dom                 }             });         }

   The view for ``{% url mark_joyride %}`` would be:
     ::
         @login_required         def mark_joyride(request):             from joyride.models import JoyRide, JoyRideHistory             slug = request.GET.get('slug')             joyride = get_object_or_404(JoyRide, slug=slug)             user = request.user             obj, created = JoyRideHistory.objects.get_or_create(user=user, joyride=joyride)             if not created:                 obj.viewed = True                 obj.save()             return HttpResponse(json.dumps({}), content_type='application/json')
Thanks To
=========

-  `zurb-joyride <https://github.com/zurb/joyride>`__ This package is
   built on top of it.
-  `django-markitup <https://bitbucket.org/carljm/django-markitup/>`__
   for some help in template tags.
