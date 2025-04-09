from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, TrainingSession, Tutorial,StudentPackage,Payment,Trainer,Course,TrainingPackage,Vehicle
from .forms import StudentProfileForm, SessionBookingForm,PaymentForm
import uuid 
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
import razorpay
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import timedelta, date
from django.utils import timezone
from students.models import StudentPackage

@login_required
def dashboard(request):
    """Student dashboard showing upcoming sessions and available tutorials"""
    try:
        student = Student.objects.get(user=request.user)
        
        # Get the active package (latest one with payment status True)
        student_package = StudentPackage.objects.filter(student=student, payment_status=True).last()
        
        # Get all purchased packages
        all_packages = StudentPackage.objects.filter(student=student, payment_status=True).order_by('-purchase_date')
        
        upcoming_sessions = TrainingSession.objects.filter(
            student=student,
            session_date__gte=timezone.now().date()
        ).order_by('session_date', 'time_slot')
        
        # Also get completed sessions for history
        completed_sessions = TrainingSession.objects.filter(
            student=student,
            completed=True
        ).order_by('-session_date', 'time_slot')
    
    except Student.DoesNotExist:
        student = Student.objects.create(
            user=request.user,
            address="",
            phone_number="",
            student_type="local"
        )
        student_package = None
        all_packages = []
        upcoming_sessions = []
        completed_sessions = []
    
    tutorials = Tutorial.objects.filter(visible=True)
    
    context = {
        'student': student,
        'student_package': student_package,
        'all_packages': all_packages,
        'upcoming_sessions': upcoming_sessions,
        'completed_sessions': completed_sessions,
        'tutorials': tutorials,
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def profile(request):
    """View and update student profile"""
    student = get_object_or_404(Student, user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('students:profile')
    else:
        form = StudentProfileForm(instance=student)
    
    return render(request, 'students/profile.html', {'form': form})


# in students/views.py
from django.contrib.admin.views.decorators import staff_member_required

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})

def available_courses(request):
    print("🔍 DEBUG: available_courses view is executing...")
    
    courses = Course.objects.prefetch_related('packages').all()
    
    print(f"📢 Found {courses.count()} courses")
    for course in courses:
        print(f"✅ Course: {course.title}, Packages: {list(course.packages.all())}")
    
    return render(request, "students/courses.html", {"courses": courses}) # Temporary response for testing


import re

def convert_to_embed(url):
    # Match different YouTube URL patterns
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([\w-]+)",  # Standard YouTube link
        r"(?:https?:\/\/)?youtu\.be\/([\w-]+)",                        # Shortened youtu.be link
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([\w-]+)"    # Already an embed link
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"

    return url  # Return original URL if no match is found


@login_required
def view_tutorial(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, id=tutorial_id, visible=True)

    # Ensure the video URL is converted
    tutorial.video_url = convert_to_embed(tutorial.video_url)

    # Debug the converted URL
    print("Converted URL:", tutorial.video_url)

    return render(request, 'students/tutorial_detail.html', {'tutorial': tutorial})

@login_required
def session_history(request):
    """View past training sessions"""
    student = get_object_or_404(Student, user=request.user)
    completed_sessions = TrainingSession.objects.filter(
        student=student, completed=True
    ).order_by('-session_date', '-time_slot')
    
    return render(request, 'students/session_history.html', {'sessions': completed_sessions})


@login_required
def tutorial_list(request):
    """View all available tutorials"""
    tutorials = Tutorial.objects.filter(visible=True).order_by('-updated_at')
    return render(request, 'students/tutorial_list.html', {'tutorials': tutorials})




logger = logging.getLogger(__name__)

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
@login_required
def initiate_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            package_id = data.get("package")

            student = Student.objects.get(user=request.user)

            if not package_id:
                return JsonResponse({"error": "Missing package ID"}, status=400)

            package = get_object_or_404(TrainingPackage, id=package_id)

            # ✅ Prevent duplicate purchases
            if StudentPackage.objects.filter(student=student, payment_status=True).exists():
                return JsonResponse({"error": "You have already purchased a package."}, status=400)

            # ✅ Create a new StudentPackage if not exists or in progress
            student_package, created = StudentPackage.objects.get_or_create(
                student=student,
                package=package,
                defaults={"payment_status": False, "remaining_sessions": package.sessions}
            )

            # ✅ Avoid duplicate payment initiation
            existing_payment = Payment.objects.filter(
                student_package=student_package,
                status="pending"
            ).first()

            if existing_payment:
                return JsonResponse({
                    "order_id": existing_payment.razorpay_order_id,
                    "amount": int(package.price * 100),
                    "currency": "INR",
                    "razorpay_key": settings.RAZORPAY_KEY_ID,
                    "package_id": package_id
                })

            # ✅ Create Razorpay order
            order_data = {
                "amount": int(package.price * 100),
                "currency": "INR",
                "payment_capture": "1",
            }
            order = razorpay_client.order.create(data=order_data)

            # ✅ Save payment object
            payment = Payment.objects.create(
                student_package=student_package,
                amount=package.price,
                razorpay_order_id=order["id"],
                status="pending",
            )

            return JsonResponse({
                "order_id": payment.razorpay_order_id,
                "amount": order_data["amount"],
                "currency": order_data["currency"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "package_id": package_id
            })

        except Exception as e:
            logger.error(f"Error in initiate_payment: {e}")
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)

            # Verify Razorpay Signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result:
                # ✅ Mark payment as successful
                payment.status = "successful"
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.save()

                # ✅ Mark student package as paid
                student_package = payment.student_package
                student_package.payment_status = True
                student_package.save()

                # ❌ Removed: assign_sessions(student_package)

                return JsonResponse({"status": "success"})
            else:
                payment.status = "failed"
                payment.save()
                return JsonResponse({"status": "failure"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


from .forms import SlotBookingForm
from django.http import HttpResponseForbidden

# @login_required
# def book_slot(request):
#     try:
#         user = request.user
#         student = Student.objects.get(user=user)
#         print("Student profile found:", student)  
#     except Student.DoesNotExist:
#         print("Student profile does not exist")  # Debug: print if student profile doesn't exist
#         return HttpResponseForbidden("You must be logged in as a student to book a session.")

#     try:
#         # Check if the student has a valid package with payment status
#         student_package = StudentPackage.objects.get(student=student, payment_status=True)
#     except StudentPackage.DoesNotExist:
#         # If no package is found or payment is not successful
#         messages.error(request, "You haven't purchased a package yet.")
#         return redirect('students:courses')

#     # Check if the student has already booked a slot
#     if student_package.has_booked_slot:
#         messages.info(request, "You’ve already booked a slot.")
#         return redirect('students:dashboard')

#     if request.method == 'POST':
#         form = SlotBookingForm(request.POST, student=student)  # Pass the student object to the form
#         if form.is_valid():
#             session_date = form.cleaned_data['session_date']
#             time_slot = form.cleaned_data['time_slot']

#             # Create a training session for the student
#             TrainingSession.objects.create(
#                 student=student,
#                 student_package=student_package,
#                 session_date=session_date,
#                 time_slot=time_slot,
#                 trainer=None,
#                 vehicle=None
#             )

#             # Mark the slot as booked
#             student_package.has_booked_slot = True
#             student_package.save()

#             messages.success(request, "Slot booked! Admin will assign trainer & vehicle soon.")
#             return redirect('students:dashboard')
#     else:
#         # Initialize the form if GET request
#         form = SlotBookingForm(student=student)

#     return render(request, 'students/book_slot.html', {'form': form})
from django.utils.timezone import now

@login_required
def book_slot(request):
    try:
        user = request.user
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return HttpResponseForbidden("You must be logged in as a student to book a session.")

    try:
        student_package = StudentPackage.objects.get(student=student, payment_status=True)
    except StudentPackage.DoesNotExist:
        messages.error(request, "You haven't purchased a package yet.")
        return redirect('students:courses')

    if student_package.remaining_sessions <= 0:
        messages.info(request, "You've used all sessions in your package. Please purchase a new package.")
        return redirect('students:dashboard')

    if request.method == 'POST':
        form = SlotBookingForm(request.POST, student=student)
        if form.is_valid():
            session_date = form.cleaned_data['session_date']
            time_slot = form.cleaned_data['time_slot']

            # Check if the student has already booked a session for this date
            if TrainingSession.objects.filter(student=student, session_date=session_date).exists():
                messages.warning(request, "You have already booked a session for this date. Please choose another day.")
                return redirect('students:book_slot')

            # Create a training session for the student
            TrainingSession.objects.create(
                student=student,
                student_package=student_package,
                session_date=session_date,
                time_slot=time_slot,
                trainer=None,
                vehicle=None
            )

            # Decrease remaining sessions
            student_package.remaining_sessions -= 1
            student_package.save()

            messages.success(request, f"Slot booked! Admin will assign trainer & vehicle soon. You have {student_package.remaining_sessions} sessions remaining.")
            return redirect('students:dashboard')
    else:
        form = SlotBookingForm(student=student)

    return render(request, 'students/book_slot.html', {
        'form': form,
        'remaining_sessions': student_package.remaining_sessions
    })


def assign_sessions(student_package):
    student = student_package.student
    sessions_to_create = student_package.package.sessions
    trainer = student.trainer  # Use assigned trainer
    vehicle = Vehicle.objects.filter(vehicle_type=student_package.package.vehicle_type, is_active=True).first()
    
    if not trainer or not vehicle:
        print("❌ Trainer or vehicle not available!")
        return  # Or handle this better

    start_date = date.today() + timedelta(days=1)  # start from tomorrow
    time_slots = [slot[0] for slot in TrainingSession.TIME_SLOTS]
    created = 0

    while created < sessions_to_create:
        for time_slot in time_slots:
            if created >= sessions_to_create:
                break
            # Check if trainer already has a session in this slot
            exists = TrainingSession.objects.filter(
                trainer=trainer,
                session_date=start_date,
                time_slot=time_slot
            ).exists()
            if not exists:
                TrainingSession.objects.create(
                    student=student,
                    trainer=trainer,
                    vehicle=vehicle,
                    student_package=student_package,
                    session_date=start_date,
                    time_slot=time_slot
                )
                created += 1
        start_date += timedelta(days=1)