from django import forms
from base.models import Document


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ("document","tipo_cont", "prov_ent", "nom_ent",)
        labels = labels={
			'document':'',
			'tipo_cont':'Selecciona el tipo de contratación',
			'prov_ent':'Selecciona la provincia',
			'nom_ent':'Selecciona la Entidad contratante'
		}