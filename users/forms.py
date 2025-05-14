from django import forms
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        help_text="Enter a strong password"
        )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        label="Confirm Password",
        help_text="Re-enter your password for confirmation"
        )

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.name@g.bracu.ac.bd'}),
            'user_type': forms.Select(attrs={'class': 'form-select'})
            }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        user_type = cleaned_data.get('user_type')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if user_type and email:
            if user_type == 'STUDENT' and not email.endswith('@g.bracu.ac.bd'):
                self.add_error('email', "BracU students must use their GSuite (@g.bracu.ac.bd) email")
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
