from django import forms

from .models import Application, Company, Contact


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'website', 'location', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'role', 'email', 'phone', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'company', 'job_title', 'job_url', 'status',
            'salary_min', 'salary_max', 'applied_on', 'notes',
        ]
        widgets = {
            'applied_on': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['company'].queryset = Company.objects.filter(owner=user)
