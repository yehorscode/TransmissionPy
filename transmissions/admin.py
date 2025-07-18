from django.contrib import admin
from .models import Frequency, Transmission, EncryptionKey # Import your models

@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'description')
    search_fields = ('name', 'number')
    list_filter = ('number',)

@admin.register(Transmission)
class TransmissionAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'scheduled_time', 'code', 'transmission_type', 'status', 'duration_seconds')
    list_filter = ('frequency', 'transmission_type', 'status', 'scheduled_time')
    search_fields = ('code',)
    date_hierarchy = 'scheduled_time'
    readonly_fields = ('created_at',)

@admin.register(EncryptionKey)
class EncryptionKeyAdmin(admin.ModelAdmin):
    list_display = ('key_value', 'is_active', 'valid_from', 'valid_until', 'associated_transmission', 'description')
    list_filter = ('is_active', 'valid_from', 'valid_until')
    search_fields = ('key_value', 'description')
    raw_id_fields = ('associated_transmission',)