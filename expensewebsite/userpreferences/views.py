from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages 

def index(request):
    exists = UserPreferences.objects.filter(user=request.user).exists()
    user_preferences = None
    if exists:
        user_preferences = UserPreferences.objects.get(user=request.user)
    
    # Initialize currencies as an empty list
    currencies = []

    # Load currencies from the JSON file
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                for key, value in data.items():
                    currencies.append({'name': key, 'value': value})
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Handle GET and POST requests
    if request.method == 'POST':
        currency = request.POST.get('currency')
        
        if exists:
            # Update the existing UserPreferences
            user_preferences.currency = currency
            user_preferences.save()
        else:
            # Create a new UserPreferences instance
            UserPreferences.objects.create(user=request.user, currency=currency)

        messages.success(request, "Changes Saved")
    
    # Render the template with the currencies and user preferences
    return render(
        request,
        'userpreferences/index.html',
        {'currencies': currencies, 'user_preferences': user_preferences}
    )
