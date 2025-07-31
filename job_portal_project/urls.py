"""
URL configuration for job_portal_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# job_portal_project/urls.py
from django.contrib import admin
from django.urls import path, include # 'include' is needed to include app-specific URLs
from django.conf import settings
from django.conf.urls.static import static # To serve media files in development

from jobs import views as job_views # Import your app's views

urlpatterns = [
    path('admin/', admin.site.urls), # Django Admin URL

    # Authentication URLs
    path('register/', job_views.register_view, name='register'),
    path('login/', job_views.login_view, name='login'),
    path('logout/', job_views.logout_view, name='logout'),
    path('dashboard/', job_views.dashboard_view, name='dashboard'), # Role-based redirection
    path('', job_views.home_view, name='home'), # Public home page

    # Employer URLs
    path('employer/dashboard/', job_views.employer_dashboard, name='employer_dashboard'),
    path('employer/post-job/', job_views.post_job, name='post_job'),
    path('employer/job/<int:job_id>/applicants/', job_views.job_applicants, name='job_applicants'),

    # Applicant URLs
    path('jobs/', job_views.job_list, name='job_list'), # List all jobs with search
    path('jobs/<int:job_id>/', job_views.job_detail, name='job_detail'), # Specific job details
    path('jobs/<int:job_id>/apply/', job_views.apply_job, name='apply_job'), # Apply to a job
    path('applicant/dashboard/', job_views.applicant_dashboard, name='applicant_dashboard'), # Applicant's applications
]

# Serve media files during development.
# IMPORTANT: This should ONLY be used in development.
# In production, web servers (like Nginx, Apache) handle media files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)