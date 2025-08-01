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
from django.urls import path
from jobs import views as job_views
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/applicant/', job_views.register_applicant, name='register_applicant'),
    path('register/employer/', job_views.register_employer, name='register_employer'),
    path('login/', auth_views.LoginView.as_view(template_name='jobs/login.html'), name='login'),
     path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', job_views.register, name='register'),
    path('', job_views.home, name='home'),
    path('employer/dashboard/', job_views.employer_dashboard, name='employer_dashboard'),
    path('applicant/dashboard/', job_views.applicant_dashboard, name='applicant_dashboard'),

    # Employer Functionalities
    path('jobs/post/', job_views.post_job, name='post_job'),
    path('jobs/<int:job_id>/applicants/', job_views.job_applicants, name='job_applicants'),
    path('applications/<int:application_id>/status/', job_views.update_application_status, name='update_application_status'),

    # Applicant Functionalities
    path('jobs/', job_views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', job_views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', job_views.apply_for_job, name='apply_for_job'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)