from django.urls import path
from savedJob.views import *


urlpatterns = [
    path("savedlist/", SavedJobListView.as_view()),
    path("add/", SavedJobCreateView.as_view()),
    path("delete/<int:pk>/", SavedJobDeleteView.as_view()),
]
 