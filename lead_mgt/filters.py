import django_filters

from .models import Lead


class LeadFilter(django_filters.FilterSet):
    class Meta:
        model = Lead
        fields = ['lead_date', 'status', 'next_call_date']

