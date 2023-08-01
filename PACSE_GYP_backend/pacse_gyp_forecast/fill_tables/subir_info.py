import pandas as pd
from datetime import date
import sqlite3
#Esta linea importa la conexión a la base de datos por defecto: from django.db import connection
from django.db import connection
from django.conf import settings
from django.utils.timezone import make_aware, get_default_timezone
from pytz import timezone
import pytz
from django.shortcuts import render
from django.db import transaction

from pacse_gyp_forecast.models import Product, Sales, Category,Stock,Status
import pacse_gyp_forecast.fill_tables.filtro_info_inicial as filtro_info_inicial


# Nuevas
def cortar_dataframe(df):
    print("cortar dataframe")
    with open("pacse_gyp_forecast/log/log.log", 'r') as archivo:
        contenido = archivo.read()

    if len(contenido) > 0:
        lineas = contenido.splitlines()
        ultima_lectura = lineas[-1]
        ultima_lectura = pd.to_datetime(ultima_lectura)
        if ultima_lectura != df['Fecha de compra'].iloc[-1]:
            df_filtrado = df[df['Fecha de compra'] >= ultima_lectura]
            return df_filtrado
        else:
            return df
    else:
        return df

def obtener_ventas_desde_ultima_venta(sales_df: pd.DataFrame) -> pd.DataFrame:
    print("obtener_ventas_desde_ultima_venta")
    settings.TIME_ZONE
    zona_horaria = pytz.timezone('UTC')

    last_sale = Sales.objects.order_by('-date').first()  # Última venta guardada en la base de datos
    if last_sale:
        # Convertir la columna de fechas a objetos datetime
        sales_df['Fecha de compra'] = sales_df['Fecha de compra'].apply(make_aware)
        #sales_df['Fecha de compra'] = sales_df['Fecha de compra'] + pd.Timedelta(hours=3)
        
        # Filtrar las ventas posteriores a la última venta en la base de datos
        sales_since_last_sale = sales_df[(sales_df['Fecha de compra'] > last_sale.date)]
        
        return sales_since_last_sale
    else:
        # Convertir la columna de fechas a objetos datetime
        sales_df['Fecha de compra'] = sales_df['Fecha de compra'].apply(make_aware)
        #sales_df['Fecha de compra'] = sales_df['Fecha de compra'] + pd.Timedelta(hours=3)
        return sales_df

def verificar_orden_fecha(df, columna_fecha,id):
    # Verificar si la columna está ordenada de forma ascendente
    orden_ascendente = df[columna_fecha].is_monotonic_increasing

    # Verificar si la columna está ordenada de forma descendente
    orden_descendente = df[columna_fecha].is_monotonic_decreasing

    # Devolver True si está ordenada de forma ascendente o descendente, False en caso contrario
    if orden_ascendente or orden_descendente:
        print("ordenada ",id)
        return True
    else:
        print("Desornada ",id)
        return False

def sort_cut_dataframe(data):
    data = data.sort_values('Fecha de compra')
    data = obtener_ventas_desde_ultima_venta(data)
    return data


def guardar_log(data):
    fecha= str(data['Fecha de compra'].iloc[-1])
    with open("pacse_gyp_forecast/log/log.log", 'w') as archivo:
        archivo.write(fecha)

# SUBIR INFORMACIÓN INICIAL
# Ingresar categorias
def subir_info_inicial_categoria(df):
    print("subir_info_inicial_categoria")
    # APARTADO PARA SUBIR INFORMACIÓN DE LA TABLA "CATEGORY"
    # Se filtra la información a subir
    categorias = filtro_info_inicial.obtener_info_columna_específica_df(df, 'Clase')

    table_exists = Category._meta.db_table in connection.introspection.table_names()
    
    if not table_exists:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS "pacse_gyp_forecast_category" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" varchar(30) NOT NULL)""")
        cursor.close()
    
    # Consultar si existen elementos en la tabla
    cantidad_category = Category.objects.count()

    if cantidad_category > 0:
        # Insertar los datos en la tabla de la base de datos
        for categoria in categorias:
            if not Category.objects.filter(description=categoria).exists():
                Category.objects.get_or_create(description=categoria)
    else:
        if not Category.objects.filter(description="Sin_categoria").exists():
            nueva_categoria = Category.objects.create(description="Sin_categoria")
        # Insertar los datos en la tabla de la base de datos
        for categoria in categorias:    
            nueva_categoria = Category.objects.create(description=categoria)


def subir_info_inicial_status():
    status_iniciales = ["1. Bien, Aprox. Más de 2 meses", "2. Regular, Aprox. 2 meses", "3. Peligro, Aprox. Menos de 1 mes", "4. Sin estado"]

    table_exists = Status._meta.db_table in connection.introspection.table_names()

    if not table_exists:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS "pacse_gyp_forecast_status" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(50) NOT NULL)""")
        cursor.close()

    cantidad_status = Status.objects.count()

    if cantidad_status > 0:
        for status in status_iniciales:
            if not Status.objects.filter(name=status).exists():
                Status.objects.get_or_create(name=status)
    else:
        for status in status_iniciales:    
            new_status = Status.objects.create(name=status)

def subir_info_inicial_producto(df):
    column_categorias = Category.objects.values_list('description', flat=True)
    categorias = list(column_categorias)
    df_productos = filtro_info_inicial.obtener_info_inicial_productos_df(df,categorias)

    table_exists = Product._meta.db_table in connection.introspection.table_names()
    if not table_exists:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE "pacse_gyp_forecast_product" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "SKU" varchar(30) NOT NULL UNIQUE, "description" varchar(100) NOT NULL, "restock_time" integer NOT NULL, "ignored" bool NOT NULL, "deleted" bool NOT NULL, "known" bool NOT NULL, "standby" bool NOT NULL, "Category_id" bigint NOT NULL REFERENCES "pacse_gyp_forecast_category" ("id") DEFERRABLE INITIALLY DEFERRED, "Status_id" bigint NOT NULL REFERENCES "pacse_gyp_forecast_status" ("id") DEFERRABLE INITIALLY DEFERRED)""")
        cursor.close()

    # Consultar si existen elementos en la tabla
    cantidad_product = Product.objects.count()

    if cantidad_product > 0:
        # Caso donde hay productos en la base de datos
        for index, row in df_productos.iterrows():
            sku = row['SKU Master']
            description = row['Descripcion Master']
            restock_periods = 24
            ignored = False
            deleted = False
            known = True
            standby = True
            category = Category.objects.get(description=row['Clase'])
            status_inicial = 4
            if not Product.objects.filter(SKU=sku).exists():
                #product = Product(SKU=sku, description=description, restock_time = restock_periods, ignored=ignored, deleted = deleted, known = known, standby = standby, Category_id=category_id, Status_id=status_inicial)
                product = Product(SKU=sku, description=description, restock_time = restock_periods, ignored=ignored, deleted = deleted, known = known, standby = standby, Category=category, Status_id=status_inicial)
                product.save()
    else:
        # Caso donde no hay productos en la base de datos
        # Insertar los datos en la tabla de la base de datos
        for index, row in df_productos.iterrows():
            sku = row['SKU Master']
            description = row['Descripcion Master']
            restock_periods = 24
            ignored = False
            deleted = False
            known = True
            stand_by = True
            category = Category.objects.get(description=row['Clase'])
            status_inicial = 4
            new_product = Product.objects.create(SKU=sku, description=description, restock_time = restock_periods, ignored=ignored, deleted = deleted, known = known, standby = stand_by, Category_id=category.id, Status_id=status_inicial)
            

def subir_info_inicial_stock():
    table_exists = Stock._meta.db_table in connection.introspection.table_names()

    if not table_exists:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS "pacse_gyp_forecast_stock" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer NOT NULL, "date" date NOT NULL, "Product_id" bigint NOT NULL REFERENCES "pacse_gyp_forecast_product" ("id") DEFERRABLE INITIALLY DEFERRED)""")
        cursor.close()
        
    # Consultar si existen elementos en la tabla stock
    cantidad_stock = Stock.objects.count()

    if cantidad_stock > 0:
        # Consultar cuantos elementos hay en la tabla Product
        number_products = Product.objects.count()

        for index in range(number_products):
            fecha_actual = date.today()
            if not Stock.objects.filter(Product_id=index+1).exists():
                stock_data = Stock(quantity=0, date=fecha_actual, Product_id=index+1)
                stock_data.save()

    else:
        # Consultar cuantos elementos hay en la tabla Product
        number_products = Product.objects.count()
    
        for index in range(number_products):
            fecha_actual = date.today()
            new_stock = Stock.objects.create(quantity=0, date=fecha_actual, Product_id=index+1)


def subir_info_inicial_ventas(df):

    table_exists = Sales._meta.db_table in connection.introspection.table_names()

    if not table_exists:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE "pacse_gyp_forecast_sales" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" datetime NOT NULL, "units" integer NOT NULL, "Product_id" bigint NOT NULL REFERENCES "pacse_gyp_forecast_product" ("id") DEFERRABLE INITIALLY DEFERRED)""")
        cursor.close()

    cantidad_sales = Sales.objects.count()
    
    if cantidad_sales > 0:
        # Hacer log para filtrar el excel
        settings.TIME_ZONE
        with transaction.atomic():
            # Recorrer el dataframe de ventas
            i = 1
            for index, row in df.iterrows():
                sku = row['SKU Master']
                fecha_compra = row['Fecha de compra']
                unidades = row['Unidades']
                
                # Obtener el producto correspondiente al SKU en la tabla Producto
                product = Product.objects.get(SKU=sku)
                product.standby = True
                product.save()

                # Verificar si ya existe una venta con el mismo producto y fecha
                existing_sale = Sales.objects.filter(Product=product, date=fecha_compra, units = unidades).exists()
                
                if not existing_sale:
                    # Crear y guardar un objeto de Ventas relacionado al producto
                    sale = Sales.objects.create(date=fecha_compra,units=unidades,Product_id=product.id)
                    #print("Venta guardada i=", i)
                    i += 1
                else:
                    print("Venta %i duplicada, no se guarda" % i)
    else:
        #CASO DONDE NO HAY INFORMACIÓN
        settings.TIME_ZONE
        with transaction.atomic():
            # Recorrer el dataframe de ventas
            i = 1
            for index, row in df.iterrows():
                sku = row['SKU Master']
                fecha_compra = row['Fecha de compra']
                unidades = row['Unidades']
                
                # Obtener el producto correspondiente al SKU en la tabla Producto
                product = Product.objects.get(SKU=sku)
                product.standby = True
                product.save()

                # Crear y guardar un objeto de Ventas relacionado al producto
                sale = Sales.objects.create(date=fecha_compra,units=unidades,Product_id=product.id)
                #print("Venta guardada i=", i)
                i+=1

def cargar_datos_inicial_bd(data):
    # Si hay informacion nueva
    if not data.empty:
        print("subir_info_inicial_categoria")
        subir_info_inicial_categoria(data)
        print("subir_info_inicial_status")
        subir_info_inicial_status()
        print("subir_info_inicial_producto")
        subir_info_inicial_producto(data)
        print("subir_info_inicial_stock")
        subir_info_inicial_stock()
        print("subir_info_inicial_ventas")
        subir_info_inicial_ventas(data)
        print("Carga realizada")
    else:
        print("No hay informacion que actualizar")

# SUBIR INFORMACIÓN CON LA BD CARGADA
def subir_info_ventas(data):
    
    i = 1
    for index, row in data.iterrows():
        # Se obtienen los datos a guardar de la venta
        sku_master = row['SKU Master']
        fecha_compra = row['Fecha de compra']
        unidades = row['Unidades']

         # Verificar la existencia del SKU Master de esta venta en la tabla Product
        if not Product.objects.filter(SKU=sku_master).exists():
            print("producto no esta en BD")
            new_product_description = row['Clase']
            if not Category.objects.filter(description= new_product_description).exists():
                
                new_category = Category.objects.create(description = new_product_description)

                new_product = Product.objects.create(
                    SKU = sku_master,
                    description = new_product_description,
                    restock_time = 24,
                    ignored = False,
                    deleted = False,
                    known =  False,
                    standby =  True,
                    #FK attributes.
                    Category_id = new_category.id,
                    Status_id = 4
                )
                
                new_stock = Stock.objects.create(
                    quantity = 0,
                    date = date.today(),
                    #FK attributes.
                    Product_id = new_product.id
                )

                new_sale = Sales.objects.create(
                    date=fecha_compra,
                    units=unidades,
                    Product_id= new_product.id
                )

            else:
                category_asociated = Category.objects.get(description = new_product_description)

                #Para este caso la categoría si existe, entonces no es necesario añadirla a la base de datos
                new_product = Product.objects.create(
                    SKU = sku_master,
                    description = category_asociated.description,
                    restock_time = 24,
                    ignored = False,
                    deleted = False,
                    known =  False,
                    standby =  True,
                    #FK attributes.
                    Category_id = category_asociated.id,
                    Status_id = 4
                )

                new_stock = Stock.objects.create(
                    quantity = 0,
                    date = date.today(),
                    #FK attributes.
                    Product_id = new_product.id
                )

                new_sale = Sales.objects.create(
                    date=fecha_compra,
                    units=unidades,
                    Product_id= new_product.id
                )
            
        else: # Si el producto existe en la base de datos, entonces se guarda la venta de forma normal
            # Obtener el producto correspondiente al SKU en la tabla Producto
            product = Product.objects.get(SKU=sku_master)
            product.standby = True
            product.save()

            # Crear y guardar un objeto de Ventas relacionado al producto
            sale = Sales.objects.create(
                date=fecha_compra,
                units=unidades,
                Product_id=product.id
            )
        #print("Venta guardada i=", i)
        i+=1    

def cargar_datos_bd(data):
    if not data.empty:
        subir_info_ventas(data)
        print("Carga realizada")
    else:
        print("No hay informacion que actualizar 2")
