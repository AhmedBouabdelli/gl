from django.urls import path
from django.http import JsonResponse

# Placeholder views
def placeholder_view(request):
    return JsonResponse({"message": "Missions API - Endpoint under construction"})

app_name = 'missions'

urlpatterns = [
    path('', placeholder_view, name='index'),
    path('missions/', placeholder_view, name='missions-list'),
    path('missions/<uuid:pk>/', placeholder_view, name='mission-detail'),
    path('participations/', placeholder_view, name='participations-list'),
]