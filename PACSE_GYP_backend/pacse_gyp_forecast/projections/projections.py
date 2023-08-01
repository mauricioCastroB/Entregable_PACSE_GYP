import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from math import ceil
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.filterwarnings("ignore")
warnings.simplefilter('ignore', ConvergenceWarning)
from pmdarima.arima import auto_arima, ndiffs, nsdiffs
from statsmodels.tsa.api import ExponentialSmoothing
from pacse_gyp_forecast.models import Product, Forecast, Sales


#Función que crea un dataframe de las ventas que corresponden a la lista de SKUs
def get_sales_in_bd_dataframe(skus_list):

    data = []

    for sku in skus_list:
        try:
            product_bd = Product.objects.get(SKU = sku)
            sales_by_product = Sales.objects.filter(Product_id = product_bd.id)

            for sale in sales_by_product:
                data.append({
                    'SKU': sku,
                    'Date': sale.date,
                    'Units': sale.units
                })
        except Product.DoesNotExist:
            # Manejar el caso en el que el SKU no exista en la base de datos
            print(f"El SKU '{sku}' no existe")
    
    # Crear el dataframe a partir de la lista de diccionarios
    df = pd.DataFrame(data)
    return df

#Ignorar productos que poseen un año o mas sin ventas     
def ignore_old_and_new_products(SKU_list, df_products):
    for SKU in SKU_list:
        df_product = df_products[df_products['SKU'] == SKU]
        recent_sale_date = df_product['Date'].max().date()
        now_date = datetime.now().date()
        diff_time = (now_date - recent_sale_date).days

        if diff_time > 364:
            product_to_ignore = Product.objects.get(SKU = SKU)
            product_to_ignore.ignored = True
            product_to_ignore.save()
            
        df_weekly = filter_SKU(df_product, SKU)

        if df_weekly.shape[0] <= 16:
            product_to_ignore = Product.objects.get(SKU = SKU)
            product_to_ignore.ignored = True
            product_to_ignore.save()
        
    return True

#Obtener todos los SKU de un dataframe
def list_all_SKUs(sales_df):
    
    all_SKUs = sales_df['SKU'].unique()

    return all_SKUs

#Obtener un datafame de todas las ventas de un SKU
def filter_SKU(sales_df, SKU_product):
    
    sales_df_product = sales_df[sales_df['SKU'] == SKU_product]
    sales_df_product = sales_df_product.groupby(pd.Grouper(key='Date',freq='W'))['Units'].sum().reset_index()
    sales_df_product = sales_df_product.set_index('Date')
    
    return sales_df_product

#Obtener el diferenciador D y d para el algoritmo de sarima
def evaluate_diff(sales_ts, periods):

    d_value = ndiffs(x = sales_ts,
                     alpha = 0.05,
                     test = 'adf')
    
    D_value = nsdiffs(x = sales_ts,
                      m = periods,
                      test = 'ch')
    
    return D_value , d_value

#Obtener el modelo de sarima y realizar sus proyecciones
def generate_predictions(sales_ts, D_value, d_value, periods):

    sarima_model = auto_arima(sales_ts,
                              test = 'adf',
                              d = d_value,
                              seasonal = True,
                              seasonal_test = 'ch',
                              D = D_value,
                              m = periods,
                              trace = False,
                              max_order = None)

    predictions = sarima_model.predict(n_periods = 32)

    return predictions

#Obtener un arreglo con las fechas futuras de las proyecciones
def generate_future_date(df_date_product, n_dates):
    
    recent_date = df_date_product.max()

    list_future_date = []

    i = 1
    while i <= n_dates:
        new_date = recent_date + timedelta(weeks = i)
        list_future_date.append(new_date.date())
        i = i + 1
    return list_future_date


#Redondear los valores de las proyecciones al entero mas cercano (0 para los negativos)
def round_predictions(prediction_series):
    i = 0
    prediction_series_rounded = []
    while i < len(prediction_series):
        if prediction_series[i] < 0:
            prediction_series_rounded.append(0)
        else:
            prediction_series_rounded.append(round(prediction_series[i]))
        i += 1
    return prediction_series_rounded

#Guardar las predicciones en la base de datos
def save_forecast(future_dates, predictions, id):
    list_forecast = Forecast.objects.filter(Product_id = id).order_by('id')
    if list_forecast:
        
        i = 0
        for forecast in list_forecast:
            forecast.date = future_dates[i]
            forecast.units = predictions[i]
            forecast.save()
            i = i + 1
    else:
        i = 0
        while i < 32:
            Forecast.objects.create(date = future_dates[i], units = predictions[i], Product_id = id)
            i+=1
    return True

#Calcular proyeciones con el algoritmo de sarima
def forecast_sarima(sales_df_product,id):
    sales_acum_product = sales_df_product['Units'].cumsum().values.tolist()
    Diff_value, diff_value = evaluate_diff(sales_acum_product, 52)
    predictions_acum = generate_predictions(sales_acum_product, Diff_value, diff_value, 52)
    predictions = pd.DataFrame(predictions_acum).diff()[0].values.tolist()
    predictions[0] = predictions_acum[0] - sales_acum_product[len(sales_acum_product)-1]
    predictions_rounded = round_predictions(predictions)
    future_date = generate_future_date(sales_df_product.index, 32)
    save_forecast(future_date,predictions_rounded,id)

    return True

#Calcular proyeciones con el algoritmo de suavizado exponencial triple
def forecast_exponential_smooth(sales_df_product,id):
    sales_acum_product = sales_df_product.cumsum()
    periods = ceil(sales_acum_product.shape[0]/3)
    model_w = ExponentialSmoothing(sales_acum_product, seasonal_periods = periods, trend = 'add', seasonal = 'add')
    model_w_fit = model_w.fit(optimized = True)
    predictions_acum = model_w_fit.forecast(32)
    predictions = predictions_acum.diff()
    predictions[0] = predictions_acum[0] - sales_acum_product['Units'][-1]
    predictions_rounded = round_predictions(predictions)
    future_date = generate_future_date(sales_df_product.index, 32)
    save_forecast(future_date,predictions_rounded,id)

    return True
    
#Funcion principal que calcula todos los forecast de la lista de SKU dada con su respectivo dataframe de ventas
def forecast_all_products(sales_df, list_SKUs):
    if len(list_SKUs) == 0:
        return True
    
    for SKU in list_SKUs:
        sales_df_product = filter_SKU(sales_df, SKU)
        cant_sales = sales_df_product.shape[0]
        product_to_update = Product.objects.get(SKU = SKU)
        
        if product_to_update.ignored != True:
            
            if cant_sales >= 52: # Utilizar el modelo de sarima
                forecast_sarima(sales_df_product, product_to_update.id)

            elif cant_sales > 16: # Utilizar el modelo de suavizado exponencial triple
                forecast_exponential_smooth(sales_df_product, product_to_update.id)

            else: #Se marca como ignorado el producto ya que no cumple con los requisitos para hacerle proyecciones

                product_to_update.ignored = True
                product_to_update.save()                

    #Fin de la funcion
    return True