from django import forms
from students.models import TrainingSession, Student
from vehicles.models import Vehicle
from .models import Trainer  # Direct import

class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['user', 'specialization', 'experience', 'availability', 'is_remote']

class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['specialization', 'experience', 'availability', 'is_remote']

class StudentAssignmentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['trainer'].queryset = Trainer.objects.filter(is_active=True)
    #     self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
    #     self.fields['trainer'].required = True
    #     self.fields['vehicle'].required = True

class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ['trainer', 'vehicle', 'session_date', 'time_slot', 'notes']

class AssignTrainerVehicleForm(forms.Form):
    trainer = forms.ModelChoiceField(queryset=Trainer.objects.filter(is_active=True), label="Select Trainer")
    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.filter(is_active=True), label="Select Vehicle")