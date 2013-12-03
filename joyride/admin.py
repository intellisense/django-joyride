from django.contrib import admin

from joyride.models import *

class JoyRideStepsInline(admin.StackedInline):
    model = JoyRideSteps

class JoyRideAdmin(admin.ModelAdmin):
    inlines = (JoyRideStepsInline, )

admin.site.register(JoyRide, JoyRideAdmin)
admin.site.register(JoyRideHistory)