from django.db import models
from django.conf import settings


class Wallet(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
	balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

	def __str__(self):
		return f"Wallet({self.user.username}): {self.balance}"


class Category(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)

	class Meta:
		verbose_name_plural = 'Categories'

	def __str__(self):
		return self.name


class Transaction(models.Model):
	DEPOSIT = 'DEPOSIT'
	WITHDRAW = 'WITHDRAW'
	TYPE_CHOICES = [
		(DEPOSIT, 'Deposit'),
		(WITHDRAW, 'Withdraw'),
	]

	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
	type = models.CharField(max_length=10, choices=TYPE_CHOICES)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	description = models.CharField(max_length=255, blank=True)
	balance_after = models.DecimalField(max_digits=12, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.type} {self.amount} on {self.wallet.user.username} ({self.created_at})"
