from django.contrib import admin
from .models import Trainer,TrainerSchedule,TrainerVehicle

# Register your models here.
# admin.site.register(Trainer)
admin.site.register(TrainerSchedule)
admin.site.register(TrainerVehicle)
