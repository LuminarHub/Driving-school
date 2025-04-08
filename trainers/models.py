from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

class Trainer(models.Model):
    # Link to the User model (from accounts app)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driving_trainer_profile'  
    )
    
    # Trainer's specialization (car, scooty, both, etc.)
    SPECIALIZATION_CHOICES = [
        ('CAR', 'Car'),
        ('SCOOTY', 'Scooty'),
        ('BOTH', 'Both Car and Scooty'),
        ('OTHER', 'Other')
    ]
    specialization = models.CharField(
        max_length=10,
        choices=SPECIALIZATION_CHOICES,
        default='BOTH'
    )
    
    # Years of experience
    experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Years of experience as a driving trainer"
    )
    
    # Availability schedule
    AVAILABILITY_CHOICES = [
        ('WEEKDAY', 'Weekdays Only'),
        ('WEEKEND', 'Weekends Only'),
        ('MORNING', 'Morning Shifts Only'),
        ('EVENING', 'Evening Shifts Only'),
        ('FLEXIBLE', 'Flexible Schedule'),
        ('CUSTOM', 'Custom Schedule')
    ]
    availability = models.CharField(
        max_length=10,
        choices=AVAILABILITY_CHOICES,
        default='FLEXIBLE'
    )
    
    # For remote trainers
    is_remote = models.BooleanField(
        default=False,
        help_text="Whether this trainer provides remote training services"
    )
    
    # For remote trainers - service area
    service_area = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Geographic areas where remote training is available"
    )
    
    # Maximum number of students this trainer can handle
    max_students = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of students this trainer can handle at once"
    )
    
    # Date when the trainer joined
    date_joined = models.DateField(
        default=timezone.now,
        help_text="Date when the trainer joined the driving school"
    )
    
    # Trainer's license number
    license_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Trainer's driving license number"
    )
    
    # Additional notes about the trainer
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the trainer"
    )
    
    # Is the trainer currently active?
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this trainer is currently active"
    )
    
    class Meta:
        ordering = ['-experience', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"
    
    def get_assigned_students_count(self):
        """Get the number of students currently assigned to this trainer"""
        return self.student_set.count()
    
    def has_capacity(self):
        """Check if the trainer can take more students"""
        return self.get_assigned_students_count() < self.max_students


class TrainerSchedule(models.Model):
    
    """Model to store trainer's specific schedule slots"""
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,  # Changed from SET_NULL to CASCADE to match your original design
        related_name='schedules'   # Changed from 'student_set' to 'schedules'
    )
    # The day of the week for this schedule
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ]
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    
    # Time slots
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Is this slot available for booking?
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['trainer', 'day_of_week', 'start_time', 'end_time']
    
    def __str__(self):
        day_name = self.get_day_of_week_display()
        return f"{self.trainer} - {day_name} {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')}"


from vehicles.models import Vehicle  # Assuming you have a Vehicle model already

class TrainerVehicle(models.Model):
    """Model to track which vehicle is assigned to which trainer"""
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True,       # ✅ allow null in database
        blank=True,      # ✅ allow blank in forms/admin
        related_name='trainer_assignments'
    )

    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['trainer', 'vehicle']
    
    def __str__(self):
        return f"{self.vehicle} assigned to {self.trainer}"