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
    
    
    
from django.contrib.auth import get_user_model
from .models import Trainer

User = get_user_model()


class TrainerUserForm(forms.Form):
    # User fields
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )
    
    username = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'})
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
    
    # Trainer fields
    specialization = forms.ChoiceField(
        choices=Trainer.SPECIALIZATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    experience = forms.IntegerField(
        min_value=0, 
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of experience'})
    )
    
    availability = forms.ChoiceField(
        choices=Trainer.AVAILABILITY_CHOICES,
        initial='FLEXIBLE',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_remote = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    license_number = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter license number'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match")
            
        # Check if username already exists
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "This username is already taken")
            
        # Check if email already exists
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "This email is already registered")
            
        return cleaned_data