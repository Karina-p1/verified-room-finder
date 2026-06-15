# apps/listings/forms.py

from django import forms
from .models import Listing, Facilities, ListingImage, ListingReport

PROVINCES = [
    ('', 'Select Province'),
    ('Koshi', 'Koshi Province'),
    ('Madhesh', 'Madhesh Province'),
    ('Bagmati', 'Bagmati Province'),
    ('Gandaki', 'Gandaki Province'),
    ('Lumbini', 'Lumbini Province'),
    ('Karnali', 'Karnali Province'),
    ('Sudurpashchim', 'Sudurpashchim Province'),
]

DISTRICTS_ALL = [
    # Koshi
    'Taplejung', 'Sankhuwasabha', 'Solukhumbu', 'Okhaldhunga',
    'Khotang', 'Bhojpur', 'Dhankuta', 'Terhathum', 'Panchthar',
    'Ilam', 'Jhapa', 'Morang', 'Sunsari', 'Udayapur',
    # Madhesh
    'Saptari', 'Siraha', 'Dhanusha', 'Mahottari',
    'Sarlahi', 'Rautahat', 'Bara', 'Parsa',
    # Bagmati
    'Kathmandu', 'Lalitpur', 'Bhaktapur', 'Kavrepalanchok',
    'Sindhupalchok', 'Rasuwa', 'Nuwakot', 'Dhading',
    'Makwanpur', 'Chitwan', 'Sindhuli', 'Ramechhap', 'Dolakha',
    # Gandaki
    'Kaski', 'Syangja', 'Parbat', 'Baglung', 'Myagdi',
    'Mustang', 'Manang', 'Lamjung', 'Tanahu', 'Gorkha',
    'Nawalpur', 'Palpa',
    # Lumbini
    'Rupandehi', 'Kapilvastu', 'Nawalparasi', 'Arghakhanchi',
    'Gulmi', 'Dang', 'Pyuthan', 'Rolpa',
    'Eastern Rukum', 'Banke', 'Bardiya',
    # Karnali
    'Surkhet', 'Dailekh', 'Jajarkot', 'Western Rukum',
    'Salyan', 'Dolpa', 'Humla', 'Jumla', 'Kalikot', 'Mugu',
    # Sudurpashchim
    'Kailali', 'Kanchanpur', 'Dadeldhura', 'Baitadi',
    'Darchula', 'Bajhang', 'Bajura', 'Achham', 'Doti',
]

DISTRICT_CHOICES = [('', 'Select district')] + [(d, d) for d in sorted(set(DISTRICTS_ALL))]


class ListingForm(forms.ModelForm):
    province = forms.ChoiceField(
        choices=PROVINCES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'provinceSelect'})
    )
    # district is a ChoiceField so it validates the submitted value properly
    district = forms.ChoiceField(
        choices=DISTRICT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'districtSelect'})
    )

    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'property_type', 'furnished_status',
            'province', 'district', 'city', 'area', 'ward_number',
            'latitude', 'longitude',
            'monthly_rent', 'security_deposit',
            'bills_water', 'bills_electricity', 'bills_internet',
            'available_date', 'house_rules',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Cozy 1BHK near Thamel'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5, 'minlength': '100'
            }),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'furnished_status': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'City or VDC'
            }),
            'area': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Area / Tole'
            }),
            'ward_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ward no.'
            }),
            'monthly_rent': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 8000'
            }),
            'security_deposit': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 16000'
            }),
            'available_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'house_rules': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'e.g. No smoking, no pets...'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def clean_province(self):
        province = self.cleaned_data.get('province', '')
        if not province:
            raise forms.ValidationError('Please select a province.')
        return province

    def clean_district(self):
        district = self.cleaned_data.get('district', '')
        if not district:
            raise forms.ValidationError('Please select a district.')
        return district

    def clean_description(self):
        desc = self.cleaned_data.get('description', '')
        if len(desc) < 100:
            raise forms.ValidationError('Description must be at least 100 characters.')
        return desc

def clean_latitude(self):
    lat = self.cleaned_data.get('latitude')
    if lat is not None:
        return round(lat, 6)
    return lat

def clean_longitude(self):
    lng = self.cleaned_data.get('longitude')
    if lng is not None:
        return round(lng, 6)
    return lng
class FacilitiesForm(forms.ModelForm):
    class Meta:
        model = Facilities
        exclude = ['listing']
        widgets = {
            field: forms.CheckboxInput()
            for field in [
                'car_parking', 'bike_parking', 'wifi', 'drinking_water',
                'water_24_7', 'attached_bathroom', 'balcony', 'furnished',
                'cctv', 'security_guard', 'pet_allowed', 'laundry', 'kitchen',
            ]
        }

class ListingReportForm(forms.ModelForm):
    class Meta:
        model = ListingReport
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InquiryMessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Write your message...',
        }),
        max_length=1000,
    )