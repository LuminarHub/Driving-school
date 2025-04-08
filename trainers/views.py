from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from trainers.models import Trainer
from .forms import AssignTrainerVehicleForm,StudentAssignmentForm
from students.models import Student
from django.utils import timezone
from trainers.forms import TrainerForm,TrainerProfileForm,TrainingSessionForm
from vehicles.models import Vehicle
@login_required
def trainer_list(request):
    trainers = Trainer.objects.all()
    return render(request, 'trainers/trainer_list.html', {'trainers': trainers})

#
from django.urls import reverse


@login_required
def trainer_detail(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    assigned_sessions = TrainingSession.objects.filter(trainer=trainer).select_related('student__user', 'vehicle', 'student_package')

    if request.method == "POST":
        session_id = request.POST.get("session_id")
        session = get_object_or_404(TrainingSession, id=session_id, trainer=trainer)

        # Toggle session completion status
        session.completed = not session.completed
        session.save()
        messages.success(request, "Session status updated successfully!")
        return redirect('trainers:trainer_detail', trainer_id=trainer.id)
    unique_students = {}
    for session in assigned_sessions:
        if session.student.id not in unique_students:
            unique_students[session.student.id] = session
    return render(request, 'trainers/trainer_detail.html', {
        'trainer': trainer,
        'assigned_sessions': assigned_sessions,
        'unique_students': unique_students.values(),
    })
    
    
@login_required
def trainer_create(request):
    if request.method == 'POST':
        form = TrainerForm(request.POST)
        if form.is_valid():
            trainer = form.save()
            messages.success(request, 'Trainer created successfully.')
            return redirect('admins:manage_trainers', trainer_id=trainer.id)
    else:
        form = TrainerForm()
    return render(request, 'trainers/trainer_form.html', {'form': form, 'action': 'Create'})

@login_required
def trainer_update(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    if request.method == 'POST':
        form = TrainerForm(request.POST, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trainer updated successfully.')
            return redirect('trainers:trainer_detail', trainer_id=trainer.id)
    else:
        form = TrainerForm(instance=trainer)
    return render(request, 'trainers/trainer_form.html', {'form': form, 'trainer': trainer, 'action': 'Update'})

@login_required
def trainer_delete(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    if request.method == 'POST':
        trainer.delete()
        messages.success(request, 'Trainer deleted successfully.')
        return redirect('trainer_list')
    return render(request, 'trainers/trainer_confirm_delete.html', {'trainer': trainer})

@login_required
def trainer_schedule(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    # Logic to get trainer's schedule
    # This would interact with a Schedule model that you might need to create
    return render(request, 'trainers/trainer_schedule.html', {'trainer': trainer})

@login_required
def trainer_dashboard(request):
    trainer = get_object_or_404(Trainer, user=request.user)
    assigned_students = trainer.student_set.all()
    
    # Replace this with the actual session model query
    from students.models import TrainingSession  # if your session model is named this
    upcoming_sessions = TrainingSession.objects.filter(trainer=trainer, session_date__gte=timezone.now()).order_by('session_date')[:5]

    return render(request, 'trainers/dashboard.html', {
        'trainer': trainer,
        'assigned_students': assigned_students,
        'upcoming_sessions': upcoming_sessions
    })

from students.models import StudentPackage, Payment

from django.db.models import Q

from django.db.models import Exists, OuterRef

@login_required
def students_to_assign(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)

    # Get students in training sessions who haven't been assigned a trainer or vehicle
    unassigned_sessions = TrainingSession.objects.filter(
        trainer__isnull=True,  # No trainer assigned
        vehicle__isnull=True,   # No vehicle assigned
        student_package__isnull=False  # Ensure they have a package
    ).select_related('student__user', 'student_package')

    # Ensure they have paid
    paid_student_ids = Payment.objects.filter(
        student_package=OuterRef('student_package')
    ).values('student_package')

    eligible_sessions = unassigned_sessions.annotate(
        has_paid=Exists(paid_student_ids)
    ).filter(has_paid=True)

    return render(request, 'trainers/assign_students.html', {
        'trainer': trainer,
        'sessions': eligible_sessions  
    })

@login_required
def assign_trainer_vehicles(request, session_id):
    session = get_object_or_404(TrainingSession, id=session_id)

    if request.method == "POST":
        trainer_id = request.POST.get("trainer")
        vehicle_id = request.POST.get("vehicle")

        session.trainer = get_object_or_404(Trainer, id=trainer_id)
        session.vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        session.save()

        messages.success(request, "Trainer and Vehicle assigned successfully!")
        return redirect('trainers:students_to_assign', trainer_id=session.trainer.id)

    trainers = Trainer.objects.all()
    vehicles = Vehicle.objects.all()

    return render(request, 'trainers/vehicle_assign_trainer.html', {
        'session': session,
        'trainers': trainers,
        'vehicles': vehicles
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from students.models import Student
from .forms import StudentAssignmentForm


@login_required
def assign_trainer_vehicle(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentAssignmentForm(request.POST, instance=student)
        if form.is_valid():
            assigned_student = form.save(commit=False)
            assigned_student.trainer = form.cleaned_data['trainer']
            assigned_student.vehicle = form.cleaned_data['vehicle']
            assigned_student.save()
            print("POSTED TRAINER:", form.cleaned_data['trainer'])
            print("POSTED VEHICLE:", form.cleaned_data['vehicle'])
            print(f"Assigned student {assigned_student.id} to trainer {assigned_student.trainer}")
            messages.success(request, "Trainer and vehicle assigned successfully!")
            return redirect('trainers:students_to_assign', trainer_id=assigned_student.trainer.id if assigned_student.trainer else 1)
    else:
        form = StudentAssignmentForm(instance=student)

    return render(request, 'trainers/assign_trainer_vehicle.html', {
        'form': form,
        'student': student,
    })

from students.models import TrainingSession

@login_required
def unassigned_sessions(request):
    sessions = TrainingSession.objects.filter(
        Q(trainer__isnull=True) | Q(vehicle__isnull=True)
    ).select_related('student', 'student__user')

    return render(request, 'admin/unassigned_sessions.html', {
        'sessions': sessions
    })

# @login_required
# def assign_training_session(request, student_id):
#     student = get_object_or_404(Student, id=student_id)

#     # ⛔ Prevent assigning session if trainer is not assigned
#     if not student.trainer:
#         messages.warning(request, "Trainer not assigned to this student yet.")
#         return redirect('trainers:assign_trainer_vehicle', student_id=student.id)

#     if request.method == 'POST':
#         form = TrainingSessionForm(request.POST)
#         if form.is_valid():
#             session = form.save(commit=False)
#             session.student = student
#             session.save()
#             messages.success(request, "Training session assigned successfully.")
#             return redirect('trainers:students_to_assign', trainer_id=student.trainer.id)
#     else:
#         form = TrainingSessionForm()

#     return render(request, 'trainers/assign_training_session.html', {
#         'form': form,
#         'student': student
#     })

@login_required
def assign_trainer_to_session(request, session_id):
    session = get_object_or_404(TrainingSession, id=session_id)

    if request.method == 'POST':
        form = AssignTrainerVehicleForm(request.POST)
        if form.is_valid():
            trainer = form.cleaned_data['trainer']
            vehicle = form.cleaned_data['vehicle']

            # Check for double-booking
            trainer_conflict = TrainingSession.objects.filter(
                trainer=trainer,
                session_date=session.session_date,
                time_slot=session.time_slot
            ).exclude(id=session.id).exists()

            vehicle_conflict = TrainingSession.objects.filter(
                vehicle=vehicle,
                session_date=session.session_date,
                time_slot=session.time_slot
            ).exclude(id=session.id).exists()

            if trainer_conflict:
                form.add_error('trainer', 'Trainer is already booked for this slot.')
            elif vehicle_conflict:
                form.add_error('vehicle', 'Vehicle is already booked for this slot.')
            else:
                session.trainer = trainer
                session.vehicle = vehicle
                session.save()
                messages.success(request, "Trainer and vehicle assigned successfully.")
                return redirect('trainers:unassigned_sessions')  # Or wherever you list unassigned sessions
    else:
        form = AssignTrainerVehicleForm()

    return render(request, 'admin/assign_trainer_vehicle.html', {
        'form': form,
        'session': session,
    })