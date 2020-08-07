from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.user),
    path('start', views.quiz),
    path('instructions', views.instructions),
    path('admin/downloadexcel',views.excel),
     path('admin/downloadpdf',views.pdf),
    path('admin/',views.admin),
    path('admin/edit',views.edit),
    path('question',views.next),
    path('admin/change',views.change),
    path('admin/time',views.set_timer),
    path('admin/result',views.result),
]