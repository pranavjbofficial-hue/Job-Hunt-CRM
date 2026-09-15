from django.contrib import admin

from .models import Application, Company, Contact, StatusHistory


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'created_at')
    search_fields = ('name', 'location')
    inlines = [ContactInline]


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_at')
    can_delete = False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'owner', 'status', 'applied_on', 'updated_at')
    list_filter = ('status',)
    search_fields = ('job_title', 'company__name')
    inlines = [StatusHistoryInline]


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'old_status', 'new_status', 'changed_at')
    list_filter = ('new_status',)
