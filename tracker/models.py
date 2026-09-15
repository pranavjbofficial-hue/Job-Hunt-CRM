from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies',
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('company_detail', kwargs={'pk': self.pk})


class Contact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} ({self.company.name})'


class Application(models.Model):
    STATUS_APPLIED = 'applied'
    STATUS_PHONE_SCREEN = 'phone_screen'
    STATUS_INTERVIEW = 'interview'
    STATUS_OFFER = 'offer'
    STATUS_REJECTED = 'rejected'
    STATUS_WITHDRAWN = 'withdrawn'

    STATUS_CHOICES = [
        (STATUS_APPLIED, 'Applied'),
        (STATUS_PHONE_SCREEN, 'Phone Screen'),
        (STATUS_INTERVIEW, 'Interview'),
        (STATUS_OFFER, 'Offer'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]

    # Statuses that count as the pipeline still being "active"
    OPEN_STATUSES = [STATUS_APPLIED, STATUS_PHONE_SCREEN, STATUS_INTERVIEW]
    CLOSED_STATUSES = [STATUS_OFFER, STATUS_REJECTED, STATUS_WITHDRAWN]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='applications')
    job_title = models.CharField(max_length=200)
    job_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    applied_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.job_title} @ {self.company.name}'

    def get_absolute_url(self):
        return reverse('application_detail', kwargs={'pk': self.pk})

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    @property
    def days_since_applied(self):
        return (timezone.localdate() - self.applied_on).days

    @property
    def needs_follow_up(self):
        """True if it's been 7+ days since applying with no movement, and it's still open."""
        return self.is_open and self.status == self.STATUS_APPLIED and self.days_since_applied >= 7


class StatusHistory(models.Model):
    """Automatically logged every time an Application's status changes."""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES, blank=True, null=True)
    new_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'status history'

    def __str__(self):
        return f'{self.application}: {self.old_status} -> {self.new_status}'
