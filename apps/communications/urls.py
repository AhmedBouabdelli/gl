from django.urls import path
from django.http import JsonResponse

# Placeholder views
def placeholder_view(request):
    return JsonResponse({"message": "Communications API - Endpoint under construction"})

app_name = 'communications'

urlpatterns = [
    path('', placeholder_view, name='index'),
    path('messages/', placeholder_view, name='messages-list'),
    path('groups/', placeholder_view, name='groups-list'),
    path('notifications/', placeholder_view, name='notifications-list'),
]