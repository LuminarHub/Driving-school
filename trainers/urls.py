from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    path('', views.trainer_dashboard, name='dashboard'),
    path('trainers/', views.trainer_list, name='trainer_list'),
    path('<int:trainer_id>/', views.trainer_detail, name='trainer_detail'),
    path('create/', views.trainer_create, name='trainer_create'),
    path('<int:trainer_id>/update/', views.trainer_update, name='trainer_update'),
    path('<int:trainer_id>/delete/', views.trainer_delete, name='trainer_delete'),
    path('<int:trainer_id>/schedule/', views.trainer_schedule, name='trainer_schedule'),
    path('assign_trainer_vehicles/<int:session_id>/', views.assign_trainer_vehicles, name='assign_trainer_vehicles'),

    path('assign-students/<int:trainer_id>/', views.students_to_assign, name='students_to_assign'),
    path('assign-trainer-vehicle/<int:student_id>/', views.assign_trainer_vehicle, name='assign_trainer_vehicle'),
    path('unassigned-sessions/', views.unassigned_sessions, name='unassigned_sessions'),
    path('assign-session/<int:session_id>/', views.assign_trainer_to_session, name='assign_training_session'),
]