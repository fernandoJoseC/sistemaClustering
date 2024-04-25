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
from .cluster import Clustering
from sklearn.preprocessing import LabelEncoder

@login_required
def home(request):
    model_cluster = Clustering()
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            #Obtenemos los valores de la consulta
            tipo_cont = request.POST.get('tipo_cont')
            nom_ent = request.POST.get('nom_ent')
            prov_ent = request.POST.get('prov_ent')
            num_clusters = int(request.POST.get('num_clusters'))
            

            # Agrega un mensaje de éxito
            messages.success(request, 'Archivo cargado y procesado con éxito.')
            # Guarda el archivo subido en un lugar del sistema de archivos
            uploaded_file = request.FILES['document']  # Asegúrate de que 'document' es el nombre correcto en tu formulario
            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(name)

            # Aquí lees el contenido del archivo CSV
            file_path = fs.path(name)
            datos0 = model_cluster.load_data(file_path)

            #AGREGAMOS LO DEL COLAB
            #########################################
            datos1 = pd.DataFrame(datos0)

            datos2 = datos1.copy()

            """Observamos que existen en la variable Ruc Proveedor valores NaN, los reemplazaremos por 0"""

            datos2.fillna(0, inplace=True)


            datos2 = datos2.drop(['codProceso'], axis=1)
            datos2 = datos2.drop(['desCompra'], axis=1)


            datos2 = datos2.drop(['fechaPub'], axis=1)

            datos2 = datos2.drop(['rucEnt', 'rucProv'], axis=1)

            encoder = LabelEncoder()

            values = datos2['descCPC'].astype(str)
            datos2['descCPC_encoder'] = encoder.fit_transform(values)

            values = datos2['tipoCont'].astype(str)
            datos2['tipoCont_encoder'] = encoder.fit_transform(values)

            values = datos2['nomEnt'].astype(str)
            datos2['nomEnt_encoder'] = encoder.fit_transform(values)

            values = datos2['provEnt'].astype(str)
            datos2['provEnt_encoder'] = encoder.fit_transform(values)

            values = datos2['cantEnt'].astype(str)
            datos2['cantEnt_encoder'] = encoder.fit_transform(values)

            datos2 = datos2.drop(['nomProv'], axis=1)

            datos2 = datos2.drop(['codCPC'], axis=1)

            #Dataset para clustering
            datos_clustering = datos2.copy()

            datos_clustering = datos_clustering.drop(['fechaAdj', 'descCPC', 'tipoCont', 'nomEnt', 'provEnt', 'cantEnt'], axis=1)

            # Definir los rangos y etiquetas para clasificar 'valor_adjudicado'
            rangos = range(0, 50000001, 100)  # Ajusta los rangos según tus necesidades
            etiquetas = ["{0} - {1}".format(i, i + 99) for i in range(0, 50000000, 100)]

            # Clasificar 'valor_adjudicado' por rangos utilizando pd.cut

            datos_clustering["grupo_valAdj"] = pd.cut(datos_clustering['valAdj'], bins=rangos, right=False, labels=etiquetas)

            values = datos_clustering['grupo_valAdj']
            datos_clustering['grupo_valAdj_encoder'] = encoder.fit_transform(values)

            datos_clustering = datos_clustering.drop(['valAdj', 'presupuesto'], axis=1)

            datos_clustering = datos_clustering.drop(['grupo_valAdj'], axis=1)


            
            # Aplicar Mini-Batch K-means
            clusters = model_cluster.cluster_data(datos_clustering, num_clusters)


            datos1['valAdj_grupo'] = pd.cut(datos1['valAdj'], bins=rangos, right=False, labels=etiquetas)

            datos_csv_clustering = pd.concat([datos1, pd.DataFrame({'cluster': clusters})], axis=1)

            datos_csv_clustering['Latitud'] = datos_csv_clustering['provEnt'].map(lambda x: provincias[x]['latitud'])
            datos_csv_clustering['Longitud'] = datos_csv_clustering['provEnt'].map(lambda x: provincias[x]['longitud'])
            datos_csv_clustering['diferencia'] = datos_csv_clustering['presupuesto']-datos_csv_clustering['valAdj']

            datos = datos_csv_clustering.copy()

            #########################################


            # Filtrando los datos para la Provincia de Loja
            data_filtrada_provincias = pd.DataFrame(datos[datos['provEnt'] == prov_ent])
            data_filtrada_tipo_cont = pd.DataFrame(datos[datos['tipoCont'] == tipo_cont])
            #data_filtrada_nom_ent = pd.DataFrame(datos[datos['nomEnt']== nom_ent])
            
        
            # Convertir el DataFrame a JSON

            if prov_ent == "TODOS":
                data_filtrada = datos
            else:
                data_filtrada = data_filtrada_provincias

            # Uso de la función
            totals = model_cluster.calculate_totals_by_cluster(data_filtrada, 'cluster', 'presupuesto', 'valAdj')

            total_presupuesto_por_cluster = totals['presupuesto']
            total_valAdj_por_cluster = totals['valAdj']

            total_diferencia_por_cluster = data_filtrada.groupby('cluster')['diferencia'].mean().reset_index()
            total_promedio_diferencia_tipo_cero = datos.groupby('tipoCont')['diferencia'].mean().reset_index()

            # Convertir los resultados en listas para facilitar su uso posterior
            # Uso de la función, asumiendo que `totals` ya fue definido como en el ejemplo anterior
            
            clusters = model_cluster.data_to_list(total_presupuesto_por_cluster, 'cluster')
            totales_presupuesto_cluster = model_cluster.data_to_list(total_presupuesto_por_cluster, 'presupuesto')
            totales_valAdj_cluster = model_cluster.data_to_list(total_valAdj_por_cluster, 'valAdj')
            totales_diferencia_cluster = model_cluster.data_to_list(total_diferencia_por_cluster, 'diferencia')


            total_promedio_diferencia_tipo_cero = model_cluster.calculate_average_difference_by_contract(data_filtrada, 0)
            total_promedio_diferencia_tipo_uno = model_cluster.calculate_average_difference_by_contract(data_filtrada, 1)
            total_promedio_diferencia_tipo_dos = model_cluster.calculate_average_difference_by_contract(data_filtrada, 2)
            total_promedio_diferencia_tipo_tres = model_cluster.calculate_average_difference_by_contract(data_filtrada, 3)
            total_promedio_diferencia_tipo_cuatro = model_cluster.calculate_average_difference_by_contract(data_filtrada, 4)
            

            # Calculate the average difference for each type of contract

            if tipo_cont == "Todos":
                data_filtrada_tipo = datos
            else:
                data_filtrada_tipo = data_filtrada_tipo_cont
            
            total_promedio_diferencia_provincia_cero = model_cluster.calculate_average_difference_by_province(data_filtrada_tipo, 0)
            total_promedio_diferencia_provincia_uno = model_cluster.calculate_average_difference_by_province(data_filtrada_tipo, 1)
            total_promedio_diferencia_provincia_dos = model_cluster.calculate_average_difference_by_province(data_filtrada_tipo, 2)
            total_promedio_diferencia_provincia_tres = model_cluster.calculate_average_difference_by_province(data_filtrada_tipo, 3)
            total_promedio_diferencia_provincia_cuatro = model_cluster.calculate_average_difference_by_province(data_filtrada_tipo, 4)
           

            #Filtro por el tipo de contratacion el promedio de la diferencia
            tipos_contrato_cero = model_cluster.data_to_list(total_promedio_diferencia_tipo_cero, 'tipoCont')
            totales_promedio_diferencia_tipo_cero = model_cluster.data_to_list(total_promedio_diferencia_tipo_cero, 'diferencia')

            tipos_contrato_uno = model_cluster.data_to_list(total_promedio_diferencia_tipo_uno, 'tipoCont')
            totales_promedio_diferencia_tipo_uno = model_cluster.data_to_list(total_promedio_diferencia_tipo_uno, 'diferencia')

            tipos_contrato_dos = model_cluster.data_to_list(total_promedio_diferencia_tipo_dos, 'tipoCont')
            totales_promedio_diferencia_tipo_dos = model_cluster.data_to_list(total_promedio_diferencia_tipo_dos, 'diferencia')

            tipos_contrato_tres = model_cluster.data_to_list(total_promedio_diferencia_tipo_tres, 'tipoCont')
            totales_promedio_diferencia_tipo_tres = model_cluster.data_to_list(total_promedio_diferencia_tipo_tres, 'diferencia')

            tipos_contrato_cuatro = model_cluster.data_to_list(total_promedio_diferencia_tipo_cuatro, 'tipoCont')
            totales_promedio_diferencia_tipo_cuatro = model_cluster.data_to_list(total_promedio_diferencia_tipo_cuatro, 'diferencia')

            provincias_cero = model_cluster.data_to_list(total_promedio_diferencia_provincia_cero, 'provEnt')
            totales_promedio_diferencia_provincia_cero = model_cluster.data_to_list(total_promedio_diferencia_provincia_cero, 'diferencia')

            provincias_uno = model_cluster.data_to_list(total_promedio_diferencia_provincia_uno, 'provEnt')
            totales_promedio_diferencia_provincia_uno = model_cluster.data_to_list(total_promedio_diferencia_provincia_uno, 'diferencia')

            provincias_dos = model_cluster.data_to_list(total_promedio_diferencia_provincia_dos, 'provEnt')
            totales_promedio_diferencia_provincia_dos = model_cluster.data_to_list(total_promedio_diferencia_provincia_dos, 'diferencia')

            provincias_tres = model_cluster.data_to_list(total_promedio_diferencia_provincia_tres, 'provEnt')
            totales_promedio_diferencia_provincia_tres = model_cluster.data_to_list(total_promedio_diferencia_provincia_tres, 'diferencia')

            provincias_cuatro = model_cluster.data_to_list(total_promedio_diferencia_provincia_cuatro, 'provEnt')
            totales_promedio_diferencia_provincia_cuatro = model_cluster.data_to_list(total_promedio_diferencia_provincia_cuatro, 'diferencia')

            df = pd.DataFrame({
                'cluster': clusters,
                'presupuesto': totales_presupuesto_cluster
                })
            df2 = pd.DataFrame({
                'cluster': clusters,
                'valAdj': totales_valAdj_cluster
                })
            df3 = pd.DataFrame({
                'cluster': clusters,
                'diferencia': totales_diferencia_cluster
                })
            df4 = pd.DataFrame({
                'tipo_contrato_cero': tipos_contrato_cero,
                'promedio_diferencia_cero': totales_promedio_diferencia_tipo_cero
                })
            df5 = pd.DataFrame({
                'tipo_contrato_uno': tipos_contrato_uno,
                'promedio_diferencia_uno': totales_promedio_diferencia_tipo_uno
                })
            df6 = pd.DataFrame({
                'tipo_contrato_dos': tipos_contrato_dos,
                'promedio_diferencia_dos': totales_promedio_diferencia_tipo_dos
                })
            df7 = pd.DataFrame({
                'provincias_cero': provincias_cero,
                'promedio_diferencia_provincia_cero': totales_promedio_diferencia_provincia_cero
                })
            df8 = pd.DataFrame({
                'provincias_uno': provincias_uno,
                'promedio_diferencia_provincia_uno': totales_promedio_diferencia_provincia_uno
                })
            df9 = pd.DataFrame({
                'provincias_dos': provincias_dos,
                'promedio_diferencia_provincia_dos': totales_promedio_diferencia_provincia_dos
                })
            df10 = pd.DataFrame({
                'tipo_contrato_tres': tipos_contrato_tres,
                'promedio_diferencia_tres': totales_promedio_diferencia_tipo_tres
                })
            df11 = pd.DataFrame({
                'tipo_contrato_cuatro': tipos_contrato_cuatro,
                'promedio_diferencia_cuatro': totales_promedio_diferencia_tipo_cuatro
                })
            df12 = pd.DataFrame({
                'provincias_tres': provincias_tres,
                'promedio_diferencia_provincia_tres': totales_promedio_diferencia_provincia_tres
                })
            df13 = pd.DataFrame({
                'provincias_cuatro': provincias_cuatro,
                'promedio_diferencia_provincia_cuatro': totales_promedio_diferencia_provincia_cuatro
                })
            df_json = df.to_json(orient='records')
            df2_json = df2.to_json(orient='records')
            df3_json = df3.to_json(orient='records')
            df4_json = df4.to_json(orient='records')
            df5_json = df5.to_json(orient='records')
            df6_json = df6.to_json(orient='records')
            df7_json = df7.to_json(orient='records')
            df8_json = df8.to_json(orient='records')
            df9_json = df9.to_json(orient='records')
            df10_json = df10.to_json(orient='records')
            df11_json = df11.to_json(orient='records')
            df12_json = df12.to_json(orient='records')
            df13_json = df13.to_json(orient='records')
            context = {
                'form': form, 
                'df_json': mark_safe(df_json), 
                'df2_json': mark_safe(df2_json), 
                'df3_json': mark_safe(df3_json), 
                'df4_json': mark_safe(df4_json), 
                'df5_json': mark_safe(df5_json), 
                'df6_json': mark_safe(df6_json), 
                'df7_json': mark_safe(df7_json), 
                'df8_json': mark_safe(df8_json), 
                'df9_json': mark_safe(df9_json),
                'df10_json': mark_safe(df10_json),
                'df11_json': mark_safe(df11_json),
                'df12_json': mark_safe(df12_json),
                'df13_json': mark_safe(df13_json),
                'prov_ent': prov_ent,
                'tipo_cont': tipo_cont,
                'num_clusters': num_clusters,
                }
            return render(request, "home.html", context)
            

        else:
            messages.error(request, 'Error en el formulario.')
            context = {'form': form}
            return render(request, "home.html", context)
    
    context = {'form': DocumentForm()}
    return render(request, "home.html", context)



def webScrappingView(request):
    if request.method == "POST":
        form = WebScrappingForm(request.POST)
        if form.is_valid():

            url = str(request.POST.get('url'))
            year = str(request.POST.get('year'))
            month = str(request.POST.get('month'))
            
            selenium_handler = TestUnl()
            
            download = str(selenium_handler.test_unl(url, year, month))


            context = {
                "form": form, 
                'url': url,
                'download': download,
                }
            return render(request, "webscrapping.html", context)
        else:
            #messages.error(request, 'Error en el formulario.')
            context = {'form': form}
            return render(request, "webscrapping.html", context)
    
    context = {'form': WebScrappingForm()}
    return render(request, "webscrapping.html", context)

def inicioView(request):
    return render(request, "inicio.html", {})

def introduccionView(request):
    return render(request, "introduccion.html", {})

def prediccionView(request):
    
    if request.method == "POST":
        form = DocumentPrediccionForm(request.POST, request.FILES)
        if form.is_valid():
            #Obtenemos los valores de la consulta
            num_clusters = int(request.POST.get('num_clusters'))
            

            # Agrega un mensaje de éxito
            messages.success(request, 'Archivo cargado y procesado con éxito.')
            # Guarda el archivo subido en un lugar del sistema de archivos
            uploaded_file = request.FILES['document']  # Asegúrate de que 'document' es el nombre correcto en tu formulario
            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(name)

            # Aquí lees el contenido del archivo CSV
            file_path = fs.path(name)
            '''datos0 = (pd.read_csv(file_path).rename(columns={
                            "Código Proceso":"codProceso",
                            "Descripción compra":"desCompra",
                            #"Fecha_Publicación Jerarquía - Fecha Publicación":"fechaPub",
                            "Fecha Publicación":"fechaPub",
                            #"Fecha Adjudicación Jerarquía - Fecha Adjudicación":"fechaAdj",
                            "Fecha Adjudicación":"fechaAdj",
                            "CPC N9":"codCPC",
                            "Descripción CPC N9":"descCPC",
                            "Tipo Contratación":"tipoCont",
                            "Ruc Entidad":"rucEnt",
                            "Nombre Entidad":"nomEnt",
                            "Provincia Entidad":"provEnt",
                            #"Canton Entidad":"cantEnt",
                            "Cantón Entidad":"cantEnt",
                            "Ruc Proveedor":"rucProv",
                            "Nombre Proveedor":"nomProv",
                            "Presupuesto":"presupuesto",
                            "Valor adjudicado":"valAdj"
                        }))'''

            #AGREGAMOS LO DEL COLAB
            #########################################
            df = (pd.read_csv(file_path).rename(columns={
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
            }))
            

            datos = df.copy()

            """Observamos que existen en la variable Ruc Proveedor valores NaN, los reemplazaremos por 0"""

            datos.fillna(0, inplace=True)

            """El porcentaje de datos únicos por cada columna"""


            datos = datos.drop(['codProceso','desCompra'], axis=1)

            datos = datos.drop(['fechaPub', 'fechaAdj'], axis=1)

            datos = datos.drop(['rucEnt', 'rucProv'], axis=1)

            
            encoder = LabelEncoder()

            values = datos['descCPC'].astype(str)
            datos['descCPC_encoder'] = encoder.fit_transform(values)

            values = datos['tipoCont'].astype(str)
            datos['tipoCont_encoder'] = encoder.fit_transform(values)

            values = datos['nomEnt'].astype(str)
            datos['nomEnt_encoder'] = encoder.fit_transform(values)

            values = datos['provEnt'].astype(str)
            datos['provEnt_encoder'] = encoder.fit_transform(values)

            values = datos['cantEnt'].astype(str)
            datos['cantEnt_encoder'] = encoder.fit_transform(values)

            datos = datos.drop(['nomProv'], axis=1)

            datos = datos.drop(['codCPC'], axis=1)


            datos_clustering = datos.copy()

            datos_clustering = datos_clustering.drop(['descCPC', 'tipoCont', 'nomEnt', 'provEnt', 'cantEnt'], axis=1)

            datos_clustering['diferencia'] = datos_clustering['presupuesto'] - datos_clustering['valAdj']

            """CLUSTERING"""

        

            # Definir los rangos y etiquetas para clasificar 'valor_adjudicado'
            rangos = range(0, 50000001, 100)  # Ajusta los rangos según tus necesidades
            etiquetas = ["{0} - {1}".format(i, i + 99) for i in range(0, 50000000, 100)]

            # Clasificar 'valor_adjudicado' por rangos utilizando pd.cut
            datos_clustering["grupo_valAdj"] = pd.cut(datos_clustering['valAdj'], bins=rangos, right=False, labels=etiquetas)

            # Definir los rangos y etiquetas para clasificar 'valor_adjudicado'
            rangos_presupuesto = range(0, 50000001, 100)  # Ajusta los rangos según tus necesidades
            etiquetas_presupuesto = ["{0} - {1}".format(i, i + 99) for i in range(0, 50000000, 100)]

            datos_clustering["grupo_presupuesto"] = pd.cut(datos_clustering['presupuesto'], bins=rangos_presupuesto, right=False, labels=etiquetas_presupuesto)

            rangos_diferencia = range(0, 2000001, 100)  # Ajusta los rangos según tus necesidades
            etiquetas_diferencia = ["{0} - {1}".format(i, i + 99) for i in range(0, 2000000, 100)]

            datos_clustering["grupo_diferencia"] = pd.cut(datos_clustering['diferencia'], bins=rangos_diferencia, right=False, labels=etiquetas_diferencia)

            values = datos_clustering['grupo_valAdj'].astype(str)
            datos_clustering['grupo_valAdj_encoder'] = encoder.fit_transform(values)

            values = datos_clustering['grupo_presupuesto'].astype(str)
            datos_clustering['grupo_presupuesto_encoder'] = encoder.fit_transform(values)

            values = datos_clustering['grupo_diferencia'].astype(str)
            datos_clustering['grupo_diferencia_encoder'] = encoder.fit_transform(values)


            datos_clustering = datos_clustering.drop(['valAdj', 'presupuesto', 'diferencia'], axis=1)

            datos_clustering = datos_clustering.drop(['grupo_valAdj', 'grupo_presupuesto', 'grupo_diferencia'], axis=1)


            # Aplicar Mini-Batch K-means
            kmeans = MiniBatchKMeans(n_clusters=3, batch_size=1000, random_state=42)
            clusters = kmeans.fit_predict(datos_clustering)
            clusters

            df['valAdj_grupo'] = pd.cut(df['valAdj'], bins=rangos, right=False, labels=etiquetas)
            df['presupuesto_grupo'] = pd.cut(df['presupuesto'], bins=rangos_presupuesto, right=False, labels=etiquetas_presupuesto)

            datos_csv_2020_clustering = pd.concat([df, pd.DataFrame({'cluster': clusters})], axis=1)

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

            datos_csv_2020_clustering['Latitud'] = datos_csv_2020_clustering['provEnt'].map(lambda x: provincias[x]['latitud'])
            datos_csv_2020_clustering['Longitud'] = datos_csv_2020_clustering['provEnt'].map(lambda x: provincias[x]['longitud'])

            #datos_csv_2020_clustering.to_csv('datos_clustering_2024_FINAL_3CLUSTERS.csv', index=False)

            #print(datos_csv_2020_clustering) #con estos datos TRabajo la ia


            #datos = pd.read_csv('/content/drive/MyDrive/PRACTICAS_TESIS/DATOS/datos_clustering_2024_FINAL_3CLUSTERS.csv')
            datos = datos_csv_2020_clustering.copy()

            datos.drop(['rucProv', 'rucEnt', 'codCPC', 'codProceso'], axis=1, inplace=True)

            datos = datos.drop(['desCompra', 'fechaAdj', 'fechaPub', 'descCPC', 'nomEnt', 'nomProv'], axis=1)

            datos = datos.drop(['presupuesto'], axis=1)

            datos = datos.drop(['valAdj'], axis=1)


            datos = datos.drop(['Latitud', 'Longitud'], axis=1)

            encoder = LabelEncoder ()

            values = datos['tipoCont']
            datos['tipoCont_encoder'] = encoder. fit_transform(values) #variable categorica a numerical
            datos['tipoCont_encoder']

            values = datos['provEnt']
            datos['provEnt_encoder'] = encoder. fit_transform(values) #variable categorica a numerical
            datos['provEnt_encoder']

            values = datos['cantEnt']
            datos['cantEnt_encoder'] = encoder. fit_transform(values) #variable categorica a numerical
            datos['cantEnt_encoder']


            values = datos['valAdj_grupo']
            datos['valAdj_grupo_encoder'] = encoder. fit_transform(values) #variable categorica a numerical
            datos['valAdj_grupo_encoder']

            values = datos['presupuesto_grupo']
            datos['presupuesto_grupo_encoder'] = encoder. fit_transform(values) #variable categorica a numerical
            datos['presupuesto_grupo_encoder']



            valAdj_uniques = datos[['valAdj_grupo_encoder', 'valAdj_grupo']].drop_duplicates().sort_values(by='valAdj_grupo_encoder' )

            presupuesto_uniques = datos[['presupuesto_grupo_encoder', 'presupuesto_grupo']].drop_duplicates().sort_values(by='presupuesto_grupo_encoder' )


            datos = datos.drop(['tipoCont', 'provEnt', 'cantEnt', 'valAdj_grupo', 'presupuesto_grupo'], axis=1)


            # Obtiene una lista de todas las columnas excepto 'codCPC' y 'valAdj'
            columnas = [c for c in datos.columns if c not in ['valAdj_grupo_encoder']]

            # Añade 'codCPC' y 'valAdj' al final de la lista de columnas
            columnas_reordenadas = columnas + ['valAdj_grupo_encoder']

            # Reordena el DataFrame según la nueva lista de columnas
            datos = datos[columnas_reordenadas]

            #print("estamos aqui" , datos)

            """# Nueva sección"""

            from math import sqrt
            from numpy import concatenate

            import pandas as pd
            from pandas import DataFrame
            from pandas import concat
            from sklearn.preprocessing import MinMaxScaler, LabelEncoder

            def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
                """
                Transforma una serie de tiempo en un DataFrame de aprendizaje supervisado.

                Argumentos:
                    data: secuencia de observaciones como una lista o DataFrame de Pandas.
                    n_in: número de pasos de tiempo de retraso (lag) (X).
                    n_out: número de pasos de tiempo en el futuro para predecir (y).
                    dropnan: booleano que indica si se deben eliminar las filas con valores NaN después de la transformación.

                Retorna:
                    DataFrame de Pandas de la serie transformada en formato de aprendizaje supervisado.
                """
                n_vars = 1 if type(data) is list else data.shape[1]
                df = DataFrame(data)
                cols, names = list(), list()

                # secuencia de entrada (t-n, ... t-1)
                for i in range(n_in, 0, -1):
                    cols.append(df.shift(i))
                    names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]

                # secuencia de pronóstico (t, t+1, ... t+n)
                for i in range(0, n_out):
                    cols.append(df.shift(-i))
                    if i == 0:
                        names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
                    else:
                        names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]

                # juntarlo todo
                agg = concat(cols, axis=1)
                agg.columns = names

                # eliminar filas con valores NaN
                if dropnan:
                    agg.dropna(inplace=True)
                return agg



            n_in = 30
            n_out = 1

            values = datos.values
            values = values.astype('float32')

            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled = scaler.fit_transform(values)
            #scaled_df = pd.DataFrame(scaled)

            reframed = series_to_supervised(scaled, n_in, n_out)
            #reframed = series_to_supervised(values, n_in, n_out)


            reframed.drop(reframed.columns[[-2, -3,-4,-5,-6]], axis=1, inplace=True)
            from pathlib import Path
            import os
            print(Path(__file__).parents[1]/'media/docs')
            print("ESTOY AQUIIII", reframed)

            # Supongamos que reframed es tu DataFrame preparado
            values = reframed.values

            # Elegir usar todos los datos para el test
            test_X, test_y = values[:, :-1], values[:, -1]

            # Redimensionar entrada para ser 3D [muestras, pasos de tiempo, características]
            # Asumiendo que 'n_in' está definido correctamente según la estructura de tus datos
            test_X = test_X.reshape((test_X.shape[0], n_in, test_X.shape[1] // n_in))


            #from keras.models import load_model
            
            #import keras

            #modelo_cargado = tf.keras.models.load_model('media/docs/modelo_CLUSTER_LSTM_DATOS20212223v2.h5')
            #print(modelo_cargado.summary())
            
            #print(Path(__file__).parents[1]/'media/docs/modelo_CLUSTER_LSTM_DATOS20212223v2.h5')
            #modelo_cargado = keras.load_model(Path(__file__).parents[1]/'media/docs/modelo_CLUSTER_LSTM_DATOS20212223v2.h5')
            #print(modelo_cargado)

            # Generar predicciones
            #predictions = modelo_cargado.predict(test_X)
           # print(predictions)


            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

            '''mse = mean_squared_error(test_y, predictions)
            rmse = mean_squared_error(test_y, predictions, squared=False)
            mae = mean_absolute_error(test_y, predictions)
            r2 = r2_score(test_y, predictions)'''

            print(f"MSE: {mse}")
            print(f"RMSE: {rmse}")
            print(f"MAE: {mae}")
            print(f"R^2: {r2}")



            '''scaled_df = pd.DataFrame(scaled)

            scaled_df.describe()

            predictions_df = pd.DataFrame(predictions)
            predictions_df.describe()

            desnormalice_df = pd.concat([scaled_df, predictions_df], axis=1)
            desnormalice_df

            desnormalice_df = desnormalice_df.drop([5], axis=1)
            desnormalice_df

            values = desnormalice_df.values
            values = values.astype('float32')
            desnormaliced = scaler.inverse_transform(values)
            desnormaliced_df = pd.DataFrame(desnormaliced)
            desnormaliced_df

            df = pd.read_csv('/content/drive/MyDrive/PRACTICAS_TESIS/DATOS/datos_clustering_2024_FINAL_3CLUSTERS.csv')
            df

            valAdj_grupo_unique = df[['valAdj_grupo']].drop_duplicates().sort_values('valAdj_grupo')
            valAdj_grupo_unique

            values = valAdj_grupo_unique['valAdj_grupo']
            valAdj_grupo_unique['valAdj_grupo_encoder'] = encoder. fit_transform(values) #variable categorica a numerical
            valAdj_grupo_unique['valAdj_grupo_encoder']

            valAdj_grupo_unique

            map_valAdj_grupo_unique = valAdj_grupo_unique.set_index('valAdj_grupo_encoder')['valAdj_grupo'].to_dict()
            map_valAdj_grupo_unique

            datos['grupo_mapeo'] = datos['valAdj_grupo_encoder'].map(map_valAdj_grupo_unique)
            datos'''
            
            
            context = {
                'form': form, 
                
                }
            return render(request, "prediccion.html", context)
            

        else:
            messages.error(request, 'Error en el formulario.')
            context = {'form': form}
            return render(request, "prediccion.html", context)
    
        #form = DocumentForm()
        #context = {'form': form}
        #return render(request, "home.html", context)
    context = {'form': DocumentPrediccionForm()}
    #return render(request, "home.html", context)
    return render(request, "prediccion.html", context)
    

def authView (request):
    if request.method =="POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect("base:login")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form":form})

def upload_form(request):
 context = {'form':DocumentForm(),}
 return render(request, "home.html", context)
