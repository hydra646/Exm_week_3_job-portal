

# Create your models here.
# jobs/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser # Import AbstractUser

# 1. Custom User Model with Roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('employer', 'Employer'),
        ('applicant', 'Applicant'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='applicant')

    def __str__(self):
        return f"{self.username} ({self.role})"

# 2. Job Model
class Job(models.Model):
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True) # Automatically sets on creation

    def __str__(self):
        return f"{self.title} at {self.company_name}"

# 3. Application Model
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/') # Files uploaded to media/resumes/
    cover_letter = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True) # Automatically sets on creation

    class Meta:
        # Ensures an applicant can only apply once to a specific job
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at'] # Order applications by most recent first

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.username}"