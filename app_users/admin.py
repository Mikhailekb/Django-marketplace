from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'phone', 'avatar', 'name')
    readonly_fields = ('user',)
    search_fields = ('id', 'user')


