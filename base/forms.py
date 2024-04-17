from django import forms
from base.models import Document, DocumentPrediccion


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ("document","prov_ent", "tipo_cont", "num_clusters",)
        labels = labels={
			'document':'',
            'prov_ent':'Nombre de la provincia',
            'tipo_cont':'Tipo de contratación',
            'num_clusters':'Escoja el número de clusters entre 2 hasta 5',
		}
class DocumentPrediccionForm(forms.ModelForm):

    class Meta:
        model = DocumentPrediccion
        fields = ("document", "num_clusters",)
        labels = labels={
			'document':'',
            'num_clusters':'Escoja el número de clusters entre 2 hasta 5',
		}