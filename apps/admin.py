from django.contrib import admin
from .models import BlogPost



@admin.register(BlogPost)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'pub_date') 
    @admin.action(description="Custom Action Description")
    def custom_action(self, request, queryset):
        # Your custom action logic here
        selected = queryset.update(some_field='some_value')
        self.message_user(request, f'{selected} items were updated successfully.')

    custom_action.short_description = "Custom Action Name"  # Button text
# admin.site.register(BlogPost)
admin.site.site_title = "Administrator"
admin.site.site_header = "Admin"

