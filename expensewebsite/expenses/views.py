from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from authentication.views import clear_cache_after_logout
from .models import Category,Expense
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.
@login_required
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner = request.user).order_by('-date')
    paginator = Paginator(expenses,2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
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

@login_required
def expense_edit(request,id):
    expense = Expense.objects.get(pk= id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html',context)
    
    elif request.method == 'POST':
        if request.method == 'POST':
            amount = request.POST.get('amount')
            description = request.POST.get('description')
            date = request.POST.get('date')
            category = request.POST.get('category')
            if not amount:
                messages.error(request,'Amount is Required')
                response = render(request, 'expenses/edit_expense.html',context)

            if not description:
                messages.error(request,'Description is Required')
                response = render(request, 'expenses/edit_expense.html',context)
            
            expense.owner = request.user
            expense.amount = amount
            expense.date = date
            expense.category = category
            expense.description = description
            expense.save()
            messages.success(request,"Expense updated successfully")
            
            return redirect('expenses:expenses') 

        return clear_cache_after_logout(response)

@login_required
def expense_delete(request, id):
    # Get the expense, or show a 404 error if not found
    expense = get_object_or_404(Expense, pk=id)
    
    # Only allow deletion via POST to prevent accidental deletions
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully")
        return redirect('expenses:expenses')
    else:
        # Handle GET request by asking for confirmation
        return render(request, 'expenses/confirm_delete.html', {'expense': expense})
