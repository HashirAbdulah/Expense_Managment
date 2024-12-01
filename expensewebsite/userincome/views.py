from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from authentication.views import clear_cache_after_logout
from .models import Source, UserIncome
from django.contrib import messages
from django.core.paginator import Paginator
from userpreferences.models import UserPreferences
from datetime import datetime,date
import json

# Create your views here.
@login_required(login_url='/authentication/login')
def index(request):
    source = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user).order_by('-date')
    paginator = Paginator(income, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Try to get user preferences, or create them if they don't exist
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    currency = user_preferences.currency or 'USD'  # Default to USD if no currency set

    context = {
        'income': income,
        'source':source,
        'page_obj': page_obj,
        'currency': currency,
    }
    response = render(request, "income/index.html", context)
    return clear_cache_after_logout(response)


@login_required(login_url='/authentication/login')
def add_income(request):
    source = Source.objects.all()
    context = {
        'source': source,
        'values': request.POST  # Pass the POST data to preserve user input
    }
    response = render(request, 'income/add_income.html', context)

    if request.method == 'GET':
        return response

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        income_date = request.POST.get('income_date')
        source = request.POST.get('source')

        if amount:
            amount = amount.replace(',', '')  # Strip commas before storing
            try:
                amount = float(amount)  # Convert the amount to a float
            except ValueError:
                messages.error(request, 'Invalid Amount Format')
                return render(request, 'income/add_income.html', context)
        else:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
            

        if not description:
            messages.error(request, 'Description is Required')
            return render(request, 'income/add_income.html', context)
            

        if not income_date:
            income_date = date.today()  # Set the current date if the user didn't provide one
        else:
            try:
                # Convert the date string to a date object
                income_date = datetime.strptime(income_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid Date Format')
                return render(request, 'income/add_income.html', context)

        # Create the income record
        UserIncome.objects.create(
            owner=request.user,
            amount=amount,
            description=description,
            date=income_date,  # Use `income_date` instead of `date`
            source=source
        )

        messages.success(request, "Income record saved successfully")
        return redirect('income:income')

    return clear_cache_after_logout(response)


@login_required
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    source = Source.objects.all()
    
    # Store the initial values in context to persist the data on form errors
    context = {
        'income': income,
        'values': income,
        'source': source,
    }
    
    if request.method == 'GET':
        return render(request, 'income/income_edit.html', context)
    
    elif request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('income_date')  # Ensure the correct key name is used
        source = request.POST.get('source')
        
        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'income/income_edit.html', context)
        
        if not description:
            messages.error(request, 'Description is Required')
            return render(request, 'income/income_edit.html', context)
        
        # Check if date is provided and convert it to a date object if needed
        if date:
            try:
                # Convert string date into a datetime.date object
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid Date Format')
                return render(request, 'income/income_edit.html', context)
        
        # Update the expense object
        income.owner = request.user
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description
        income.save()
        
        messages.success(request, "Income updated successfully")
        return redirect('income:income')
        

@login_required
def income_delete(request, id):
    income = get_object_or_404(UserIncome, pk=id)
    if request.method == 'POST':
        income.delete()
        messages.success(request, "Income deleted successfully")
        return redirect('income:income')
    else:
        return render(request, 'income/confirm_delete.html', {'income': income})
    
def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values('id', 'amount', 'source', 'description', 'date')
        return JsonResponse(list(data), safe=False)