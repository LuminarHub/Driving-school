from datetime import timedelta, date
from .models import TrainingSession, Trainer

def assign_sessions(student_package):
    student = student_package.student
    package = student_package.package
    vehicle_type = package.vehicle_type
    total_sessions = package.sessions

    # ✅ Select one trainer who has that vehicle type
    trainer = Trainer.objects.filter(assigned_vehicles__vehicle_type=vehicle_type).first()

    # ✅ Get one of the trainer's assigned vehicles of that type
    vehicle = trainer.assigned_vehicles.filter(vehicle_type=vehicle_type).first() if trainer else None

    if not trainer or not vehicle:
        print("No trainer or vehicle available for the selected vehicle type.")
        return  # Or raise an exception / log this

    start_date = date.today()

    # Simple logic — assigns one session per day, first time slot
    for i in range(total_sessions):
        session_date = start_date + timedelta(days=i)
        time_slot = 'morning_1'  # First time slot (you can rotate them later if needed)

        TrainingSession.objects.create(
            student=student,
            trainer=trainer,
            vehicle=vehicle,
            student_package=student_package,
            session_date=session_date,
            time_slot=time_slot,
            completed=False
        )