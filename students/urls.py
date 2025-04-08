from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'students' 

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('courses/', views.available_courses, name='courses'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
    path("initiate-payment/", views.initiate_payment, name="initiate_payment"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path('tutorials/<int:tutorial_id>/', views.view_tutorial, name='view_tutorial'),
    path('book-slot/', views.book_slot, name='book_slot'),
    path('sessions/history/', views.session_history, name='session_history'),
    path('tutorials/', views.tutorial_list, name='tutorials'),
]