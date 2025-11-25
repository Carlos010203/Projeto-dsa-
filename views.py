from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from .models import Wallet, Transaction
from .forms import TransactionForm


def home_view(request):
	if request.user.is_authenticated:
		return redirect('wallet')
	return redirect('admin:index')


@login_required
def wallet_view(request):
	wallet, created = Wallet.objects.get_or_create(user=request.user)
	return render(request, 'core/wallet.html', {'wallet': wallet})


@login_required
def deposit_view(request):
	wallet, _ = Wallet.objects.get_or_create(user=request.user)
	if request.method == 'POST':
		form = TransactionForm(request.POST)
		if form.is_valid():
			amount = form.cleaned_data['amount']
			category = form.cleaned_data.get('category')
			description = form.cleaned_data['description']
			with db_transaction.atomic():
				# lock wallet row
				w = Wallet.objects.select_for_update().get(pk=wallet.pk)
				w.balance += amount
				w.save()
				Transaction.objects.create(wallet=w, type=Transaction.DEPOSIT, category=category, amount=amount, description=description, balance_after=w.balance)
			return redirect('wallet')
	else:
		form = TransactionForm()
	return render(request, 'core/deposit.html', {'form': form, 'wallet': wallet})


@login_required
def withdraw_view(request):
	wallet, _ = Wallet.objects.get_or_create(user=request.user)
	if request.method == 'POST':
		form = TransactionForm(request.POST)
		if form.is_valid():
			amount = form.cleaned_data['amount']
			category = form.cleaned_data.get('category')
			description = form.cleaned_data['description']
			with db_transaction.atomic():
				w = Wallet.objects.select_for_update().get(pk=wallet.pk)
				if w.balance < amount:
					form.add_error('amount', 'Insufficient funds')
				else:
					w.balance -= amount
					w.save()
					Transaction.objects.create(wallet=w, type=Transaction.WITHDRAW, category=category, amount=amount, description=description, balance_after=w.balance)
					return redirect('wallet')
	else:
		form = TransactionForm()
	return render(request, 'core/withdraw.html', {'form': form, 'wallet': wallet})


@login_required
def history_view(request):
	wallet, _ = Wallet.objects.get_or_create(user=request.user)
	transactions = wallet.transactions.all()
	return render(request, 'core/history.html', {'wallet': wallet, 'transactions': transactions})


@login_required
def reports_view(request):
	from django.utils import timezone
	from datetime import timedelta
	from django.db.models import Sum
	
	wallet, _ = Wallet.objects.get_or_create(user=request.user)
	
	# Filtros
	start_date = request.GET.get('start_date')
	end_date = request.GET.get('end_date')
	
	transactions = wallet.transactions.all()
	
	if start_date:
		transactions = transactions.filter(created_at__gte=start_date)
	if end_date:
		transactions = transactions.filter(created_at__lte=end_date)
	
	# Agregação por categoria (apenas saques/gastos)
	by_category = transactions.filter(type=Transaction.WITHDRAW).values('category__name').annotate(total=Sum('amount')).order_by('-total')
	
	# Dados para gráfico
	categories_data = []
	amounts_data = []
	for row in by_category:
		cat_name = row['category__name'] or 'Sem categoria'
		categories_data.append(cat_name)
		amounts_data.append(float(row['total']) if row['total'] else 0)
	
	total_withdraws = transactions.filter(type=Transaction.WITHDRAW).aggregate(Sum('amount'))['amount__sum'] or 0
	total_deposits = transactions.filter(type=Transaction.DEPOSIT).aggregate(Sum('amount'))['amount__sum'] or 0
	
	context = {
		'wallet': wallet,
		'transactions': transactions,
		'by_category': by_category,
		'categories_data': categories_data,
		'amounts_data': amounts_data,
		'total_withdraws': total_withdraws,
		'total_deposits': total_deposits,
		'start_date': start_date,
		'end_date': end_date,
	}
	
	return render(request, 'core/reports.html', context)
