from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from base.forms import DocumentForm, DocumentPrediccionForm, WebScrappingForm
import pandas as pd
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score
import pandas as pd
import os
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from .selenium import SeleniumHandler
from .scrappingv2 import TestP1
from .busquedadinamica import TestDinamico
from .unl import TestUnl
from sklearn.preprocessing import LabelEncoder

provincias = {
                "AZUAY": {"latitud": -2.898611, "longitud": -78.477778},
                "BOLIVAR": {"latitud": -1.749722, "longitud": -78.166667},
                "CAÑAR": {"latitud": -2.833333, "longitud": -78.666667},
                "CARCHI": {"latitud": 0.783333, "longitud": -78.166667},
                "CHIMBORAZO": {"latitud": -1.700833, "longitud": -78.666667},
                "COTOPAXI": {"latitud": -0.683333, "longitud": -78.416667},
                "EL ORO": {"latitud": -3.450000, "longitud": -79.916667},
                "ESMERALDAS": {"latitud": 0.966667, "longitud": -79.666667},
                "GALAPAGOS": {"latitud": -0.633333, "longitud": -90.333333},
                "GUAYAS": {"latitud": -2.200000, "longitud": -79.883333},
                "IMBABURA": {"latitud": 0.416667, "longitud": -78.416667},
                "LOJA": {"latitud": -4.000000, "longitud": -79.216667},
                "LOS RIOS": {"latitud": -1.500000, "longitud": -79.166667},
                "MANABI": {"latitud": -0.500000, "longitud": -80.000000},
                "MORONA SANTIAGO": {"latitud": -2.833333, "longitud": -77.833333},
                "NAPO": {"latitud": -1.000000, "longitud": -77.833333},
                "ORELLANA": {"latitud": -0.583333, "longitud": -76.833333},
                "PASTAZA": {"latitud": -1.416667, "longitud": -77.833333},
                "PICHINCHA": {"latitud": -0.250000, "longitud": -78.500000},
                "SANTA ELENA": {"latitud": -2.250000, "longitud": -80.833333},
                "SANTO DOMINGO DE LOS TSACHILAS": {"latitud": -0.250000, "longitud": -79.333333},
                "SUCUMBIOS": {"latitud": -0.500000, "longitud": -76.833333},
                "TUNGURAHUA": {"latitud": -1.416667, "longitud": -78.250000},
                "ZAMORA CHINCHIPE": {"latitud": -4.083333, "longitud": -78.916667},
            }

class Clustering():
    
    def load_data(self, file_path):
        self.datos = pd.read_csv(file_path).rename(columns={
                            "Código Proceso":"codProceso",
                            "Descripción compra":"desCompra",
                            "Fecha Publicación":"fechaPub",
                            "Fecha Adjudicación":"fechaAdj",
                            "CPC N9":"codCPC",
                            "Descripción CPC N9":"descCPC",
                            "Tipo Contratación":"tipoCont",
                            "Ruc Entidad":"rucEnt",
                            "Nombre Entidad":"nomEnt",
                            "Provincia Entidad":"provEnt",
                            "Cantón Entidad":"cantEnt",
                            "Ruc Proveedor":"rucProv",
                            "Nombre Proveedor":"nomProv",
                            "Presupuesto":"presupuesto",
                            "Valor adjudicado":"valAdj"
                        })
        return self.datos

    def cluster_data(self, data, n_clusters):
        self.minibatch_kmeans = MiniBatchKMeans(n_clusters=n_clusters, batch_size=1000, random_state=42)
        self.clusters = self.minibatch_kmeans.fit_predict(data)
        return self.clusters

    def calculate_totals_by_cluster(self, data, group_by_column, *sum_columns):
        self.result = {}
        for column in sum_columns:
            self.grouped_data = data.groupby(group_by_column)[column].sum().reset_index()
            self.result[column] = self.grouped_data
        return self.result

    def calculate_average_difference_by_contract(self, data, num, group_by_column='cluster', target_column='tipoCont', value_column='diferencia'):
        
        self.cluster = num
        self.filtered_data = data[data[group_by_column] == self.cluster]
        self.lista = self.filtered_data.groupby(target_column)[value_column].mean().reset_index()
        return self.lista

    def calculate_average_difference_by_province(self, data, num, group_by_column='cluster', target_column='provEnt', value_column='diferencia'):
        
        self.cluster = num
        self.filtered_data = data[data[group_by_column] == self.cluster]
        self.lista = self.filtered_data.groupby(target_column)[value_column].mean().reset_index()
        return self.lista

    def data_to_list(self, data,group_by_column):
        self.lista = data[group_by_column].tolist()
        return self.lista

