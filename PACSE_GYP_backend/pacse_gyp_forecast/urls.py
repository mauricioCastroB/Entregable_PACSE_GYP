from django.urls import path
from pacse_gyp_forecast.views_subida_datos import subida_inicial_categoria,subida_inicial_status,subida_inicial_producto,subida_inicial_stock
from pacse_gyp_forecast.views_subida_datos import subida_inicial_venta,subida_excel,subida_stock
from pacse_gyp_forecast.views_subida_datos import calculo_manual_forecast, calculo_manual_status
from pacse_gyp_forecast.views_crud import get_info_tabla, get_forecast_and_sales, get_product_by_id, ignore_product, dis_ignore_product, update_standby
from pacse_gyp_forecast.views_crud import update_knownProduct_by_id , softDelete_knownProduct_by_id
from pacse_gyp_forecast.views_crud import get_last_sales, get_last_stock
from pacse_gyp_forecast.views_crud import update_product_status_by_id, salir, drop_table, update_product,get_all_categories, update_category,create_category,delete_category

app_name = 'pacse_gyp_forecast'

urlpatterns = [
    path('subida_categoria/', subida_inicial_categoria, name = 'subida_categoria'),
    path('subida_status/', subida_inicial_status, name = 'subida_status'),
    path('subida_producto/', subida_inicial_producto, name = 'subida_producto'),
    path('subida_venta/', subida_inicial_venta, name = 'subida_venta'),
    path('subida_excel/', subida_excel, name = 'subida_excel'),
    path('subida_stock/', subida_stock, name = 'subida_stock'),
    path('productos/', get_info_tabla, name = 'get_info_tabla'),
    path('productos/<int:id>', get_product_by_id, name='get_product_by_id'),
    path('productos/<int:id>/status', update_product_status_by_id, name='update_product_status_by_id'),
    path('predicciones/<int:id>', get_forecast_and_sales, name='get_forecast_and_sales'),
    path('productos/ignorar/<int:id>', ignore_product, name='ignore_product'),
    path('productos/designorar/<int:id>', dis_ignore_product, name='dis_ignore_product'),
    path('salir', salir, name='salir'),
    path('sale/last_sales/', get_last_sales, name = 'get_last_sales'),
    path('sale/last_stock/', get_last_stock, name = 'get_last_stock'),
    path('calculo_manual_forecast/', calculo_manual_forecast, name = 'calculo_manual_forecast'),
    path('calculo_manual_status/', calculo_manual_status, name = 'calculo_manual_status'),
    path('productos_known/modificar/<int:id>', update_knownProduct_by_id, name = 'update_knownProduct_by_id'),
    path('productos_known/eliminar/<int:id>', softDelete_knownProduct_by_id, name ='sofDelete_knownProduct_by_id'),
    path('drop/', drop_table, name='drop_table'),
    path('update_product/<int:id>', update_product, name='update_product'),
    path('update_category/<int:id>', update_category, name='update_category'),
    path('delete_category/<int:id>', delete_category, name='delete_category'),
    path('create_category/', create_category, name='create_category'),
    path('get_all_categories', get_all_categories, name='get_all_categories'),
    path('update_standby', update_standby, name ='update_standby')
]
