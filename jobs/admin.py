# jobs/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User as DefaultUser # Import default User model
from .models import User, Job, Application

# Customize the User model in the admin
class CustomUserAdmin(UserAdmin):
    # Add 'role' to the fields displayed when editing a user
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    # Add 'role' to the fields displayed when adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    # Customize the list view in the admin
    list_display = ('username', 'email', 'id', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active') # Add role to filters
    search_fields = ('username', 'email', 'first_name', 'last_name') # Add search fields

# Unregister the default User model
# IMPORTANT: Use the actual default User model class, not get_model()
try:
    admin.site.unregister(DefaultUser) # Corrected line: pass the imported DefaultUser model
except admin.sites.NotRegistered:
    pass # It's fine if it's not registered (e.g., on first run or if unregister was done elsewhere)

admin.site.register(User, CustomUserAdmin) # Register your custom User model


# Customize Job model in the admin
@admin.register(Job) # Decorator to register the model
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'posted_by', 'created_at')
    list_filter = ('location', 'company_name', 'posted_by', 'created_at')
    search_fields = ('title', 'company_name', 'location', 'description', 'posted_by__username')
    date_hierarchy = 'created_at' # Adds a date navigation filter
    raw_id_fields = ('posted_by',) # For ForeignKey, useful if many users

# Customize Application model in the admin
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'applied_at', 'get_job_company', 'get_job_location', 'get_applicant_email')
    list_filter = ('applied_at', 'job__company_name', 'job__location', 'applicant__role')
    search_fields = ('job__title', 'applicant__username', 'cover_letter', 'job__company_name', 'job__location')
    raw_id_fields = ('job', 'applicant',) # For ForeignKeys

    # Custom methods to display related fields in the list view
    def get_job_company(self, obj):
        return obj.job.company_name
    get_job_company.short_description = 'Company Name' # Column header
    get_job_company.admin_order_field = 'job__company_name' # Allows sorting by this field

    def get_job_location(self, obj):
        return obj.job.location
    get_job_location.short_description = 'Job Location'
    get_job_location.admin_order_field = 'job__location'

    def get_applicant_email(self, obj):
        return obj.applicant.email
    get_applicant_email.short_description = 'Applicant Email'
    get_applicant_email.admin_order_field = 'applicant__email'