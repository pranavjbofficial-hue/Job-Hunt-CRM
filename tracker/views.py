from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import ApplicationForm, CompanyForm, ContactForm
from .models import Application, Company, Contact


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


class OwnedQuerysetMixin(LoginRequiredMixin):
    """Restrict any ListView/DetailView/UpdateView/DeleteView to the current user's own rows."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


# ---------- Dashboard ----------

@login_required
def dashboard(request):
    applications = Application.objects.filter(owner=request.user)

    total = applications.count()
    status_counts = dict(
        applications.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )

    open_count = sum(status_counts.get(s, 0) for s in Application.OPEN_STATUSES)
    closed_count = sum(status_counts.get(s, 0) for s in Application.CLOSED_STATUSES)
    offers = status_counts.get(Application.STATUS_OFFER, 0)
    rejections = status_counts.get(Application.STATUS_REJECTED, 0)

    # Response rate = anything that moved past "applied" divided by total
    moved_past_applied = applications.exclude(status=Application.STATUS_APPLIED).count()
    response_rate = round((moved_past_applied / total) * 100, 1) if total else 0

    # Funnel counts, in pipeline order
    funnel = [
        {'label': label, 'key': key, 'count': status_counts.get(key, 0)}
        for key, label in Application.STATUS_CHOICES
    ]

    needs_follow_up = [a for a in applications if a.needs_follow_up]

    recent = applications.order_by('-updated_at')[:8]

    context = {
        'total': total,
        'open_count': open_count,
        'closed_count': closed_count,
        'offers': offers,
        'rejections': rejections,
        'response_rate': response_rate,
        'funnel': funnel,
        'needs_follow_up': needs_follow_up,
        'recent': recent,
    }
    return render(request, 'tracker/dashboard.html', context)


# ---------- Applications ----------

class ApplicationListView(OwnedQuerysetMixin, ListView):
    model = Application
    template_name = 'tracker/application_list.html'
    context_object_name = 'applications'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('company')
        status = self.request.GET.get('status')
        q = self.request.GET.get('q')
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(
                Q(job_title__icontains=q) | Q(company__name__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Application.STATUS_CHOICES
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class ApplicationDetailView(OwnedQuerysetMixin, DetailView):
    model = Application
    template_name = 'tracker/application_detail.html'
    context_object_name = 'application'

    def get_queryset(self):
        return super().get_queryset().select_related('company').prefetch_related('status_history')


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'tracker/application_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Application added.')
        return super().form_valid(form)


class ApplicationUpdateView(OwnedQuerysetMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'tracker/application_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Application updated.')
        return super().form_valid(form)


class ApplicationDeleteView(OwnedQuerysetMixin, DeleteView):
    model = Application
    template_name = 'tracker/application_confirm_delete.html'
    success_url = reverse_lazy('application_list')

    def form_valid(self, form):
        messages.success(self.request, 'Application deleted.')
        return super().form_valid(form)


# ---------- Companies ----------

class CompanyListView(OwnedQuerysetMixin, ListView):
    model = Company
    template_name = 'tracker/company_list.html'
    context_object_name = 'companies'

    def get_queryset(self):
        return super().get_queryset().annotate(app_count=Count('applications'))


class CompanyDetailView(OwnedQuerysetMixin, DetailView):
    model = Company
    template_name = 'tracker/company_detail.html'
    context_object_name = 'company'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('applications', 'contacts')


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'tracker/company_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Company added.')
        return super().form_valid(form)


class CompanyUpdateView(OwnedQuerysetMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'tracker/company_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Company updated.')
        return super().form_valid(form)


class CompanyDeleteView(OwnedQuerysetMixin, DeleteView):
    model = Company
    template_name = 'tracker/company_confirm_delete.html'
    success_url = reverse_lazy('company_list')

    def form_valid(self, form):
        messages.success(self.request, 'Company deleted.')
        return super().form_valid(form)


@login_required
def contact_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk, owner=request.user)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.company = company
            contact.save()
            messages.success(request, 'Contact added.')
            return redirect('company_detail', pk=company.pk)
    else:
        form = ContactForm()
    return render(request, 'tracker/contact_form.html', {'form': form, 'company': company})
