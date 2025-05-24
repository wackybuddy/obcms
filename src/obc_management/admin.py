from django.contrib import admin
from django.urls import reverse

# Customize the default admin site
admin.site.site_header = 'OBC Management System Admin'
admin.site.site_title = 'OBC Admin'
admin.site.index_title = 'Administration Dashboard'

# Override the each_context method to customize site_url
original_each_context = admin.site.each_context

def custom_each_context(request):
    context = original_each_context(request)
    # Override the site_url to point to the dashboard
    context['site_url'] = reverse('common:dashboard')
    return context

admin.site.each_context = custom_each_context