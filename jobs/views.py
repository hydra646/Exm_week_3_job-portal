# jobs/views.py
# jobs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import Job, Application, APPLICATION_STATUS_CHOICES
from .forms import JobForm, ApplicationForm, CustomUserCreationForm

def register(request):
    return render(request, 'jobs/register.html')

def is_employer(user):
    return user.groups.filter(name='Employer').exists()

def is_applicant(user):
    return user.groups.filter(name='Applicant').exists()

# --- Authentication Views ---
def register_applicant(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'applicant'
            user.save()
            applicant_group, created = Group.objects.get_or_create(name='Applicant')
            user.groups.add(applicant_group)
            messages.success(request, 'Applicant account created successfully! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm(initial={'role': 'applicant'})
    return render(request, 'jobs/register_applicant.html', {'form': form})

def register_employer(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'employer'
            user.save()
            employer_group, created = Group.objects.get_or_create(name='Employer')
            user.groups.add(employer_group)
            messages.success(request, 'Employer account created successfully! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm(initial={'role': 'employer'})
    return render(request, 'jobs/register_employer.html', {'form': form})

# --- Dashboard/Home Views ---

def home(request):
    return render(request, 'jobs/home.html')

@login_required
def employer_dashboard(request):
    jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})

@login_required
def applicant_dashboard(request):
    status_filter = request.GET.get('status')
    applications = Application.objects.filter(applicant=request.user)
    if status_filter in dict(APPLICATION_STATUS_CHOICES):
        applications = applications.filter(status=status_filter)
    return render(request, 'jobs/applicant_dashboard.html', {
        'applications': applications,
        'status_choices': APPLICATION_STATUS_CHOICES,
        'selected_status': status_filter,
    })

# --- Employer Functionalities ---
@login_required
def post_job(request):
    if not is_employer(request.user):
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
    # Ensure only the employer who posted the job can view this page
    if not is_employer(request.user):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')
    # Get the job object, ensuring the logged-in user is the one who posted it
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    # Fetch all applications for this specific job
    applications = job.applications.select_related('applicant').all()
    return render(request, 'jobs/job_applicants.html', {'job': job, 'applications': applications})

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if application.job.posted_by != request.user:
        return redirect('home')
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        if new_status in dict(APPLICATION_STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Application status updated to {new_status}.")
    return redirect('job_applicants', job_id=application.job.id)

# --- Applicant Functionalities ---
@login_required
def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    # Check if the user has already applied for this job
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job_id)
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