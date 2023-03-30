from django.urls import path
from .views import *

urlpatterns = [
    path('' , index , name='index'),
    path('post/<str:postId>/<str:slug>' , detay , name='post'),
    path('create/' , create , name = 'create') 
]