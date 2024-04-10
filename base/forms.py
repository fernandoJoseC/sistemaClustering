from django import forms
from base.models import Document


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ("document","prov_ent", "tipo_cont", "num_clusters",)
        labels = labels={
			'document':'',
            'prov_ent':'Nombre de la provincia',
            'tipo_cont':'Tipo de contratación',
            'num_clusters':'Escoja el número de clusters',
		}