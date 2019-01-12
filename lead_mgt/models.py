from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Lead(models.Model):
    agent = models.ForeignKey(User, null=True, on_delete=models.SET_DEFAULT, default=1)
    lead_date = models.DateField(verbose_name='Date')
    title = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    status = models.CharField(max_length=30,
                              default='submitted',
                              choices=(
                                  ('submitted', 'submitted'),
                                  ('unreachable', 'unreachable'),
                                  ('unreachable_follow_up', 'unreachable follow up'),
                                  ('wrong_number', 'wrong number'),
                                  ('converted', 'converted'),
                                  ('not_interested', 'not interested'),
                                  ('not_expired', 'not expired'),
                                  ('call_later', 'call later'),
                                  ('quoted', 'quoted'),
                                  ('bad_line', 'bad line')
                              )
                              )
    next_call_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Call(models.Model):
    call_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    call_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    type = models.CharField(max_length=20, blank=True)
    open_status = models.CharField(max_length=30, blank=True)
    close_status = models.CharField(max_length=30,
                                    blank=True,
                                    choices=(
                                        ('unreachable', 'unreachable'),
                                        ('unreachable_follow_up', 'unreachable follow up'),
                                        ('wrong_number', 'wrong number'),
                                        ('converted', 'converted'),
                                        ('not_interested', 'not interested'),
                                        ('not_expired', 'not expired'),
                                        ('call_later', 'call later'),
                                        ('quoted', 'quoted'),
                                        ('bad_line', 'bad line')
                                    )
                                    )

    def __str__(self):
        return self.lead.last_name


class CommissionPayment(models.Model):
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recipient')

    def __str__(self):
        '{} - {}'.format(self.recipient.username, self.amount)


class Earning(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    earning_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid = models.BooleanField(default=False)


class Vehicle(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    make = models.CharField(max_length=50, blank=True)
    vehicle_model = models.CharField(max_length=50, blank=True)
    reg_number = models.CharField(max_length=20, blank=True)
    insurance_expiry = models.DateField(null=True)
    status = models.CharField(max_length=20,
                              default='open',
                              blank=True,
                              choices=(
                                       ('open', 'open'),
                                       ('closed', 'closed')
                              )
                              )
    policy_type = models.CharField(max_length=20,
                                   blank=True,
                                   choices=(
                                       ('ftp', 'third party'),
                                       ('comp', 'comprehensive')
                                   )
                                   )
    policy_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return '{} {}({})'.format(self.make, self.vehicle_model, self.reg_number)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ref = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='referer')
    ref_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=50)
    birth_date = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=50)
    bank = models.CharField(max_length=50, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ecocash_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        if self.ref:
            return '{} < {}'.format(self.user.username, self.ref.username)
        else:
            return self.user.username

    def affiliate_1_count(self):
        return self.user.referer.all().count()

    def affiliate_2_count(self):
        count = 0
        for affiliate in self.user.referer.all():
            count += affiliate.affiliate_1_count()

        return count

    def affiliate_3_count(self):
        count = 0
        for affiliate in self.user.referer.all():
            count += affiliate.affiliate_2_count()
        return count

    def affiliate_1_2_count(self):
        return self.affiliate_1_count() + self.affiliate_2_count()

    def affiliate_total_count(self):
        return self.affiliate_1_count() + self.affiliate_2_count() + self.affiliate_3_count()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Interaction(models.Model):
    batch_number = models.IntegerField()
    lead = models.CharField(max_length=10)
    interaction_date = models.DateField()
    user = models.CharField(max_length=10)
    notes = models.TextField(blank=True)
    result = models.CharField(max_length=50)
    database_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.result


class RawCallData(models.Model):
    batch_number = models.IntegerField()
    database_date = models.DateTimeField(auto_now_add=True)
    lead_id = models.CharField(max_length=20)
    lead_date = models.CharField(max_length=20)
    lead_name = models.CharField(max_length=160)
    lead_phone = models.CharField(max_length=50)
    current_status = models.CharField(max_length=50)
    current_next_call = models.CharField(max_length=50, blank=True, null=True)
    agent_id = models.CharField(max_length=50, blank=True)
    call_date = models.CharField(max_length=20, blank=True)
    disposition = models.CharField(max_length=50)
    notes = models.CharField(max_length=160, blank=True, null=True)
    new_next_call = models.CharField(max_length=20, blank=True, null=True)
    policy_number = models.CharField(max_length=50, blank=True, null=True)
    policy_type = models.CharField(max_length=20,
                                   blank=True,
                                   choices= (
                                       ('ftp', 'full third party'),
                                       ('comp', 'comprehensive')
                                   )
                                   )
    upload_status = models.CharField(max_length=20,
                                     blank=True,
                                     choices=(
                                         ('success', 'success'),
                                         ('failed', 'failed')
                                     )
                                     )

    def __str__(self):
        return "{} > {}".format(self.agent_id, self.lead_name)


class ImportErrors(models.Model):
    call = models.ForeignKey(RawCallData, on_delete=models.CASCADE)
    error_text = models.CharField(max_length=120)


class PointSchedule(models.Model):
    scheme_name = models.CharField(max_length=20)
    level_0_comp = models.IntegerField()
    level_1_comp = models.IntegerField()
    level_2_comp = models.IntegerField()
    level_3_comp = models.IntegerField()
    level_0_ftp = models.IntegerField()
    level_1_ftp = models.IntegerField()
    level_2_ftp = models.IntegerField()
    level_3_ftp = models.IntegerField()

    def __str__(self):
        return self.scheme_name


class PointsEarned(models.Model):
    points_date = models.DateTimeField(auto_now_add=True)
    affiliate = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    points = models.IntegerField()
    type = models.CharField(max_length=20)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.affiliate.username, self.points)


class RedemptionSchedule(models.Model):
    points = models.IntegerField()
    amount = models.IntegerField()

    def __str__(self):
        return '{}-{}'.format(self.points, self.amount)


class Redemption(models.Model):
    affiliate = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    amount = models.IntegerField()
    redemption_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {} > ${}'. format(self.affiliate.username, self.points, self.amount)

