from django.contrib import admin
from .models import FamilyBeneficiary, Quote, SubscriptionPackage, UserProfile, Transaction, UserSubscription

# FamilyBeneficiary Admin
class FamilyBeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'surname', 'relationship', 'date_of_birth', 'gender', 'mobile_number', 'created_at', 'updated_at')
    search_fields = ('user__username', 'first_name', 'surname', 'relationship')
    list_filter = ('gender', 'relationship')
    readonly_fields = ('created_at', 'updated_at')

# Quote Admin
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'total_amount', 'created_at', 'updated_at')
    readonly_fields = ('quote_number', 'total_amount', 'created_at', 'updated_at')

# SubscriptionPackage Admin
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_monthly', 'price_yearly', 'features')
    readonly_fields = ('price_monthly', 'price_yearly')
    search_fields = ('name', 'features')
    list_filter = ('name',)


# admin.py (Add the UserSubscriptionAdmin)

class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_package', 'start_date', 'end_date', 'status')  # Fields to display in the list view
    search_fields = ('user__username', 'subscription_package__name')  # Allows searching by username or package name
    list_filter = ('status', 'subscription_package')  # Filter by status and subscription package
    readonly_fields = ('start_date', 'end_date')  # Make start_date and end_date readonly
    ordering = ('-start_date',)  # Order by start_date, newest first

admin.site.register(UserSubscription, UserSubscriptionAdmin)



# UserProfile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'identification_type', 'identification_number', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('identification_type',)

# Transaction Admin
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'status', 'user', 'quote', 'created_at', 'updated_at')
    readonly_fields = ('transaction_id', 'amount', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'user__username')

# Register models
admin.site.register(FamilyBeneficiary, FamilyBeneficiaryAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(SubscriptionPackage, SubscriptionPackageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transaction, TransactionAdmin)
