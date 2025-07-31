# jobs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout # For user session management
from django.contrib.auth.decorators import login_required, user_passes_test # For access control
from django.db.models import Q # For complex queries (search)
from django.contrib import messages # For displaying feedback messages to users

from .forms import CustomUserCreationForm, CustomAuthenticationForm, JobForm, ApplicationForm
from .models import User, Job, Application

# --- Helper Functions for Role-Based Access Control ---
# These functions are used with @user_passes_test decorator
def is_employer(user):
    return user.is_authenticated and user.role == 'employer'

def is_applicant(user):
    return user.is_authenticated and user.role == 'applicant'

# --- Authentication Views ---

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in immediately after registration
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('dashboard') # Redirect to the role-based dashboard
        else:
            messages.error(request, 'Error during registration. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() # Get the authenticated user
            login(request, user) # Log the user in
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard') # Redirect to the role-based dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required # Requires user to be logged in
def logout_view(request):
    logout(request) # Log the user out
    messages.info(request, 'You have been logged out.')
    return redirect('home') # Redirect to the home page

# --- Dashboard/Home Page Redirection ---

@login_required
def dashboard_view(request):
    # Redirects logged-in users to their respective dashboards based on role
    if request.user.role == 'employer':
        return redirect('employer_dashboard')
    elif request.user.role == 'applicant':
        return redirect('applicant_dashboard')
    else:
        # Fallback for users without a defined role (shouldn't happen with our current setup)
        messages.warning(request, 'Your user role is not recognized. Please contact support.')
        return redirect('home')

# --- Employer Functionalities ---

@login_required
@user_passes_test(is_employer) # Only employers can access this view
def employer_dashboard(request):
    # Display jobs posted by the current employer
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    return render(request, 'employer/dashboard.html', {'jobs': jobs})

@login_required
@user_passes_test(is_employer) # Only employers can access this view
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False) # Don't save to DB yet
            job.posted_by = request.user # Assign the current user as the poster
            job.save() # Now save the job
            messages.success(request, 'Job posted successfully!')
            return redirect('employer_dashboard')
        else:
            messages.error(request, 'Error posting job. Please correct the errors below.')
    else:
        form = JobForm() # Display an empty form for GET request
    return render(request, 'employer/post_job.html', {'form': form})

@login_required
@user_passes_test(is_employer) # Only employers can access this view
def job_applicants(request, job_id):
    # Retrieve the job, ensuring it belongs to the current employer
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    # Get all applications for this job
    applications = job.applications.all().order_by('-applied_at')
    return render(request, 'employer/job_applicants.html', {'job': job, 'applications': applications})

# --- Applicant Functionalities ---

@login_required
@user_passes_test(is_applicant) # Only applicants can access this view
def applicant_dashboard(request):
    # Display applications submitted by the current applicant
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'applicant/dashboard.html', {'applications': applications})

@login_required
@user_passes_test(is_applicant) # Only applicants can access this view
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at') # Start with all jobs, ordered by newest first

    # --- Search Functionality ---
    # Get search parameters from the GET request
    query = request.GET.get('q') # General search (title, description, company, location)
    title_query = request.GET.get('title')
    company_query = request.GET.get('company')
    location_query = request.GET.get('location')

    if query:
        # Use Q objects for OR queries across multiple fields
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(company_name__icontains=query) |
            Q(location__icontains=query)
        ).distinct() # .distinct() to avoid duplicate results if a job matches multiple criteria

    if title_query:
        jobs = jobs.filter(title__icontains=title_query)
    if company_query:
        jobs = jobs.filter(company_name__icontains=company_query)
    if location_query:
        jobs = jobs.filter(location__icontains=location_query)

    return render(request, 'applicant/job_list.html', {
        'jobs': jobs,
        'query': query, # Pass back to template to pre-fill search bar
        'title_query': title_query,
        'company_query': company_query,
        'location_query': location_query,
    })

@login_required
@user_passes_test(is_applicant) # Only applicants can access this view
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id) # Get the specific job or return 404
    # Check if the current applicant has already applied for this job
    has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'applicant/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
@user_passes_test(is_applicant) # Only applicants can access this view
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Prevent re-application
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        # request.FILES is essential for file uploads
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False) # Don't save to DB yet
            application.job = job # Associate with the job
            application.applicant = request.user # Associate with the current applicant
            application.save() # Now save the application
            messages.success(request, 'Application submitted successfully!')
            return redirect('applicant_dashboard') # Redirect to applicant's applications
        else:
            messages.error(request, 'Error submitting application. Please ensure all fields are correct and a resume is uploaded.')
    else:
        form = ApplicationForm() # Display an empty form for GET request
    return render(request, 'applicant/apply_job.html', {'form': form, 'job': job})

# --- Public Home Page ---
def home_view(request):
    return render(request, 'home.html')