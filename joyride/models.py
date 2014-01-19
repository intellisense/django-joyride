import json

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_noop as _
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.core import serializers

try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from positions.fields import PositionField


class JoyRideManager(models.Manager):
    def get_joyrides(self, url_path=None, for_user=None, exclude_viewed=True):
        qs = super(JoyRideManager, self).get_query_set()
        if for_user and for_user.is_authenticated():
            viewed_qs = JoyRideHistory.objects.filter(user__id=for_user.id)
            if exclude_viewed:
                viewed_qs = viewed_qs.filter(viewed=True)
            viewed_qs_ids = viewed_qs.values_list('joyride__id', flat=True)
            qs = qs.exclude(id__in=viewed_qs_ids)
        if url_path is not None:
            qs = qs.filter(url_path__regex=r'^%s$' % url_path)
        return qs
    
    def get_joyride(self, slug, url_path=None, for_user=None, viewed=False):
        qs = super(JoyRideManager, self).get_query_set()
        kw = {'slug__exact': slug}
        if url_path is not None:
            kw.update({'url_path__regex': r'^%s$' % url_path})
        obj = qs.get(**kw)
        if for_user and for_user.is_authenticated():
            objv = obj.views.filter(user__id=for_user.id)
            if objv:
                objv = objv[0]
                if objv.viewed != viewed:
                    obj = None
        return obj


class JoyRide(models.Model):
    class Meta:
        verbose_name = _('Joy Ride')
        verbose_name_plural = _('Joy Rides')
        ordering = ['-created']
    
    TIP_LOCATION_TOP = 'top'
    TIP_LOCATION_BOTTOM = 'bottom'
    TIP_LOCATION_RIGHT = 'right'
    TIP_LOCATION_LEFT = 'left'
    TIP_LOCATION_CHOICES = (
        (TIP_LOCATION_TOP, _('top')),
        (TIP_LOCATION_BOTTOM, _('bottom')),
        (TIP_LOCATION_RIGHT, _('right')),
        (TIP_LOCATION_LEFT, _('left')),
    )
    
    TIP_ANIMATION_POP = 'pop'
    TIP_ANIMATION_FADE = 'fade'
    TIP_ANIMATION_CHOICES = (
        (TIP_ANIMATION_POP, _('pop')),
        (TIP_ANIMATION_FADE, _('fade')),
    )
    
    name = models.CharField(
        _('Joy Ride Name'),
        max_length=50,
        unique=True,
        help_text=_('This will be slugify automatically and will be used as ID for a joy ride'),
    )
    url_path = models.CharField(
        _('Page URL'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_('The url e.g. /about/ or url regex /abc/\d+/ of the page on which this joyride will be activated. \
        If left blank joyride will be activated on global scope')
    )
    slug = models.SlugField(editable=False)
    tipLocation = models.CharField(
        choices=TIP_LOCATION_CHOICES,
        default=TIP_LOCATION_BOTTOM,
        max_length=10,
        help_text=_('"top" or "bottom" in relation to parent'),
    )
    nubPosition = models.CharField(
        max_length=10,
        default='auto',
        help_text=_('Override on a per tooltip bases'),
    )
    scroll = models.BooleanField(
        default=True,
        help_text=_('Whether to scroll to tips'),
    )
    scrollSpeed = models.PositiveIntegerField(
        default=300,
        help_text=_('Page scrolling speed in milliseconds'),
    )
    timer = models.PositiveIntegerField(
        default=0,
        help_text=_('0 = no timer , all other numbers = timer in milliseconds'),
    )
    autoStart = models.BooleanField(
        default=False,
        help_text=_('true or false - false tour starts when restart called'),
    )
    startTimerOnClick = models.BooleanField(
        default=True,
        help_text=_('true or false - true requires clicking the first button start the timer'),
    )
    startOffset = models.PositiveIntegerField(
        default=0,
        help_text=_('the index of the tooltip you want to start on (index of the li)'),
    )
    nextButton = models.BooleanField(
        default=True,
        help_text=_('true or false to control whether a next button is used'),
    )
    tipAnimation = models.CharField(
        choices=TIP_ANIMATION_CHOICES,
        default=TIP_ANIMATION_FADE,
        max_length=10,
        help_text=_('"pop" or "fade" in each tip'),
    )
    tipAnimationFadeSpeed = models.PositiveIntegerField(
        default=300,
        help_text=_('when tipAnimation = "fade" this is speed in milliseconds for the transition'),
    )
    cookieMonster = models.BooleanField(
        default=True,
        help_text=_('true or false to control whether cookies are used'),
    )
    cookieName = models.CharField(
        max_length=50,
        default='joyride',
        help_text=_('Name the cookie you\'ll use'),
    )
    cookieDomain = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text=_('Will this cookie be attached to a domain, ie. ".notableapp.com"'),
    )
    cookiePath = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Set to "/" if you want the cookie for the whole website'),
    )
    localStorage = models.BooleanField(
        default=False,
        help_text=_('true or false to control whether localstorage is used'),
    )
    localStorageKey = models.CharField(
        default='joyride',
        max_length=50,
        help_text=_('Keyname in localstorage'),
    )
    tipContainer = models.CharField(
        max_length=100,
        default='body',
        help_text=_('Where will the tip be attached'),
    )
    modal = models.BooleanField(
        default=False,
        help_text=_('Whether to cover page with modal during the tour'),
    )
    expose = models.BooleanField(
        default=False,
        help_text=_('Whether to expose the elements at each step in the tour (requires modal:true)'),
    )
    postExposeCallback = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('A method to call after an element has been exposed'),
    )
    preRideCallback = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('A method to call before the tour starts (passed index, tip, and cloned exposed element)'),
    )
    postRideCallback = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('A method to call once the tour closes (canceled or complete)'),
    )
    preStepCallback = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('A method to call before each step'),
    )
    postStepCallback = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('A method to call after each step'),
    )
    showJoyRideElement = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('A DOM element id or class, a method must be provided in showJoyRideElementOn, \
        if this is left blank then JoyRide will be shown on page load'),
    )
    showJoyRideElementOn = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('When to show JoyRide i.e "fous", "click". This must be set if showJoyRideElement is given'),
    )
    destroy = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('IDs of joyrides which should be destroyed before invoking this joyride e.g. #abc, #cde'),
    )
    created = models.DateTimeField(
        _('Creation Date'),
        default=timezone.now,
        help_text=_('Date and Time of when created'),
    )
    
    objects = JoyRideManager()
    
    @property
    def properties(self):
        j = serializers.serialize('json', [self])
        j = json.loads(j)[0]['fields']
        j.pop('name')
        j.pop('slug')
        j.pop('url_path')
        j.pop('created')
        cookieDomain = j.pop('cookieDomain')
        if not cookieDomain:
            cookieDomain = False
        cookiePath = j.pop('cookiePath')
        if not cookiePath:
            cookiePath = False
        
        j.update({'cookieDomain': cookieDomain, 'cookiePath': cookiePath})
        d = {}
        for key, val in j.iteritems():
            if val != '':
                d[key] = val
        return json.dumps(d)
    
    def clean(self, *args, **kwargs):
        if self.showJoyRideElement and not self.showJoyRideElementOn:
            raise ValidationError(_('showJoyRideElementOn field is required if showJoyRideElement is given'))
        super(JoyRide, self).clean(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(JoyRide, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name


class JoyRideSteps(models.Model):
    class Meta:
        verbose_name = _('Joy Ride Step')
        verbose_name_plural = _('Joy Ride Steps')
        ordering = ['position',]
    
    joyride = models.ForeignKey(JoyRide, related_name='steps')
    
    header = models.CharField(
        _('Step Header'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_('The step header conent'),
    )
    
    content = models.TextField(
        _('Step Content'),
        max_length=255,
        help_text=_('The content for step, can be valid html'),
    )
    
    button = models.CharField(
        max_length=50,
        default='Next',
    )
    
    attachId = models.CharField(
        'data-id',
        max_length=100,
        null=True,
        blank=True,
        help_text=_('Attach this step to particular dom element by id')
    )
    
    attachClass = models.CharField(
        'data-class',
        max_length=100,
        null=True,
        blank=True,
        help_text=_('Attach this step to particular dom element by class')
    )
    
    options = models.CharField(
        _('Options'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Custom attributes related to step which will be used in data-options, \
        i.e. tipLocation:top;tipAnimation:fade'),
    )
    cssClass = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=_('A custom css class name for tip'),
    )
    
    position = PositionField(collection='joyride', default=0)
    
    def clean(self, *args, **kwargs):
        if (self.attachId and self.attachClass) or (not self.attachId and not self.attachClass):
            raise ValidationError(_('Either provide data-id or data-class'))
        super(JoyRideSteps, self).clean(*args, **kwargs)
    
    def __unicode__(self):
        return self.header or self.content[:20]


class JoyRideHistory(models.Model):
    class Meta:
        verbose_name = _('Joy Ride History')
        ordering = ['created',]
        unique_together = ('joyride', 'user')
    
    joyride = models.ForeignKey(JoyRide, related_name='views')
    user = models.ForeignKey(User, related_name='joyrides')
    viewed = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
