from pacse_gyp_forecast.models import *
from django.shortcuts import get_object_or_404
from datetime import datetime

def status_by_time(periods_till_stock_break, restock_time):
    print("status_by_time")
    window_to_restock = periods_till_stock_break - restock_time
    if (window_to_restock > 8):
        return 1
    elif ( 8 >= window_to_restock > 4):
        return 2
    else:
        return 3

def calc_stocks_by_period(stock_quantity,forecasts_by_product,sales_by_stock_date):
    stocks_by_period =[]
    quantity_by_period = stock_quantity
    for sale in sales_by_stock_date:
        quantity_by_period = quantity_by_period - sale.units
        stocks_by_period.append(quantity_by_period)
    for forecast in forecasts_by_product:
        quantity_by_period = quantity_by_period - forecast.units
        stocks_by_period.append(quantity_by_period)
    return stocks_by_period

def periods_till_stock_break(quantitys_by_periods):
    period_counter = 1
    for quantity in quantitys_by_periods:
        if quantity <= 0:
            return period_counter
        period_counter += 1 
    return period_counter


def calculate_status(product,stock_by_product):
    print("Calculo de status")
    # Se obtiene el producto y el tiempo para hacer el restock
    restock_time = product.restock_time
    stock_date = stock_by_product.date
    stock_date = datetime.combine(stock_date, datetime.min.time())

    # Se obtienen los pronosticos y el stock del producto correspondiente
    sales_by_stock_date = Sales.objects.filter(date__gt=stock_date)
    forecasts_by_product = Forecast.objects.filter(Product_id = product.id).order_by('date')
    stock_quantity = stock_by_product.quantity

    # Se calcula la cantidad de producto que hay tras las ventas de cada periodo de los pronosticos
    quantitys_by_periods = calc_stocks_by_period(stock_quantity, forecasts_by_product,sales_by_stock_date)
    # Se obtiene cuantos periodos hay
    periods_till_break = periods_till_stock_break(quantitys_by_periods)

    new_status = status_by_time( periods_till_break, restock_time)
    print(f"SKU producto = {product.SKU}")
    print(f"new_status = {new_status}")

    return new_status

