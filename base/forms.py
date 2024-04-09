from django import forms
from base.models import Document


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ("document","prov_ent", "tipo_cont")
        labels = labels={
			'document':'',
            'prov_ent':'Nombre de la provincia',
            'tipo_cont':'Tipo de contratación',
		}