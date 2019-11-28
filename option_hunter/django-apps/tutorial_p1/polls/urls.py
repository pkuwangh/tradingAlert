from django.urls import path
from . import views

# to call the view, we need to map it to a URL
# and for this we need a URLconf
urlpatterns = [
    path('', views.index, name='index'),
]
