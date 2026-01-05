from django.urls import path
from django.http import JsonResponse

# Placeholder views
def placeholder_view(request):
    return JsonResponse({"message": "Audit API - Endpoint under construction"})

app_name = 'audit'

urlpatterns = [
    path('', placeholder_view, name='index'),
    path('logs/', placeholder_view, name='logs-list'),
]