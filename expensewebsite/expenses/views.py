from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from authentication.views import clear_cache_after_logout
from .models import Category,Expense
from django.contrib import messages
# Create your views here.
@login_required
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner = request.user).order_by('-date')
    context = {
        'expenses': expenses
    }
    response = render(request, "expenses/index.html",context)
    return clear_cache_after_logout(response)

@login_required
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values':request.POST
    }
    response = render(request, 'expenses/add_expense.html',context)

    if request.method == 'GET':
        return response
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')
        if not amount:
            messages.error(request,'Amount is Required')
            response = render(request, 'expenses/add_expense.html',context)

        if not description:
            messages.error(request,'Description is Required')
            response = render(request, 'expenses/add_expense.html',context)

        Expense.objects.create(owner = request.user, amount = amount, description = description, date = date, category = category)
        messages.success(request,"Expense created successfully")
        
        return redirect('expenses:expenses') 

    return clear_cache_after_logout(response)
    
