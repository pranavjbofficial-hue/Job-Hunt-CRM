from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Applications
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/new/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_update'),
    path('applications/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),

    # Companies
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/new/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('companies/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    path('companies/<int:pk>/contacts/new/', views.contact_create, name='contact_create'),
]
