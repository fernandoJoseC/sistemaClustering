from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from base.forms import DocumentForm
import pandas as pd
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import streamlit as st
from django.http import JsonResponse
from django.utils.safestring import mark_safe

# Create your views here.
'''def home(request):
    form = DocumentForm(request.POST, request.FILES)
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            context = {'form':form}
            return render(request, "home.html", context)
    context = {'form': DocumentForm()}
    return render(request, "home.html", context)'''


@login_required
def home(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Agrega un mensaje de éxito
            messages.success(request, 'Archivo cargado y procesado con éxito.')

            # Guarda el archivo subido en un lugar del sistema de archivos
            uploaded_file = request.FILES['document']  # Asegúrate de que 'document' es el nombre correcto en tu formulario
            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(name)

            # Aquí lees el contenido del archivo CSV
            file_path = fs.path(name)
            datos = pd.read_csv(file_path)
            #print(datos)

            #Obtenemos los valores de la consulta
            tipo_cont = request.POST.get('tipo_cont')
            nom_ent = request.POST.get('nom_ent')
            prov_ent = request.POST.get('prov_ent')

            # Filtrando los datos para la Provincia de Loja
            data_filtrada_provincias = datos[datos['provEnt'] == prov_ent]
            data_filtrada_tipo_cont = data_filtrada_provincias[data_filtrada_provincias['tipoCont'] == tipo_cont]
            data_filtrada_nom_ent = data_filtrada_tipo_cont[data_filtrada_tipo_cont['nomEnt']== nom_ent]
            
        
            # Convertir el DataFrame a JSON
            # Crear una lista con los nombres únicos de la columna 'tipoCont', 'nom_ent', 'prov_ent', 'cluster'
            tipos_contrato_unicos = datos['tipoCont'].unique().tolist()
            nombres_entidad_unicos = datos['nomEnt'].unique().tolist()
            provincias_unicas = datos['provEnt'].unique().tolist()
            clusters_unicos = datos['cluster'].unique().tolist()


            # Calcular el total del presupuesto y valor adjudicado por cada tipo 
            total_presupuesto_por_tipo = datos.groupby('tipoCont')['presupuesto'].sum().reset_index()
            total_valAdj_por_tipo = datos.groupby('tipoCont')['valAdj'].sum().reset_index()
            total_diferencia_por_tipo = datos.groupby('tipoCont')['diferencia'].sum().reset_index()

            total_presupuesto_por_provincia = datos.groupby('provEnt')['presupuesto'].sum().reset_index()
            total_valAdj_por_provincia = datos.groupby('provEnt')['valAdj'].sum().reset_index()
            total_diferencia_por_provincia = datos.groupby('provEnt')['diferencia'].sum().reset_index()

            #total_presupuesto_por_cluster = datos.groupby('cluster')['presupuesto'].sum().reset_index()
            total_presupuesto_por_cluster = datos.groupby('cluster')['presupuesto'].sum().reset_index()
            total_valAdj_por_cluster = datos.groupby('cluster')['valAdj'].sum().reset_index()
            total_diferencia_por_cluster = datos.groupby('cluster')['diferencia'].mean().reset_index()

            total_promedio_diferencia_tipo_cero = datos.groupby('tipoCont')['diferencia'].mean().reset_index()

            


            # Convertir los resultados en listas para facilitar su uso posterior
            clusters = total_presupuesto_por_cluster['cluster'].tolist()
            totales_presupuesto_cluster = total_presupuesto_por_cluster['presupuesto'].tolist()
            totales_valAdj_cluster = total_valAdj_por_cluster['valAdj'].tolist()
            totales_diferencia_cluster = total_diferencia_por_cluster['diferencia'].tolist()

            # Calculate the average difference for each type of contract
            total_promedio_diferencia_tipo_cero = datos[datos['cluster']==0].groupby('tipoCont')['diferencia'].mean().reset_index()
            total_promedio_diferencia_tipo_uno = datos[datos['cluster']==1].groupby('tipoCont')['diferencia'].mean().reset_index()
            total_promedio_diferencia_tipo_dos = datos[datos['cluster']==2].groupby('tipoCont')['diferencia'].mean().reset_index()
            total_promedio_diferencia_provincia_cero = datos[datos['cluster']==0].groupby('provEnt')['diferencia'].mean().reset_index()
            total_promedio_diferencia_provincia_uno = datos[datos['cluster']==1].groupby('provEnt')['diferencia'].mean().reset_index()
            total_promedio_diferencia_provincia_dos = datos[datos['cluster']==2].groupby('provEnt')['diferencia'].mean().reset_index()
           

            #Filtro por el tipo de contratacion el promedio de la diferencia
            #total_promedio_diferencia_tipo = total_promedio_diferencia_tipo[total_promedio_diferencia_tipo['cluster'] == "0"]
            tipos_contrato_cero = total_promedio_diferencia_tipo_cero['tipoCont'].tolist()
            totales_promedio_diferencia_tipo_cero = total_promedio_diferencia_tipo_cero['diferencia'].tolist()

            tipos_contrato_uno = total_promedio_diferencia_tipo_uno['tipoCont'].tolist()
            totales_promedio_diferencia_tipo_uno = total_promedio_diferencia_tipo_uno['diferencia'].tolist()

            tipos_contrato_dos = total_promedio_diferencia_tipo_dos['tipoCont'].tolist()
            totales_promedio_diferencia_tipo_dos = total_promedio_diferencia_tipo_dos['diferencia'].tolist()

            provincias_cero = total_promedio_diferencia_provincia_cero['provEnt'].tolist()
            totales_promedio_diferencia_provincia_cero = total_promedio_diferencia_provincia_cero['diferencia'].tolist()

            provincias_uno = total_promedio_diferencia_provincia_uno['provEnt'].tolist()
            totales_promedio_diferencia_provincia_uno = total_promedio_diferencia_provincia_uno['diferencia'].tolist()

            provincias_dos = total_promedio_diferencia_provincia_dos['provEnt'].tolist()
            totales_promedio_diferencia_provincia_dos = total_promedio_diferencia_provincia_dos['diferencia'].tolist()


            # Agrupando por 'tipoCont' para obtener nombres únicos y sumar los presupuestos
            #grouped_data = data_filtrada.groupby('tipoCont')['presupuesto'].sum().reset_index()
            #grouped_data = data_filtrada_nom_ent.groupby('nomEnt')['presupuesto'].sum().reset_index()

            # Creando listas para los nombres únicos de 'tipoCont' y para el total del presupuesto por tipo
            tipo_cont_list = data_filtrada_nom_ent['tipoCont'].tolist()
            clusters_list = data_filtrada_nom_ent['cluster'].tolist()
            presupuesto_total_list = data_filtrada_nom_ent['presupuesto'].tolist()


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
            df_json = df.to_json(orient='records')
            df2_json = df2.to_json(orient='records')
            df3_json = df3.to_json(orient='records')
            df4_json = df4.to_json(orient='records')
            df5_json = df5.to_json(orient='records')
            df6_json = df6.to_json(orient='records')
            df7_json = df7.to_json(orient='records')
            df8_json = df8.to_json(orient='records')
            df9_json = df9.to_json(orient='records')
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
                }
            return render(request, "home.html", context)
            

        else:
            messages.error(request, 'Error en el formulario.')
            context = {'form': form}
            return render(request, "home.html", context)
    
        #form = DocumentForm()
        #context = {'form': form}
        #return render(request, "home.html", context)
    context = {'form': DocumentForm()}
    return render(request, "home.html", context)
    

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

