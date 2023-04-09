from django import forms
from request.models import SubCategoryRequest


class SubCategoryRequestForm(forms.Form):
    class Meta:
        models = SubCategoryRequest
        fields = '__all__'