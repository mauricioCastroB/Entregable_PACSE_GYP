import pandas as pd
from datetime import date
from pacse_gyp_forecast.models import *
from django.shortcuts import get_object_or_404
#_________________________________________________________________________________________________________________
def verificar_presencia_columnas(df):
    columnas_requeridas = ['Código', 'Stock disponible']  # Lista de columnas requeridas

    columnas = df.columns
    columnas_lista = columnas.tolist()

    # Verificar si todas las columnas requeridas están presentes en el DataFrame
    columnas_presentes = set(columnas_lista)  
    columnas_faltantes = set(columnas_requeridas) - columnas_presentes

    if columnas_faltantes:
        print(f'Error: Las siguientes columnas requeridas no se encontraron en el archivo: {", ".join(columnas_faltantes)}')
        return False

    return True

# Función para comprobar si el valor es numérico mayor o igual a 0
def es_numero_mayor_igual_cero(valor):
    try:
        num = float(valor)
        return num >= 0
    except ValueError:
        return False

def verificar_formato_columnas(df):
     
    # Verificar formato en la columna "Código"
    validez_columna_codigo= all(df['Código'].str.isalnum())  # Verificar si todos los códigos son alfanuméricos
    print("validez_columna_codigo: ", validez_columna_codigo)
    
    # Verificar formato que la columna 'Stock disponible' tenga solo valores numéricos mayores o iguales a 0
    #validez_columna_stock = df['Stock disponible'].apply(es_numero_mayor_igual_cero).all()

    if not validez_columna_codigo:
        print('Error: El formato de los códigos no es válido.')

    #if not validez_columna_stock:
    #    print('Error: El formato del stock no es válido.')

    return validez_columna_codigo#, validez_columna_stock# and stock_valido


def verificar_valores_faltantes(df):
    
    # Verificar valores faltantes en columnas importantes
    columnas_importantes = ['Código', 'Stock disponible']  # Columnas que consideramos importantes
    valores_faltantes = df[columnas_importantes].isnull().any()  # Verificar si hay algún valor faltante en las columnas importantes

    if valores_faltantes.any():
        columnas_con_faltantes = valores_faltantes[valores_faltantes].index.tolist()
        print(f'Error: Los siguientes campos tienen valores faltantes: {", ".join(columnas_con_faltantes)}')
        return False

    return True

def verificar_valores_unicos(df):
    
    # Verificar valores únicos en la columna "Código"
    codigo_duplicado = df['Código'].duplicated().any()  # Verificar si hay algún código duplicado

    if codigo_duplicado:
        print('Error: La columna "Código" contiene valores duplicados.')
        return False

    return True

def verificacion_excel(df):
    Verificaciones = [False,False,False,False]
    if not verificar_presencia_columnas(df):
        return Verificaciones
    df = df[['Código', 'Stock disponible']]
    Verificaciones[0] = True

    #formato_col_codigo, formato_col_stock = verificar_formato_columnas(df)

    #if formato_col_codigo and formato_col_stock:
    if verificar_formato_columnas(df):
        Verificaciones[1] = True
    if verificar_valores_faltantes(df):
        Verificaciones[2] = True
    if verificar_valores_unicos(df):
        Verificaciones[3] = True
    return Verificaciones

#   Entrada: Recibe como entrada la dirección del archivo excel dentro de la aplicación
#   Salida:   Devuelve la cantidad de encabezados de las columnas que contienen la información a utilizar
#   Objetivo:   Encontrar dentro del archivo excel la fila que tiene los nombres de las columnas con la información
def encontrar_fila_cabeceras(archivo_excel):
    # Leer el archivo Excel sin encabezados
    df = pd.read_excel(archivo_excel, header=None, engine='openpyxl')

    # Encontrar la primera fila que contiene información en todas las columnas
    header_row = df.notna().all(axis=1).idxmax()
    print(header_row)
    return header_row


#   Entrada: Recibe como entrada la dirección del archivo excel dentro de la aplicación
#   Salida:   Devuelve un dataframe con la información a utilizar y además el resultado de las verificaciones en una lista de boolean
#   Objetivo: Quitar del excel las filas innecesarias y solo guardar la información importante, es decir, las columnas Código y Stock disponible
def filtrar_excel_stock(archivo_excel):

    # Encontrar la fila que contiene los encabezados de las columnas
    header_row = encontrar_fila_cabeceras(archivo_excel)

    # Leer el archivo Excel omitiendo las filas iniciales y utilizando la fila de encabezados
    df = pd.read_excel(archivo_excel, sheet_name="Stock actual", skiprows=header_row, engine='openpyxl')

    resultados_verificaciones = verificacion_excel(df)
    todos_verdaderos = all(resultados_verificaciones)

    if  todos_verdaderos:
        # Seleccionar solo las columnas "Código" y "Stock disponible"
        df = df[['Código', 'Stock disponible']]
        # Realizar cualquier otra acción que necesites con los datos del archivo Excel
        return df, resultados_verificaciones
    else:
        return df, resultados_verificaciones

