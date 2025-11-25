from django.contrib import admin
from .models import Wallet, Category, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
	list_display = ('user', 'balance')
	search_fields = ('user__username', 'user__email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('wallet', 'type', 'category', 'amount', 'balance_after', 'created_at')
	list_filter = ('type', 'category', 'created_at')
	search_fields = ('wallet__user__username', 'description')
