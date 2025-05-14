from django import forms
from .models import FlatListing, GroupFormationPost, ListingImage


class FlatListingForm(forms.ModelForm):
    class Meta:
        model = FlatListing
        fields = ['description', 'size', 'contact_number', 'address', 'rent_amount', 'has_elevator']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'size': forms.NumberInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_elevator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'has_elevator': 'Has Elevator?'
        }


class GroupFormationForm(forms.ModelForm):
    class Meta:
        model = GroupFormationPost
        fields = ['description', 'size', 'contact_number']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'size': forms.NumberInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ListingImageForm(forms.ModelForm):
    class Meta:
        model = ListingImage
        fields = ['image']


class FlatListingFilterForm(forms.Form):
    min_rent = forms.DecimalField(
        label="Min Rent (BDT)",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Min Rent'})
    )
    max_rent = forms.DecimalField(
        label="Max Rent (BDT)",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Max Rent'})
    )
    has_elevator = forms.ChoiceField(
        label="Elevator",
        choices=[('', 'Any'), ('yes', 'Yes'), ('no', 'No')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select mb-2'})
    )

    def clean(self):
        cleaned_data = super().clean()
        min_rent = cleaned_data.get('min_rent')
        max_rent = cleaned_data.get('max_rent')

        if min_rent is not None and max_rent is not None and min_rent > max_rent:
            self.add_error('min_rent', "Minimum rent cannot be greater than maximum rent.")
            self.add_error('max_rent', "Maximum rent cannot be less than minimum rent.")
        return cleaned_data
    
