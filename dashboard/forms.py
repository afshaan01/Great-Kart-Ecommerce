from django import forms
class UserProfileCoreForm(forms.Form):
    profile_picture= forms.ImageField(required=False)
    address_line_1=forms.CharField(max_length=100, required=False)
    address_line_2=forms.CharField(max_length=100, required=False)
    city=forms.CharField(max_length=50, required=False)
    state=forms.CharField(max_length=50, required=False)
    country=forms.CharField(max_length=50, required=False)
    pin_code=forms.CharField(max_length=10, required=False)
    phone_number=forms.CharField(max_length=15, required=False)

