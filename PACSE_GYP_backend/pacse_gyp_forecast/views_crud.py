import pandas as pd
from django.shortcuts import render, get_object_or_404,redirect
from .forms import StatusForm, CategoryForm, StockForm, ProductForm, SalesForm, ForecastForm
from .models import Status, Product, Stock, Category, Sales, Forecast
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
import json
from pacse_gyp_forecast.manage_status.manage_status import calculate_status
from django.db import connection, transaction
import datetime
import subprocess
import time

@csrf_exempt
def update_standby(request):
    try:
        if request.method == 'PATCH':
            products_standby = Product.objects.filter(standby = False)
            if products_standby:
                for producto in products_standby:
                    date_sale = Sales.objects.filter(Product_id = producto.id).latest('date').date
                    date_sale = date_sale.date()
                    print(date_sale)
                    today = datetime.datetime.today().date()
                    diferencia = today - date_sale
                    print(diferencia)
                    print(diferencia.days)
                    if diferencia.days > 14:
                        producto.standby = True
                        producto.save()
                response_data = {
                    'message': 'Cambios en el standby realizados realizado correctamente'
                }
                messages.success(request, 'CAMBIO DE STANDBY CORRECTO')
                return JsonResponse(response_data)
            
            response_data = {
                'message': 'No hay productos que actualizar'
            }
            messages.success(request, 'NO HAY PRODUCTOS QUE ACTUALIZAR')
            return JsonResponse(response_data)
    except:
        response_data = {
            'message': 'Ocurrio un error al intentar actualizar el standby'
        }
        messages.success(request, 'CAMBIO DE STANDBY CORRECTO')
        return JsonResponse(response_data)

def salir(request):
    lista = ["run.exe","node.exe","python.exe"]
    for proceso in lista:
        while True:
            comando = "taskkill /F /IM {}".format(proceso)
            try:
                subprocess.run(comando, shell=True, check=True)
            except subprocess.CalledProcessError:
                break
            time.sleep(0.1)

def reset_autoincrement_index(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")

def drop_table(request):
    try:
        with transaction.atomic():

            sales = Sales.objects.all()
            forescast = Forecast.objects.all()
            stock = Stock.objects.all()
            product = Product.objects.all()
            category = Category.objects.all()
            status = Status.objects.all()

            # Eliminar todos los registros de las tablas
            if sales.count() != 0:
                sales.delete()
                # Restablecer los índices AUTOINCREMENT usando consultas SQL directas
                reset_autoincrement_index('pacse_gyp_forecast_sales')

            if forescast.count() != 0:
                forescast.delete()
                # Restablecer los índices AUTOINCREMENT usando consultas SQL directas
                reset_autoincrement_index('pacse_gyp_forecast_forecast')
            
            if stock.count() != 0:
                stock.delete()
                reset_autoincrement_index('pacse_gyp_forecast_stock')

            if product.count() != 0:
                product.delete()
                reset_autoincrement_index('pacse_gyp_forecast_product')

            if category.count() != 0:
                category.delete()
                reset_autoincrement_index('pacse_gyp_forecast_category')

            if status.count() != 0:
                status.delete()
                reset_autoincrement_index('pacse_gyp_forecast_status')
        return HttpResponse("Todas las tablas se han vaciado correctamente.", status=200)

    except:
        return HttpResponse("Fallo el borrado de la base de datos", status=400)

    

# CRUD Product
def get_product_by_id(request, id):
    try:
        product_data = Product.objects.values('id', 'SKU', 'description', 'restock_time', 'ignored').get(id=id)
        product = Product(**product_data)
        product_json = serializers.serialize('json', [product])
        return JsonResponse(json.loads(product_json)[0]['fields'], safe=False)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

@csrf_exempt
def update_product(request, id):
    try:
        product = get_object_or_404(Product, id=id)
        if request.method == 'PATCH':
            stringProduct = request.body.decode('utf8').replace("'", '"')
            dataProduct = json.loads(stringProduct)

            if 'category' in dataProduct:
                categoryProduct = get_object_or_404(Category, description=dataProduct['category'])
                product.Category= categoryProduct

            if 'description' in dataProduct:

                product.description = dataProduct['description']
            if 'SKU' in dataProduct:
                product.SKU = dataProduct['SKU']

            if 'restock_time' in dataProduct:
                product.restock_time = dataProduct['restock_time']

            product.save()

            response_data = {
                'message': 'Producto Modificado'
            }
            messages.success(request, 'MODIFICACION HECHA')
            return JsonResponse(response_data)

    except:
        messages.error(request, "OCURRIO UN ERROR EN LA MODIFICACION")


@csrf_exempt
def update_knownProduct_by_id(request, id):
    try:
        product = get_object_or_404(Product, id=id)
        if request.method == 'PATCH':
            #Convertir el cuerpo del request a un diccionario
            stringProduct = request.body.decode('utf8').replace("'", '"')
            dataProduct = json.loads(stringProduct)
            categoryProduct = get_object_or_404(Category, description = dataProduct['category'])

            #Caso para producto que sea nuevo
            if product.SKU == dataProduct['SKU'] and product.Category_id == categoryProduct.id:
                product.known = True
                product.save()
                response_data = {
                'menssage': 'Producto Modificado'
                }
                messages.success(request, 'MODIFICACION HECHA')
                return JsonResponse(response_data)

            #Caso para producto que sea nuevo pero con error en la categoria
            elif product.SKU == dataProduct['SKU'] and product.Category_id != categoryProduct.id:
                product.Category_id = categoryProduct.id
                product.known = True
                product.save()
                response_data = {
                'menssage': 'Producto Modificado'
                }
                messages.success(request, 'MODIFICACION HECHA')
                return JsonResponse(response_data)
            #Caso donde el producto es erroneo (Reasignar las ventas)

            #Se busca el nuevo id de producto
            elif product.SKU != dataProduct['SKU']:
                product_to_assing = get_object_or_404(Product, SKU = dataProduct['SKU'], deleted = False)    
                #Obtener las ventas a reasignar
                salesProduct = Sales.objects.filter(Product_id = id)
                #Si las hay entonces se asignan al nuevo id
                if salesProduct:
                    for sale in salesProduct:
                        sale.Product_id = product_to_assing.id
                        sale.save()

                #Se elimina el producto erroneo
                product.deleted = True
                product.save()
                response_data = {
                    'menssage': 'Producto Modificado'
                }
                messages.success(request, 'MODIFICACION HECHA')
                return JsonResponse(response_data)
    except:
        messages.error(request, "OCURRIO UN ERROR EN LA MODIFICACION")

@csrf_exempt
def softDelete_knownProduct_by_id(request, id):
    try:
        if request.method == 'PATCH':
            #Eliminar el producto
            #Obtener el producto a borrar
            product = get_object_or_404(Product, id=id)
            print(product)
            product.deleted = True
            product.save()
            response_data = {
                'message': 'Producto Eliminado'
            }
            messages.success(request, 'ELIMINACION HECHA')
            return JsonResponse(response_data)
    except:
        messages.error(request, "OCURRIO UN ERROR AL BORRAR EL PRODUCTO")


@csrf_exempt
def update_product_status_by_id(request, id):
    try:
        product = get_object_or_404(Product, id=id)
        if request.method == 'PUT':
            new_status = calculate_status(product)
            status_db = get_object_or_404(Status, id = new_status)
            product.Status = status_db
            product.save()
            response_data = {
                'message': 'Cambio del estado realizado correctamente',
                'Status': new_status
            }
            messages.success(request, 'CAMBIO DE ESTADO CORRECTO')
            return JsonResponse(response_data)
        else:
            # Si la solicitud no es de tipo POST, devuelve una respuesta de error
            response_data = {
                'message': 'Error: se esperaba una solicitud PUT'
            }
            return JsonResponse(response_data, status=400)
    except:
        messages.error(request, "OCURRIO UN ERROR EN EL CAMBIO DE ESTADO")

@csrf_exempt
def ignore_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'PUT':
        product.ignored = True
        product.save()
        response_data = {
            'message': 'Producto ignorado correctamente',
            'ignored': True
        }
        return JsonResponse(response_data)

    # Si la solicitud no es de tipo POST, devuelve una respuesta de error
    response_data = {
        'message': 'Error: se esperaba una solicitud PUT'
    }
    return JsonResponse(response_data, status=400)

@csrf_exempt
def dis_ignore_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'PUT':
        product.ignored = False
        product.save()
        response_data = {
            'message': 'Producto designorado correctamente',
            'ignored': False
        }
        return JsonResponse(response_data)

    # Si la solicitud no es de tipo POST, devuelve una respuesta de error
    response_data = {
        'message': 'Error: se esperaba una solicitud PUT'
    }
    return JsonResponse(response_data, status=400)


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('product_list')

## Funciones originadas por CRUD pero necesarias.
def get_info_tabla(request):

    query = Product.objects.values('id', 'SKU', 'description','Category__description', 'Status__name', 'restock_time','ignored', 'Status_id','stock__quantity','known', 'deleted','standby')
    query = query.annotate(Category_description=F('Category__description'), Status_name=F('Status__name'))

    data = list(query)

    return JsonResponse(data, safe=False)

# CRUD Stock

def get_last_stock(request):
    try:
        stocks = Stock.objects.all()
        if stocks:
            fecha_mas_actual = Stock.objects.latest('date').date

            fecha_actual = datetime.datetime.now().date()

            # Convertir fecha_mas_actual a datetime.date
            fecha_mas_actual = datetime.date(fecha_mas_actual.year, fecha_mas_actual.month, fecha_mas_actual.day)

            # Calcular la diferencia de tiempo en días
            diferencia_tiempo = fecha_actual - fecha_mas_actual
            # Crear un diccionario con el resultado
            resultado = {
                'last_date': str(fecha_mas_actual),
                'dif_date': str(diferencia_tiempo)
            }

            # Retornar la respuesta JSON
            return JsonResponse(resultado)
        else:
            resultado = {
                'last_date': "Sin fecha",
                'actualizar': True,
            }
            # Retornar la respuesta JSON
            return JsonResponse(resultado)
    except:
        return messages.error(request, "OCURRIO UN ERROR EN EL CAMBIO DE ESTADO")

#CRUD Sales
def get_all_sales(request):
    sales = Sales.objects.all()
    return render(request, 'sales_list.html', {'sales': sales})


def get_sales_by_id(request, id):
    sales = get_object_or_404(Sales, id=id)
    return render(request, 'sales_detail.html', {'sales': sales})

def get_sales_by_sku(sku):
    try:
        product = Product.objects.get(SKU=sku)
        sales = Sales.objects.filter(Product=product)
        return sales
    except Product.DoesNotExist:
        return None

def get_last_sales(request):
    try:
        sales = Sales.objects.all()
        if sales:
            fecha_mas_actual = Sales.objects.latest('date').date

            fecha_actual = datetime.datetime.now().date()

            # Convertir fecha_mas_actual a datetime.date
            fecha_mas_actual = datetime.date(fecha_mas_actual.year, fecha_mas_actual.month, fecha_mas_actual.day)

            # Calcular la diferencia de tiempo en días
            diferencia_tiempo = fecha_actual - fecha_mas_actual

            # Verificar si han pasado dos semanas (14 días)
            han_pasado_dos_semanas = diferencia_tiempo.days >= 14

            # Crear un diccionario con el resultado
            resultado = {
                'last_date': str(fecha_mas_actual),
                'actualizar': han_pasado_dos_semanas
            }

            # Retornar la respuesta JSON
            return JsonResponse(resultado)
        else:
            resultado = {
                'last_date': "Sin fecha",
                'actualizar': True,
            }
            # Retornar la respuesta JSON
            return JsonResponse(resultado)
    except:
        return messages.error(request, "OCURRIO UN ERROR EN EL CAMBIO DE ESTADO")

#CRUD Forecast
def get_forecast_and_sales(request, id):
    product = Product.objects.get(id = id)
    forecasts = list(Forecast.objects.filter(Product_id = product.id).order_by('id'))
    sales_product = list(Sales.objects.filter(Product_id = product.id).order_by('id'))

    sales_units_dates = list()
    forecast_units = list()
    forecast_dates = list()
    
    for sale in sales_product:
        units_dates = list()
        units_dates.append(sale.units)
        units_dates.append(sale.date)
        sales_units_dates.append(units_dates)

    for forecast in forecasts:
        forecast_units.append(forecast.units)
        forecast_dates.append(forecast.date)

    
    df_sales =  pd.DataFrame(sales_units_dates, columns = ['Units', 'Date'])
    df_sales_weekly = df_sales.groupby(pd.Grouper(key='Date',freq='W'))['Units'].sum().reset_index()

    sales_units= df_sales_weekly['Units'].values.tolist()
    sales_dates= df_sales_weekly['Date'].tolist()

    cant_sales_product = len(sales_units)
    
    if cant_sales_product > 16:
        n_sales = 16
        sales_units = sales_units[-n_sales:]
        sales_dates = sales_dates[-n_sales:]

    data = {'forecast_units': forecast_units,
             'forecast_dates': forecast_dates,
             'sales_units': sales_units,
             'sales_dates': sales_dates}

    return JsonResponse(data, safe = False)
    
# CRUD Category
@csrf_exempt
def create_category(request):
    try:
        if request.method == 'POST':
            stringCategory = request.body.decode('utf8').replace("'", '"')
            Category.objects.create(description=stringCategory)

            return HttpResponse("Operación exitosa", status=200)

    except:
        return HttpResponse("Operación fallida", status=400)

def get_all_categories(request):
    query = Category.objects.values('id','description')
    data = list(query)
    return JsonResponse(data, safe=False)

def get_category_by_id(request, id):
    category = get_object_or_404(Category, id=id)
    return render(request, 'category_detail.html', {'category': category})

@csrf_exempt
def update_category(request, id):
    try:
        category = get_object_or_404(Category, id=id)
        if request.method == 'PATCH':
            stringCategory = request.body.decode('utf8').replace("'", '"')
            dataCategory = json.loads(stringCategory)
            if 'description' in dataCategory:
                category.description = dataCategory['description']
            category.save()

            return HttpResponse("Operación exitosa", status=200)

    except:
        return HttpResponse("Operación fallida", status=400)

@csrf_exempt
def delete_category(request, id):
    try:
        if request.method == 'DELETE':
            category = get_object_or_404(Category, id=id)
            category.delete()
            return HttpResponse("Operación exitosa", status=200)
    except:
        return HttpResponse("Operación fallida", status=400)
