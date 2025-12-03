from django.urls import path
from .views import FigmaReadView

urlpatterns = [
    path("figma/read/", FigmaReadView.as_view()),
]

