from django.contrib import admin
from .models import UserProfile, Quote, Transaction, FamilyBeneficiary


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for managing user profiles."""
    list_display = (
        'user', 'address', 'state', 'town', 'date_of_birth', 
        'marital_status', 'identification_type', 'identification_number'
    )
    list_filter = ('state', 'marital_status', 'identification_type')
    search_fields = ('user__username', 'user__email', 'identification_number', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user', 'address', 'state', 'town', 'date_of_birth', 
                'marital_status'
            )
        }),
        ('Identification', {
            'fields': (
                'identification_type', 'identification_number', 
                'identification_image'
            )
        }),
        ('Medical Details', {
            'fields': ('current_medical_condition', 'pre_existing_conditions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    """Admin interface for managing quotes."""
    list_display = ('user', 'plan', 'amount_paid', 'is_paid', 'created_at')
    list_filter = ('plan', 'is_paid', 'created_at')
    search_fields = ('user__username', 'user__email', 'plan')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'plan', 'amount_paid', 'is_paid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for managing transactions."""
    list_display = (
        'user', 'quote', 'amount', 'payment_gateway', 
        'transaction_id', 'status', 'created_at'
    )
    list_filter = ('payment_gateway', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'quote', 'amount', 'payment_gateway', 'transaction_id', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(FamilyBeneficiary)
class FamilyBeneficiaryAdmin(admin.ModelAdmin):
    """Admin interface for managing family beneficiaries."""
    list_display = (
        'user', 'first_name', 'surname', 'relationship', 
        'gender', 'date_of_birth', 'mobile_number', 'created_at'
    )
    list_filter = ('relationship', 'gender', 'created_at')
    search_fields = (
        'user__username', 'user__email', 'first_name', 'surname', 'mobile_number'
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': (
                'user', 'first_name', 'surname', 'relationship', 
                'gender', 'date_of_birth', 'mobile_number', 'passport_photo'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
