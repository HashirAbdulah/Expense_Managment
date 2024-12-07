from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'expenses'

urlpatterns = [
    path('', views.index, name='expenses'),
    path('add_expense', views.add_expense, name='add_expense'),
    path('expense_edit/<int:id>', views.expense_edit, name='expense_edit'),
    path('expense_delete/<int:id>', views.expense_delete, name='expense_delete'),
    path('search-expenses', csrf_exempt(views.search_expenses),name="search_expenses"),
    path('export_csv' , csrf_exempt(views.export_csv),name="export_csv"),
    path('export_excel' , csrf_exempt(views.export_excel),name="export_excel"),
    path('export_pdf' , csrf_exempt(views.export_pdf),name="export_pdf"),
    path('expense_category_summary', views.expense_category_summary, name="expense_category_summary"),
    path('stats', views.stats_view,name="stats"),
]
