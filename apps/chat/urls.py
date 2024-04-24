from django.urls import path
from . import views


urlpatterns = [
   path("chat/", views.home_view, name="chat"),
   path("groups/<uuid:uuid>/", views.group_chat_view, name="group")
]
