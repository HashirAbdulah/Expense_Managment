from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from authentication.views import clear_cache_after_logout
# Create your views here.
@login_required
def index(request):
    response = render(request, "expenses/index.html")
    return clear_cache_after_logout(response)

@login_required
def add_expense(request):
    response = render(request, 'expenses/add_expense.html')
    return clear_cache_after_logout(response)
