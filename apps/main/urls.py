from django.urls import path
from apps.main.views import SearchInFilesView

urlpatterns = [
    path("search/", SearchInFilesView.as_view(), name="search"),
]