# jobs/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Job, Application

# Form for User Registration
class CustomUserCreationForm(UserCreationForm):
    # Add the 'role' field to the registration form
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='applicant')

    class Meta(UserCreationForm.Meta):
        model = User
        # Inherit existing fields from UserCreationForm.Meta
        # Add 'role' to the fields tuple
        fields = UserCreationForm.Meta.fields + ('role',)

# Form for User Login (can use default AuthenticationForm directly)
class CustomAuthenticationForm(AuthenticationForm):
    pass # No changes needed for basic login

# Form for Employers to Post a Job
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        # Fields that the employer will fill out
        fields = ['title', 'company_name', 'location', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}), # Make description textarea larger
        }


# Form for Applicants to Apply to a Job
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        # Fields that the applicant will fill out
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 8}), # Make cover letter textarea larger
        }