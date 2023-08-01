from django.shortcuts import render
from django.contrib import messages
from pacse_gyp_forecast.fill_tables.subir_info import *
from pacse_gyp_forecast.projections.projections import *
from django.shortcuts import get_object_or_404
from pacse_gyp_forecast.stock.upload_stock import filtrar_excel_stock
from pacse_gyp_forecast.fill_tables.verificacion_archivo import *
from pacse_gyp_forecast.fill_tables.subir_info import cargar_datos_inicial_bd
from pacse_gyp_forecast.models import Product, Sales, Category,Stock,Status
from django.views.decorators.csrf import csrf_exempt
from pacse_gyp_forecast.manage_status.manage_status import calculate_status
from django.http import JsonResponse
import json

def subida_inicial_categoria(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'El archivo seleccionado no es un archivo Excel válido.')
        else:
            try:
                #AQUI NO HAY VERIFICACIONES
                data = pd.read_excel(excel_file, sheet_name="Detalle Consolidado")
                subir_info_inicial_categoria(data)
                messages.success(request, 'Los datos se han insertado correctamente en la base de datos.')
            except Exception as e:
                messages.error(request, 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e))
    return render(request, 'subida_categoria.html')

def subida_inicial_status(request):
    if request.method == 'POST':
        try:
            #AQUI NO HAY VERIFICACIONES
            subir_info_inicial_status()
            messages.success(request, 'Los datos se han insertado correctamente en la base de datos.')
        except Exception as e:
            messages.error(request, 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e))
    return render(request, 'subida_status.html')

def subida_inicial_producto(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'El archivo seleccionado no es un archivo Excel válido.')
        else:
            try:
                #AQUI NO HAY VERIFICACIONES
                data = pd.read_excel(excel_file, sheet_name="Detalle Consolidado")
                subir_info_inicial_producto(data)
                messages.success(request, 'Los datos se han insertado correctamente en la base de datos.')
            except Exception as e:
                messages.error(request, 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e))
    return render(request, 'subida_categoria.html')

def subida_inicial_stock(request):
    if request.method == 'POST':
        try:
            #AQUI NO HAY VERIFICACIONES
            subir_info_inicial_stock()
            messages.success(request, 'Los datos se han insertado correctamente en la base de datos.')
        except Exception as e:
            messages.error(request, 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e))
    return render(request, 'subida_stock.html')

def subida_inicial_venta(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'El archivo seleccionado no es un archivo Excel válido.')
        else:
            try:
                data = pd.read_excel(excel_file, sheet_name="Detalle Consolidado")
                subir_info_inicial_ventas(data)
                messages.success(request, 'Los datos se han insertado correctamente en la base de datos.')
            except Exception as e:
                messages.error(request, 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e))
    return render(request, 'subida_categoria.html')  

@csrf_exempt
def subida_excel(request):
    response_data = {
        'message':'',
        'message_error':''
    }
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            print("ERROR:",'El archivo seleccionado no es un archivo Excel válido.')
            response_data['message_error'] = 'El archivo seleccionado no es un archivo Excel válido.'
            return JsonResponse(response_data, status=400)

        with open("pacse_gyp_forecast/excel/archivo.xlsx", 'wb') as destino:
            for chunk in excel_file.chunks():
                destino.write(chunk)

        data = pd.read_excel("pacse_gyp_forecast/excel/archivo.xlsx", sheet_name="Detalle Consolidado", engine='openpyxl')

        if not verificar_existencia_columnas(data):
            print("ERROR:", "Revisar el formato del archivo, falta una de las siguientes columnas 'Clase', 'SKU Master', 'Descripcion Master', 'Fecha de compra', 'Unidades', 'Mes', 'Año'")
            response_data['message_error'] = "Revisar el formato del archivo, falta una de las siguientes columnas 'Clase', 'SKU Master', 'Descripcion Master', 'Fecha de compra', 'Unidades', 'Mes', 'Año'"
            return JsonResponse(response_data, status=400)
            
        data = data[['Clase', 'SKU Master', 'Descripcion Master', 'Fecha de compra','Unidades', 'Mes', 'Año']]

        interruptor = 0

        if not validar_datos_numericos(data):
            response_data['message_error'] = "La columna 'Unidades' contiene valores no numericos\n"
            interruptor = 1

        if not validar_fecha(data):
            response_data['message_error'] = response_data['message_error'] + "La columna 'Fecha de compra' no esta completamente en formato DD-MM-AA\n"            
            interruptor = 1
            
        resultado_unicidad_clase_sku = validar_unicidad_clase_sku(data)
        if len(resultado_unicidad_clase_sku) != 0:
            response_data['message_error'] = response_data['message_error'] + resultado_unicidad_clase_sku+'\n'
            interruptor = 1
        
        if interruptor == 0: 
            cantidad_category = Category.objects.count()
            cantidad_product = Product.objects.count()
            cantidad_status = Status.objects.count()
            cantidad_stock = Category.objects.count()
            cantidad_sales =Sales.objects.count()

            # Si todas las tablas tienen elementos, se cargan los datos nuevos
            if cantidad_category and cantidad_product and cantidad_status and cantidad_stock and cantidad_sales:
                try:
                    # Se ordena y filtra el dataframe para obtener solo los datos nuevos 
                    dataframe_filtered = sort_cut_dataframe(data)
                    
                    print("Carga datos")
                    # Se cargan los datos del dataframe en la base de datos
                    cargar_datos_bd(dataframe_filtered)
                    print("FIN Carga datos")
                    ###########################################################################################
                    # AQUÍ LA AGREGUÉ PORQUE NO ESTABA ANTES 
                    # Se obtienen los SKU de los productos nuevos a proyectar
                    #skus_list = dataframe_filtered['SKU Master'].unique()
                    #sales_dataframe = get_sales_in_bd_dataframe(skus_list)
                    #Marcar como ignorados aquellos productos con ultimas ventas antiguas y productos muy nuevos
                    #ignore_old_and_new_products(skus_list, sales_dataframe)
                    ###########################################################################################

                    response_data['message'] = 'Los datos se han insertado correctamente en la base de datos.'
                    return JsonResponse(response_data, status=200)
                except Exception as e:
                    print("ERROR: ", 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e))
                    response_data['message_error'] = 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e)
                    return JsonResponse(response_data, status=400)

            else: # Si hay una de estas tablas sin elementos entonces se debe llenar las tablas con la subida inicial
                
                try:
                    # Se ordena y filtra el dataframe para obtener solo los datos nuevos, en este caso al no haber datos, el dataframe debería quedar igual
                    dataframe_filtered = sort_cut_dataframe(data)
                    
                    print("Carga inicial datos")
                    # Se cargan los datos del dataframe en la base de datos
                    cargar_datos_inicial_bd(dataframe_filtered)
                    print("FIN Carga inicial datos")
                    ###########################################################################################
                    # AQUI ESTABA INICIALMENTE LA FUNCIÓN
                    # Se obtienen los SKU de los productos nuevos a proyectar
                    skus_list = dataframe_filtered['SKU Master'].unique()
                    sales_dataframe = get_sales_in_bd_dataframe(skus_list)
                    #Marcar como ignorados aquellos productos con ultimas ventas antiguas y productos muy nuevos
                    ignore_old_and_new_products(skus_list, sales_dataframe)
                    ###########################################################################################


                    response_data['message'] = 'Los datos se han insertado correctamente en la base de datos.'
                    return JsonResponse(response_data, status=200)
                except Exception as e:
                    print("ERROR:", 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e))
                    response_data['message_error'] = 'Ocurrió un error al insertar los datos en la base de datos: ' + str(e)
                    return JsonResponse(response_data, status=400)
        else:
            print("ERROR:", "ERROR\n Se encontraron los siguientes errores:'n" + response_data['message_error'])
            response_data['message_error'] = "ERROR\n Se encontraron los siguientes errores:'n" + response_data['message_error']
            return JsonResponse(response_data, status=400)


@csrf_exempt
def subida_stock(request):
    response_data = {
        'message': '',
        'message_error': ''
    }
    if request.method == 'POST' and request.FILES.get('excel_file') and request.POST.get('selected_date'):
        try:
            # Obtener el archivo Excel enviado desde el formulario
            excel_file = request.FILES['excel_file']

            # Obtener la fecha enviada desde el formulario
            selected_date = request.POST.get('selected_date')
            selected_date = datetime.fromisoformat(selected_date).date()
            
            # Verificación de que el archivo a leer sea de tipo '.xlsx'
            if not excel_file.name.endswith('.xlsx'):
                response_data['message_error'] = "ERROR: El archivo seleccionado no es un archivo Excel válido(.xlsx)"
                print("Error1: ",response_data['message_error'])
                return JsonResponse(response_data, status=400)
            # Se guarda el archivo dentro de la aplicación
            with open("pacse_gyp_forecast/excel/archivo_stock.xlsx", 'wb') as destino:
                for chunk in excel_file.chunks():
                    destino.write(chunk)
            
            # Dirección del archivo de stock
            file_excel = "pacse_gyp_forecast/excel/archivo_stock.xlsx"
            
            df, verification_results = filtrar_excel_stock(file_excel)
            all_true = all(verification_results)

            if all_true:
                # se sube el archivo usando el df entregado
                for index, row in df.iterrows():
                    #print("index: ", index)
                    codigo = row['Código']
                    stock_disponible = row['Stock disponible']
                    
                    if Product.objects.filter(SKU=codigo).exists():
                        producto = get_object_or_404(Product ,SKU = codigo)
                        if Stock.objects.filter(Product = producto).exists():

                            stock = get_object_or_404(Stock , Product = producto)
                            stock.quantity = stock_disponible
                            stock.date = selected_date
                            stock.save()

                            if producto.forecast_set.exists():
                                new_status=calculate_status(producto,stock)
                                # Actualizar atributo status
                                producto.Status_id = new_status
                                producto.save()
                            else:
                                response_data['message_error'] = f"Error: No hubo cálculo de estado porque el Producto {codigo} no tiene pronósticos en la base de datos\n"

                        else:
                            response_data['message_error'] = response_data['message_error'] + f"Error: El Producto {codigo} no tiene un stock asociado en la base de datos\n"
                    
                    
                    else: #Producto no existe
                        print("Producto no existe en bd")
                        response_data['message_error'] = response_data['message_error'] + f"Error: Producto {codigo} no se encuentra en la base de datos\n"
                        
                # Si la solicitud es de tipo POST, y la subida está bien, entonces se manda success
                response_data = {
                    'message': f"SUCCESS: Los datos de stock se han insertado correctamente en la base de datos.\n"
                }
                print("Se terminó subida stock:", response_data['message'])
                return JsonResponse(response_data, status=200)
        
            else:
                error = "No se puede subir el stock debido a los siguientes errores:\n"
                if not verification_results[0]:
                    error = error + "Falta una de las siguientes columnas: 'Código' o 'Stock disponible'\n"
                if not verification_results[1]:
                    error = error + "Hay valores que no son letras en la columna código\n"
                if not verification_results[2]:
                    error = error + "Hay valores nulos en las columnas Código y/o Stock disponible\n"
                if not verification_results[3]:
                    error = error + "Hay valores duplicados en la columna Código\n"
                messages.error(request, error)
                # Si la solicitud es de tipo POST, y hay un error en la subida, se devuelve el error
                response_data = {
                    'message_error': f"Error: {error}"
                }
                print("Error3: ",response_data['message_error'])
                return JsonResponse(response_data, status=400)

        except Exception as e:
            #print("Parte5")
            messages.error(request, 'Ocurrió un error al insertar el stock en la base de datos: ' + str(e))
            # Si la solicitud es de tipo POST, y hay un error en la subida, se devuelve el error
            response_data = {
                'message_error': f"Error: {str(e)}"
            }
            print("Error4: ",response_data['message_error'])
            return JsonResponse(response_data, status=400)
    else:
        # Si la solicitud no es de tipo POST, devuelve una respuesta de error
        response_data = {
            'message_error': 'Error: se esperaba una solicitud POST'
        }
        print("Error5: ",response_data['message_error'])
        return JsonResponse(response_data, status=400)


@csrf_exempt
def calculo_manual_status(request):
    response_data = {
        'message': '',
        'message_error': ''
    }
    if request.method == 'POST' and request.POST.get('SKU'):
        try:
            codigo = request.POST.get('SKU')
            if not Product.objects.filter(SKU=codigo).exists():
                response_data['message_error'] = response_data['message_error'] + f"Error: Producto {codigo} no se encuentra en la base de datos\n"
            elif not Stock.objects.filter(Product = producto).exists():
                response_data['message_error'] = response_data['message_error'] + f"Error: El Producto {codigo} no tiene un stock asociado en la base de datos\n"
            else:
                # Si el producto existe y tiene stock asociado en la base de datos
                producto = get_object_or_404(Product ,SKU = codigo)
                stock = get_object_or_404(Stock , Product = producto)
                if producto.forecast_set.exists():
                    new_status=calculate_status(producto,stock)
                    # Actualizar atributo status
                    producto.Status_id = new_status
                    producto.save()
                    response_data['message'] = f"Success: Cálculo de estado del Producto {codigo} realizado correctamente\n"
                    return JsonResponse(response_data, status=200)
                else:
                    response_data['message_error'] = f"Error: No hubo cálculo de estado porque el Producto {codigo} no tiene pronósticos en la base de datos\n"
                    return JsonResponse(response_data, status=400)
        except Exception as e:
            messages.error(request, f'Ocurrió un error con el SKU ingresado: ' + str(e))
            response_data = {
                'message_error': f"Error: {str(e)}"
            }
            return JsonResponse(response_data, status=400)
    else:
        response_data = {
            'message_error': 'Error: se esperaba una solicitud POST con un SKU'
        }
        return JsonResponse(response_data, status=400)

@csrf_exempt
def calculo_manual_forecast(request):
    response_data = {
        'message': '',
        'message_error': ''
    }
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            if 'skus' in data and isinstance(data['skus'], list):
                skus_list = data['skus']
                ###########################################################
                sales_dataframe = get_sales_in_bd_dataframe(skus_list)
                # Aquí aplicamos el forecast, con una función que recibe todos los sku a actualizar
                # En este caso no deberían obtenerse todas las ventas de la BD, ya que al ser los datos iniciales estarán todas en el dataframe filtrado (dataframe_filtered = data)
                forecast_all_products(sales_dataframe, skus_list)

                for sku in skus_list:
                    product_to_update = Product.objects.get(SKU = sku)
                    product_to_update.standby = False
                    product_to_update.save()

                ###########################################################
                return JsonResponse(response_data, status=200)
            else:
                raise ValueError('Lista de SKUs no encontrada en los datos enviados.')
        except Exception as e:
            messages.error(request, 'Ocurrió un error al procesar la lista de SKUs: ' + str(e))
            response_data = {
                'message': f"Error: {str(e)}"
            }
            return JsonResponse(response_data, status=400)
    else:
        response_data = {
            'message': 'Error: se esperaba una solicitud POST con una lista de SKUs'
        }
        return JsonResponse(response_data, status=400)
