import csv
import datetime
import django_excel as excel

from dateutil.relativedelta import relativedelta
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.db.models import Count, Sum, Q
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import Call, Interaction, Lead, PointsEarned, PointSchedule, RawCallData, Redemption, RedemptionSchedule, Vehicle
from .filters import LeadFilter
from .forms import AffiliateProfileForm, CallForm, LeadForm, UploadFileForm, UserForm, VehicleFormset, VehicleFormset1


def landing(request):
    return render(request, 'lead_mgt/landing.html', {})



def signup(request):
    ref = False
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_passord = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passord)
            user.profile.ref_code = username
            user.profile.phone = username

            affiliate_group = Group.objects.get(name='affiliate')
            user.groups.add(affiliate_group)
            user.save()
            login(request, user)

            try:
                ref = request.session['ref_id']
                try:
                    ref = User.objects.get(id=ref)
                    user.profile.ref = ref
                    user.save()
                except User.DoesNotExist:
                    ref = False
            except KeyError:
                ref = False
            return HttpResponseRedirect(reverse('lead_mgt:profile'))
    else:
        form = UserCreationForm()

    try:
        ref = request.session['ref_id']
        try:
            ref = User.objects.get(id=ref)
        except User.DoesNotExist:
            ref = False
    except KeyError:
        ref = False

    return render(request, 'registration/signup.html', {'form': form, 'ref': ref})


def referred(request, ref):
    request.session['ref_id'] = ref
    return HttpResponseRedirect(reverse('lead_mgt:signup'))


@login_required
def affiliate_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = AffiliateProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            return HttpResponseRedirect(reverse('lead_mgt:affiliate_dashboard'))
    else:
        profile_form = AffiliateProfileForm(instance=request.user.profile)
        user_form = UserForm(instance=request.user)

    return render(request,
                  'lead_mgt/affiliate_profile.html',
                  {
                      'profile_form': profile_form,
                      'user_form': user_form
                  }
                  )


@login_required
def affiliate_dashboard(request):

    link = request.build_absolute_uri(reverse('lead_mgt:referred', kwargs={'ref': request.user.id}))

    all_leads = request.user.lead_set.all().count()
    total_conversion = request.user.lead_set.filter(status='converted').count()

    total_earnings = request.user.earning_set.all().aggregate(Sum('amount'))['amount__sum']

    month_earnings = request.user.earning_set.filter(
        earning_date__month=datetime.date.today().month
    ).aggregate(Sum('amount'))['amount__sum']

    recent_leads = request.user.lead_set.all().order_by('-lead_date')[:5]

    recent_conversions = request.user.lead_set.filter(status='converted').order_by('-lead_date')[:5]

    '''
    # Graph
    labels = []
    leads = []
    conv = []

    tdy = datetime.date.today()
    for x in range(4):
        d = tdy + relativedelta(months=-x)
        labels.insert(0, d.strftime('%b'))

        leads.insert(0, request.user.lead_set.filter(lead_date__month=d.month).count())

        conv.insert(0, request.user.lead_set.filter(status='converted').filter(lead_date__month=d.month).count())
    '''

    top_earners = User.objects.all().annotate(points=Sum('pointsearned__points')).order_by('-points')[:5]

    month_top_earners = User.objects.filter(pointsearned__points_date__month=datetime.date.today().month).annotate(points=Sum('pointsearned__points')).order_by('-points')[:5]

    total_points = request.user.pointsearned_set.all().aggregate(Sum('points'))['points__sum']

    return render(
        request,
        'lead_mgt/affiliate_dashboard.html',
        {
            'top_earners': top_earners,
            'month_earners': month_top_earners,
            'total_leads': all_leads,
            'total_points': total_points,
            'total_conversion': total_conversion,
            'total_earnings': total_earnings,
            'month_earnings': month_earnings,
            'recent_leads': recent_leads,
            'recent_conversions': recent_conversions,
            # 'labels': labels,
            # 'leads': leads,
            # 'conv': conv,
            'link': link,
        }
    )


@login_required
def index(request):

    total_leads = request.user.lead_set.all().count()
    total_conversion = request.user.lead_set.filter(status='converted').count()

    total_earnings = request.user.earning_set.all().aggregate(Sum('amount'))['amount__sum']

    month_earnings = request.user.earning_set.filter(
        earning_date__month=datetime.date.today().month
    ).aggregate(Sum('amount'))['amount__sum']

    recent_leads = request.user.lead_set.all().order_by('-lead_date')[:5]

    recent_conversions = request.user.lead_set.filter(status='converted').order_by('-lead_date')[:5]

    labels = []
    leads = []
    conv = []

    tdy = datetime.date.today()
    for x in range(4):
        d = tdy + relativedelta(months=-x)
        labels.insert(0, d.strftime('%b'))

        leads.insert(0, request.user.lead_set.filter(lead_date__month=d.month).count())

        conv.insert(0, request.user.lead_set.filter(status='converted').filter(lead_date__month=d.month).count())

    return render(
        request,
        'lead_mgt/dashboard.html',
        {
            'total_leads': total_leads,
            'total_conversion': total_conversion,
            'total_earnings': total_earnings,
            'month_earnings': month_earnings,
            'recent_leads': recent_leads,
            'recent_conversions': recent_conversions,
            'labels': labels,
            'leads': leads,
            'conv': conv
        }
    )


@login_required
def add_lead(request):

    if request.method == 'POST':
        lead_form = LeadForm(request.POST)
        vehicle_formset = VehicleFormset(request.POST, request.FILES)

        if lead_form.is_valid() and vehicle_formset.is_valid():
            lead = lead_form.save(commit=False)
            lead.agent = request.user
            lead.save()

            vehicle_formset = VehicleFormset(request.POST, request.FILES, instance=lead)
            vehicle_formset.clean()
            vehicle_formset.save()

            return HttpResponseRedirect(reverse('lead_mgt:index'))
    else:

        lead_form = LeadForm(initial={
            'lead_date': datetime.datetime.today(),
            'title': 'Mr'
        })
        vehicle_formset = VehicleFormset()

    return render(
        request,
        'lead_mgt/add_lead.html',
        {
            'lead_form': lead_form,
            'vehicle_formset': vehicle_formset
        }
                  )


@login_required
def agent_view_lead(request):
    leads = Lead.objects.all()

    return render(
        request,
        'lead_mgt/agent_view_leads.html',
        {
            'leads': leads
        }
    )


@login_required
def call_dashboard(request):

    conversions = Count('call', filter=Q(call__close_status='converted'))
    month_conversions = Count('call', filter=Q(call__call_date__month=datetime.date.today().month) & Q(call__close_status='converted'))
    top_sellers = User.objects.filter(
        groups__name='call_agent'
    ).annotate(conversions=conversions).order_by('-conversions')[:5]

    month_sellers = User.objects.filter(
        groups__name='call_agent'
    ).annotate(conversions=month_conversions).order_by('-conversions')[:5]

    total_calls = request.user.call_set.all().count()
    total_converted = request.user.call_set.filter(close_status='converted').count()
    with_assists = request.user.call_set.filter(lead__status='converted').distinct().count()
    assists = with_assists - total_converted

    conversion_rate = (total_calls/total_converted)*100
    return render(
        request,
        'lead_mgt/call_dashboard.html',
        {
            'total_calls': total_calls,
            'total_converted': total_converted,
            'assists': assists,
            'top_sellers': top_sellers,
            'month_sellers': month_sellers,
            'conversion_rate': conversion_rate
        }
    )


@login_required
def supervisor_dashboard(request):
    new_leads = Lead.objects.filter(status='submitted').count()
    quoted = Lead.objects.filter(status='quoted').filter(next_call_date__lte=datetime.date.today()).count()
    call_later = Lead.objects.filter(status='call_later').filter(next_call_date__lte=datetime.date.today()).count()
    unreachable = Lead.objects.filter(status='unreachable').filter(next_call_date__lte=datetime.date.today()).count()
    unreachable_follow_up = Lead.objects.filter(status='unreachable_follow_up').filter(next_call_date__lte=datetime.date.today()).count()
    bad_line = Lead.objects.filter(status='bad_line').filter(next_call_date__lte=datetime.date.today()).count()
    all_leads = new_leads + quoted + call_later + unreachable + unreachable_follow_up + bad_line

    lead_list = {
        'New leads': new_leads,
        'Quoted': quoted,
        'Call later': call_later,
        'Unreachable': unreachable,
        'Unreachable follow up': unreachable_follow_up,
        'Bad line': bad_line,
    }

    overdue = Lead.objects.exclude(status='converted').filter(next_call_date__lt=datetime.date.today()).count()
    tdy = datetime.date.today()
    today_calls = Call.objects.filter(call_date__date=tdy).count()
    conversions = Call.objects.filter(close_status='converted').filter(call_date__date=tdy).count()
    labels = []
    upcoming_labels = []
    leads = []
    calls = []
    upcoming_calls = []
    for x in range(7):
        dy = tdy + relativedelta(days=-x)
        next_date = tdy + relativedelta(days=x)
        labels.insert(0, dy.strftime('%d %b'))
        leads.insert(0, total_leads(dy))
        calls.insert(0, Call.objects.filter(call_date__date=dy).count())

        upcoming_labels.append(next_date.strftime('%d %b'))
        upcoming_calls.append(Lead.objects.filter(next_call_date=next_date).count())

    return render(
        request,
        'lead_mgt/call_supervisor_dashboard.html',
    {
        'all_leads': all_leads,
        'lead_list': lead_list,
        'overdue': overdue,
        'labels': labels,
        'leads': leads,
        'calls': calls,
        'conversions': conversions,
        'today_calls': today_calls,
        'upcoming_calls': upcoming_calls,
        'upcoming_labels': upcoming_labels

    }
    )


def total_leads(dated):
    new_leads = Lead.objects.filter(status='submitted').filter(lead_date=dated).count()
    follow_up = Lead.objects.exclude(status='converted').filter(next_call_date=dated).count()
    return new_leads + follow_up


def import_call(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST,
                              request.FILES)
        if form.is_valid():
            try:
                last = RawCallData.objects.all().order_by('-database_date')[0]
                batch_number = last.batch_number + 1
            except IndexError:
                batch_number = 1

            def batch(row):
                row[0] = batch_number
                return row

            request.FILES['file'].save_to_database(
                #  name_columns_by_row=2,
                initializer=batch,
                model=RawCallData,
                # mapdict=['batch_number', 'lead', 'interaction_date', 'user', 'notes', 'result'])
                mapdict={
                    'Batch': 'batch_number',
                    'ID': 'lead_id',
                    'Lead date': 'lead_date',
                    'Name': 'lead_name',
                    'Phone': 'lead_phone',
                    'Current status': 'current_status',
                    'Next call date': 'current_next_call',
                    'Agent id': 'agent_id',
                    'Date': 'call_date',
                    'Disposition': 'disposition',
                    'Notes': 'notes',
                    'Call back date': 'new_next_call',
                    'Policy number': 'policy_number'
                }
            )

            return HttpResponseRedirect(reverse('lead_mgt:confirm_import', kwargs={'batch_number': batch_number}))
        #  else:
        #    return HttpResponseBadRequest()
    else:
        form = UploadFileForm()
    return render(
        request,
        'lead_mgt/upload_form.html',
        {'form': form})


def confirm_import(request, batch_number):
    title = 'Import calls'
    description = "Click confirm import to update calls to database"

    calls = RawCallData.objects.filter(batch_number=batch_number)

    columns = [
        'Lead id',
        'Client Name',
        'Call date',
        'Call agent id',
        'Disposition',
        'Notes',
        'Next call',
        'Policy number'
    ]

    return render(
        request,
        'lead_mgt/display_list.html',
        {
            'title': title,
            'description': description,
            'calls': calls,
            'columns': columns,
            'batch_number': batch_number,
            'sender': 'confirm_import'
        }
    )


def supervisor_leads(request):
    leads = Lead.objects.exclude(status='converted').exclude(status='not_interested')
    lead_filter = LeadFilter(request.GET, queryset=leads)

    if 'download' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Leads.csv"'

        writer = csv.writer(response)

        writer.writerow(['ID', 'Lead date', 'Name', 'Phone', 'Current status', 'Next call date'])

        for lead in lead_filter.qs:
            writer.writerow([
                lead.id,
                lead.lead_date,
                lead.title + ' ' + lead.first_name + ' ' + lead.last_name,
                lead.phone_number,
                lead.status,
                lead.next_call_date
            ])

        return response

    return render(
        request,
        'lead_mgt/supervisor_leads.html',
        {
            'filter': lead_filter
        }
    )


def call_import(request, batch_number):
    calls = RawCallData.objects.filter(batch_number=batch_number)

    for call in calls:
        if call.upload_status != 'success':

            lead = Lead.objects.get(id=call.lead_id)
            agent = User.objects.get(username=call.agent_id)

            if call.notes == None:
                notes = ''
            else:
                notes = call.notes

            new_call = Call(
                lead=lead,
                call_agent=agent,
                call_date=datetime.datetime.strptime(call.call_date, '%d/%m/%Y'),
                notes=notes,
                open_status=lead.status,
                close_status=call.disposition
            ).save()

            lead.status = call.disposition
            lead.save()

            call.upload_status = 'success'
            call.save()
            
    return HttpResponseRedirect(reverse('lead_mgt:import_status', kwargs={'batch_number': batch_number}))


def import_status(request, batch_number):
    title = 'Import calls status'
    description = "See below the import status of your calls"

    calls = RawCallData.objects.filter(batch_number=batch_number)

    columns = [
        'Lead id',
        'Client Name',
        'Call agent id',
        'Disposition',
        'Notes',
        'Status'
    ]

    return render(
        request,
        'lead_mgt/display_list.html',
        {
            'title': title,
            'description': description,
            'calls': calls,
            'columns': columns,
            'batch_number': batch_number,
            'sender': 'import_status'
        }
    )




@login_required
def call_lead_detail(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)

    if request.method == 'POST':
        vehicle_formset = VehicleFormset1(request.POST, request.FILES, instance=lead)
        call_form = CallForm(request.POST)
        if vehicle_formset.is_valid() and call_form.is_valid():
            vehicle_formset.save()

            call = Call(
                call_agent=request.user,
                lead=lead,
                notes=call_form.cleaned_data['notes'],
                open_status=lead.status,
                close_status=call_form.cleaned_data['close_status']
            )
            call.save()

            lead.status = call_form.cleaned_data['close_status']

            if request.POST['next_call_date']:
                lead.next_call_date = request.POST['next_call_date']

            lead.save()

            HttpResponseRedirect(reverse('lead_mgt:agent_view_lead'))
    else:
        vehicle_formset = VehicleFormset1(instance=lead)
        call_form = CallForm()

    return render(
        request,
        'lead_mgt/call_lead_detail.html',
        {
            'lead': lead,
            'vehicle_formset': vehicle_formset,
            'call_form': call_form
        }
    )


def update_vehicle(request):
    vehicle = Vehicle.objects.get(id=request.POST['vehicle_id'])
    if request.POST['status'] == 'closed':
        vehicle.status = request.POST['status']
        vehicle.policy_type = request.POST['policy_type']
        vehicle.policy_number = request.POST['policy_number']
        vehicle.save()

        allocate_points(vehicle)

    return JsonResponse({'status': 'success'})


def allocate_points(vehicle):
    scheme = PointSchedule.objects.get(scheme_name='default')
    points_0 = 0
    points_1 = 0
    points_2 = 0
    points_3 = 0

    if vehicle.status == 'closed':
        if vehicle.lead.agent:
            affiliate_0 = vehicle.lead.agent
            if affiliate_0.groups.filter(name='affiliate').exists():
                # Level 0 points:  The actual referer
                if vehicle.policy_type == 'comp':
                    points_0 = scheme.level_0_comp
                    points_1 = scheme.level_1_comp
                    points_2 = scheme.level_2_comp
                    points_3 = scheme.level_3_comp
                elif vehicle.policy_type == 'ftp':
                    points_0 = scheme.level_0_ftp
                    points_1 = scheme.level_1_ftp
                    points_2 = scheme.level_2_ftp
                    points_3 = scheme.level_3_ftp
                else:
                    points_0 = 0
                    points_1 = 0
                    points_2 = 0
                    points_3 = 0

                affiliate_points_0 = PointsEarned(
                    affiliate=vehicle.lead.agent,
                    points=points_0,
                    type='level_0_comp',
                    lead=vehicle.lead
                ).save()

            # import pdb; pdb.set_trace()
            if affiliate_0.profile.ref:
                affiliate_1 = affiliate_0.profile.ref

                affiliate_points_1 = PointsEarned(
                    affiliate=affiliate_1,
                    points=points_1,
                    type='level_1_comp',
                    lead=vehicle.lead
                ).save()

                if affiliate_1.profile.ref:
                    affiliate_2 = affiliate_1.profile.ref
                    affiliate_points_2 = PointsEarned(
                        affiliate=affiliate_2,
                        points=points_2,
                        type='level_2_comp',
                        lead=vehicle.lead
                    ).save()

                    if affiliate_2.profile.ref:
                        affiliate_3 = affiliate_2.profile.ref
                        affiliate_points_3 = PointsEarned(
                            affiliate=affiliate_3,
                            points=points_3,
                            type='level_3_comp',
                            lead=vehicle.lead
                        ).save()

    return {'status': 'success'}


@login_required
def redeem_points(request):

    # TODO remembeer to subtract redeemed points
    total_points = request.user.pointsearned_set.all().aggregate(Sum('points'))['points__sum'] or 0
    total_redeemed = request.user.redemption_set.all().aggregate(Sum('points'))['points__sum'] or 0

    # TODO remembeer to subtract paid amounts
    wallet_balance = request.user.redemption_set.all().aggregate(Sum('amount'))['amount__sum'] or 0

    options = RedemptionSchedule.objects.all().order_by('points')
    return render(
        request,
        'lead_mgt/redeem_points.html',
        {
            'link': request.build_absolute_uri(reverse('lead_mgt:referred', kwargs={'ref': request.user.id})),
            'points_balance': total_points-total_redeemed,
            'wallet_balance': wallet_balance,
            'options_1': options[:3],
            'options_2': options[3:]
        }
    )


@login_required
def redeem(request, option):
    option = get_object_or_404(RedemptionSchedule, pk=option)

    redemption = Redemption(
        affiliate=request.user,
        points=option.points,
        amount=option.amount
    ).save()

    return HttpResponseRedirect(reverse('lead_mgt:redeem_points'))
