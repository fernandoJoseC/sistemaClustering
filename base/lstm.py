import pandas as pd
from math import sqrt
from numpy import concatenate
import matplotlib
from matplotlib import pyplot
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.metrics import mean_squared_error
from pandas import DataFrame, concat
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class Lstm():
  
  def tratato_datos(self, datos):

    df = datos.copy()

    datos.drop(['rucProv', 'rucEnt', 'codCPC', 'codProceso'], axis=1, inplace=True)
    datos = datos.drop(['desCompra', 'fechaAdj', 'fechaPub', 'descCPC', 'nomEnt', 'nomProv'], axis=1)
    datos = datos.drop(['presupuesto'], axis=1)
    datos = datos.drop(['valAdj'], axis=1)
    datos = datos.drop(['Latitud', 'Longitud'], axis=1)
    
    encoder = LabelEncoder()

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

    n_in = 30
    n_out = 1

    values = datos.values
    values = values.astype('float32')

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)

    reframed = self.series_to_supervised(scaled, n_in, n_out)


    reframed.drop(reframed.columns[[-2, -3,-4,-5,-6]], axis=1, inplace=True)


    # Supongamos que reframed es tu DataFrame preparado
    values = reframed.values

    # Elegir usar todos los datos para el test
    test_X, test_y = values[:, :-1], values[:, -1]

    # Redimensionar entrada para ser 3D [muestras, pasos de tiempo, características]
    # Asumiendo que 'n_in' está definido correctamente según la estructura de tus datos
    test_X = test_X.reshape((test_X.shape[0], n_in, test_X.shape[1] // n_in))



    modelo_cargado = tf.keras.models.load_model('/content/drive/MyDrive/PRACTICAS_TESIS/DATOS/modelo_CLUSTER_LSTM_DATOS20212223v2.h5')

    test_X.shape



    test_y.shape

    # Generar predicciones
    predictions = modelo_cargado.predict(test_X)

    scaled_df = pd.DataFrame(scaled)

    predictions_df = pd.DataFrame(predictions)

    desnormalice_df = pd.concat([scaled_df, predictions_df], axis=1)


    desnormalice_df = desnormalice_df.drop([5], axis=1)


    values = desnormalice_df.values
    values = values.astype('float32')
    desnormaliced = scaler.inverse_transform(values)
    desnormaliced_df = pd.DataFrame(desnormaliced)


    valAdj_grupo_unique = df[['valAdj_grupo']].drop_duplicates().sort_values('valAdj_grupo')

    values = valAdj_grupo_unique['valAdj_grupo']
    valAdj_grupo_unique['valAdj_grupo_encoder'] = encoder. fit_transform(values) #variable categorica a numerical
    valAdj_grupo_unique['valAdj_grupo_encoder']

    map_valAdj_grupo_unique = valAdj_grupo_unique.set_index('valAdj_grupo_encoder')['valAdj_grupo'].to_dict()

    datos['grupo_mapeo'] = datos['valAdj_grupo_encoder'].map(map_valAdj_grupo_unique)
    print(datos['grupo_mapeo'])

    mse = mean_squared_error(test_y, predictions)
    rmse = mean_squared_error(test_y, predictions, squared=False)
    mae = mean_absolute_error(test_y, predictions)
    r2 = r2_score(test_y, predictions)

    print(f"MSE: {mse}")
    print(f"RMSE: {rmse}")
    print(f"MAE: {mae}")
    print(f"R^2: {r2}")



  def load_data(self, file_path):
    #datos = pd.read_csv('/content/drive/MyDrive/PRACTICAS_TESIS/DATOS/datos_clustering_2024_FINAL_3CLUSTERS.csv')
    self.datos = pd.read_csv(file_path)
    return self.datos
  
  def series_to_supervised(self, data, n_in=1, n_out=1, dropnan=True):
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









"""# Nueva sección"""






'''# Gráfica de predicciones vs valores reales
plt.figure(figsize=(10, 6))
plt.plot(test_y, label='Valores reales')
plt.plot(predictions, label='Predicciones', alpha=0.7)
plt.title('Comparación de las Predicciones del Modelo con los Valores Reales')
plt.xlabel('Proceso de compra / Indice')
plt.ylabel('Valor')
plt.legend()

plt.show()'''





# Gráfico de Dispersión de Predicciones vs. Valores Reales

'''plt.figure(figsize=(10, 6))
plt.scatter(test_y, predictions, alpha=0.5)
plt.title('Comparación de Predicciones vs. Valores Reales')
plt.xlabel('Valores Reales')
plt.ylabel('Predicciones')
plt.plot([test_y.min(), test_y.max()], [test_y.min(), test_y.max()], 'k--', lw=4) # Línea de identidad
plt.show()'''

