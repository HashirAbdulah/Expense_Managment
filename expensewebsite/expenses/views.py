from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from authentication.views import clear_cache_after_logout
from .models import Category,Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from userpreferences.models import UserPreferences
from django.db.models import Sum
from datetime import datetime, date, timedelta
# Create your views here.
@login_required
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Try to get user preferences, or create them if they don't exist
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    currency = user_preferences.currency or 'USD'  # Default to USD if no currency set

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
    }
    response = render(request, "expenses/index.html", context)
    return clear_cache_after_logout(response)


@login_required
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST  # Pass the POST data to preserve user input
    }
    response = render(request, 'expenses/add_expense.html', context)

    if request.method == 'GET':
        return response

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        expense_date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if amount:
            amount = amount.replace(',', '')  # Strip commas before storing
            try:
                amount = float(amount)  # Convert the amount to a float
            except ValueError:
                messages.error(request, 'Invalid Amount Format')
                return render(request, 'expenses/add_expense.html', context)
        else:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)

        if not description:
            messages.error(request, 'Description is Required')
            return render(request, 'expenses/add_expense.html', context)

        if not expense_date:
            expense_date = date.today()  # Set the current date if the user didn't provide one
        else:
            try:
                # Convert the date string to a date object
                expense_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid Date Format')
                return render(request, 'expenses/add_expense.html', context)

        # Create the expense record
        Expense.objects.create(
            owner=request.user,
            amount=amount,
            description=description,
            date=expense_date,  # Use `expense_date` instead of `date`
            category=category
        )

        messages.success(request, "Expense created successfully")
        return redirect('expenses:expenses')  # Redirect to the expenses list page

    return clear_cache_after_logout(response)

@login_required
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    
    # Store the initial values in context to persist the data on form errors
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
    }
    
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    
    elif request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        expense_date = request.POST.get('expense_date')  # Ensure the correct key name is used
        category = request.POST.get('category')
        
        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'expenses/edit_expense.html', context)
        
        if not description:
            messages.error(request, 'Description is Required')
            return render(request, 'expenses/edit_expense.html', context)
        
        # Check if date is provided and convert it to a date object if needed
        if expense_date:
            try:
                # Convert string date into a datetime.date object
                expense_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid Date Format')
                return render(request, 'expenses/edit_expense.html', context)
        
        # Update the expense object
        expense.owner = request.user
        expense.amount = amount
        expense.date = expense_date
        expense.category = category
        expense.description = description
        expense.save()
        
        messages.success(request, "Expense updated successfully")
        return redirect('expenses:expenses')

@login_required
def expense_delete(request, id):
    expense = get_object_or_404(Expense, pk=id)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully")
        return redirect('expenses:expenses')
    else:
        return render(request, 'expenses/confirm_delete.html', {'expense': expense})
    
@login_required
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values('id', 'amount', 'category', 'description', 'date')
        return JsonResponse(list(data), safe=False)

@login_required
def expense_category_summary(request):
    today_date = date.today()  # Use `date` directly
    six_months_ago = today_date - timedelta(days=30 * 6)

    # Fetch expenses for the last 6 months
    expenses = Expense.objects.filter(
        owner=request.user, date__gte=six_months_ago, date__lte=today_date
    )

    # Aggregate total amount by category
    final_rep = (
        expenses.values('category')  # Group by category
        .annotate(total_amount=Sum('amount'))  # Calculate total amount for each category
        .order_by('category')  # Optional: Sort by category
    )

    # Transform the data into a dictionary
    category_data = {item['category']: item['total_amount'] for item in final_rep}

    return JsonResponse({'expense_category_data': category_data}, safe=False)


@login_required
def stats_view(request):
    return render(request, 'expenses/stats.html')