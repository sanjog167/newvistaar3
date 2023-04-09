from django import forms
from .models import ReviewRating

#Customer Review Form    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['uname','email', 'review','rating']
