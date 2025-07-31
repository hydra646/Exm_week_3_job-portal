# jobs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from .models import Job, Application, APPLICATION_STATUS_CHOICES
from .forms import JobForm, ApplicationForm, UserRegistrationForm
from django.contrib.auth.models import Group


# Helper function to check if user is employer
def is_employer(user):
    return user.groups.filter(name='Employer').exists()

# Helper function to check if user is applicant
def is_applicant(user):
    return user.groups.filter(name='Applicant').exists()

# --- Authentication Views ---

def register_applicant(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            applicant_group, created = Group.objects.get_or_create(name='Applicant')
            user.groups.add(applicant_group)
            messages.success(request, 'Applicant account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'jobs/register_applicant.html', {'form': form})

def register_employer(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            employer_group, created = Group.objects.get_or_create(name='Employer')
            user.groups.add(employer_group)
            messages.success(request, 'Employer account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'jobs/register_employer.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                if is_employer(user):
                    return redirect('employer_dashboard')
                elif is_applicant(user):
                    return redirect('job_list')
                else:
                    return redirect('home') # Default for users without a specific role
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'jobs/login.html', {'form': form})

# --- Dashboard/Home Views ---

@login_required
def home(request):
    if is_employer(request.user):
        return redirect('employer_dashboard')
    elif is_applicant(request.user):
        return redirect('job_list')
    else:
        return render(request, 'jobs/home.html') # Generic home page for unassigned roles

@login_required
def employer_dashboard(request):
    if not is_employer(request.user):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')
    posted_jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'jobs/employer_dashboard.html', {'posted_jobs': posted_jobs})

@login_required
def applicant_dashboard(request):
    if not is_applicant(request.user):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    # Get status from query parameter for filtering
    status_filter = request.GET.get('status')
    
    submitted_applications = Application.objects.filter(applicant=request.user)

    # Filter applications by status if provided and valid
    if status_filter in [status[0] for status in APPLICATION_STATUS_CHOICES]:
        submitted_applications = submitted_applications.filter(status=status_filter)

    return render(request, 'jobs/applicant_dashboard.html', {
        'submitted_applications': submitted_applications,
        'status_filter': status_filter # Pass the filter to the template for highlighting active filter
    })


# --- Employer Functionalities ---

@login_required
def post_job(request):
    if not is_employer(request.user):
        messages.error(request, "You must be an employer to post jobs.")
        return redirect('home')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def job_applicants(request, job_id):
    if not is_employer(request.user):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applicants = job.applications.all() # Using related_name from Application model
    return render(request, 'jobs/job_applicants.html', {'job': job, 'applicants': applicants})


@login_required
def update_application_status(request, application_id):
    if not is_employer(request.user):
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('home')

    application = get_object_or_404(Application, id=application_id)

    # Security check: Ensure the employer owns the job associated with the application
    if application.job.posted_by != request.user:
        messages.error(request, "You do not have permission to update this application.")
        return redirect('employer_dashboard') # Redirect to a safe place

    if request.method == 'POST':
        new_status = request.POST.get('status')
        # Validate that the new_status is one of the allowed choices
        if new_status in [status_choice[0] for status_choice in APPLICATION_STATUS_CHOICES]:
            application.status = new_status
            application.save()
            messages.success(request, f"Application for {application.applicant.username} has been updated to {new_status}.")
        else:
            messages.error(request, "Invalid status provided.")
    else:
        messages.error(request, "Invalid request method.")

    # Redirect back to the job applicants page for the specific job
    return redirect('job_applicants', job_id=application.job.id)


# --- Applicant Functionalities ---

def job_list(request):
    query = request.GET.get('q')
    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(location__icontains=query)
        ).distinct() # Use distinct to avoid duplicate results if a job matches multiple conditions

    return render(request, 'jobs/job_list.html', {'jobs': jobs, 'query': query})

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    has_applied = False
    if request.user.is_authenticated and is_applicant(request.user):
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def apply_for_job(request, job_id):
    if not is_applicant(request.user):
        messages.error(request, "You must be an applicant to apply for jobs.")
        return redirect('home')
    job = get_object_or_404(Job, id=job_id)

    # Prevent multiple applications for the same job by the same applicant
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('applicant_dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply_for_job.html', {'form': form, 'job': job})