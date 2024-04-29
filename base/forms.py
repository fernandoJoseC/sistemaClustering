from django import forms
from base.models import Document, DocumentPrediccion, WebScrapping


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ("document","prov_ent", "tipo_cont", "nom_ent", "num_clusters",)
        labels = labels={
			'document':'',
            'prov_ent':'Nombre de la provincia',
            'tipo_cont':'Tipo de contratación',
            'nom_ent': 'Nombre de la entidad',
            'num_clusters':'Escoja el número de clusters entre 2 hasta 5',
		}
        widgets = {
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'prov_ent': forms.Select(attrs={'class': 'form-control'}),
            'tipo_cont': forms.Select(attrs={'class': 'form-control'}),
            'nom_ent': forms.Select(attrs={'class': 'form-control'}),
            'num_clusters': forms.Select(attrs={'class': 'form-control'}),
        }
class DocumentPrediccionForm(forms.ModelForm):

    class Meta:
        model = DocumentPrediccion
        fields = ("document", "num_clusters",)
        labels = labels={
			'document':'',
            'num_clusters':'Escoja el número de clusters entre 2 hasta 5',
		}
        widgets = {
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'num_clusters': forms.Select(attrs={'class': 'form-control'}),
        }

class WebScrappingForm(forms.ModelForm):

    class Meta:
        model = WebScrapping
        fields = ("url","year","month")
        labels = labels={"url": "Ingrese una URL","year": "Escoja el año", "month": "Escoja el mes"}