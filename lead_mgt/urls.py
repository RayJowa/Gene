from django.urls import path

from . import views

app_name = 'lead_mgt'
urlpatterns = [
    path('', views.index, name='index'),
    path('add_lead/', views.add_lead, name='add_lead'),
    path('affiliate/', views.affiliate_dashboard, name='affiliate_dashboard'),
    path('download_leads/', views.add_lead, name='add_lead'),
    path('call_dashboard/', views.call_dashboard, name='call_dashboard'),
    path('call_import/<batch_number>/', views.call_import, name='call_import'),
    path('import/', views.import_call, name='import_call'),
    path('import_status/<batch_number>/', views.import_status, name='import_status'),
    path('landing/', views.landing, name='landing'),
    path('leads/', views.agent_view_lead, name='agent_view_lead'),
    path('lead_detail/<lead_id>/', views.call_lead_detail, name='call_lead_detail'),
    path('refer/<ref>/', views.referred, name='referred'),
    path('redeem/', views.redeem_points, name='redeem_points'),
    path('redeem/<option>/', views.redeem, name='redeem'),
    path('supervisor/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor_leads/', views.supervisor_leads, name='supervisor_leads'),
    path('confirm_import/<batch_number>/', views.confirm_import, name='confirm_import'),
    path('signup/', views.signup, name='signup'),
    path('update_vehicle/', views.update_vehicle, name='update_vehicle'),
    path('profile/', views.affiliate_profile, name='profile'),

]