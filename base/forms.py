from django import forms
from base.models import Document


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ("document",)
        labels = labels={
			'document':'',
			
		}