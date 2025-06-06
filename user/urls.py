from django.urls import path
from .views import *

urlpatterns = [
    path("", UserListCreateApiView.as_view()),
    path("<int:pk>", UserRetriveUpdateDestroyApiView.as_view()),
    path("profile/", ProfileRetriveView.as_view()),
    path("me/", ProfileRetriveUpdateView.as_view()),
]
