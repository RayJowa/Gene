from django.contrib import admin

from .models import Call, CommissionPayment, Earning, Interaction, Lead, PointSchedule, PointsEarned, Profile, RawCallData, RedemptionSchedule, Vehicle


class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 1


class CallInline(admin.TabularInline):
    model = Call
    extra = 1

"""
class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 1
"""


class LeadAdmin(admin.ModelAdmin):
    inlines = [VehicleInline, CallInline, ]


admin.site.register(Lead, LeadAdmin)
admin.site.register(Profile)
admin.site.register(CommissionPayment)
admin.site.register(Earning)
admin.site.register(Interaction)
admin.site.register(PointSchedule)
admin.site.register(PointsEarned)
admin.site.register(RawCallData)
admin.site.register(RedemptionSchedule)
