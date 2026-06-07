# apps/documents/forms.py

from django import forms
from .models import LandlordDocument

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = LandlordDocument
        fields = [
            'citizenship_front',
            'citizenship_back',
            'lalpurja',
            'selfie_image',
        ]
        widgets = {
            'citizenship_front': forms.FileInput(attrs={'accept': 'image/*'}),
            'citizenship_back': forms.FileInput(attrs={'accept': 'image/*'}),
            'lalpurja': forms.FileInput(attrs={'accept': 'image/*'}),
            'selfie_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'citizenship_front': 'Citizenship Card (Front)',
            'citizenship_back': 'Citizenship Card (Back)',
            'lalpurja': 'Lalpurja (Property Ownership Document)',
            'selfie_image': 'Selfie Holding Your Citizenship',
        }

    def clean(self):
        cleaned_data = super().clean()
        # Validate each image is under 5MB
        for field in ['citizenship_front', 'citizenship_back', 'lalpurja', 'selfie_image']:
            image = cleaned_data.get(field)
            if image and image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    f'{self.fields[field].label} must be under 5MB.'
                )
        return cleaned_data