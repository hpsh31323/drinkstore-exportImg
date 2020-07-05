#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Your module description
"""
import json
import matplotlib.patches as mpatches
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import boto3
import io


# 取日均溫與業績關係圖
def exportImgB(event, context):
    s3 = boto3.client('s3')
    object = s3.get_object(Bucket='drinkstore-static', Key='json/avg_temp_tpi.json')
    serializedObject = object['Body'].read()
    dict_year_temp = json.loads(serializedObject)

    s3 = boto3.client('s3')
    object = s3.get_object(Bucket='drinkstore-static', Key='json/order_amount.json')
    serializedObject = object['Body'].read()
    dict_order_amount = json.loads(serializedObject)

    dict_max = dict_year_temp["dict_max"]
    dict_min = dict_year_temp["dict_min"]
    dict_avg = dict_year_temp["dict_avg"]

    key_set = sorted(dict_order_amount.keys()) if len(dict_order_amount.keys()) < len(dict_max.keys()) else sorted(
        dict_max.keys())
    list_keys = []
    list_avg_temps = []
    list_max_temps = []
    list_min_temps = []
    list_orders = []

    for key in key_set:
        if not (key in (dict_max if len(dict_order_amount.keys()) < len(dict_max.keys()) else dict_order_amount)):
            continue
        list_keys.append(key)
        list_max_temps.append(eval(dict_max[key]))
        list_min_temps.append(eval(dict_min[key]))
        list_avg_temps.append(eval(dict_avg[key]))
        list_orders.append(dict_order_amount[key])

    # 圖1(Avg Temp)
    fig, ax1 = plt.subplots()
    plt.title('Avg Temp')
    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temp(C)', color=color)
    ax1.plot(list_keys, list_avg_temps, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.xaxis.set_major_locator(MultipleLocator(10))
    plt.xticks(rotation=90)
    ax1.grid()
    plt.tight_layout()
    uploadImage(fig, "temp")

    # 圖2(Sales)
    fig, ax1 = plt.subplots()
    plt.title('Sales')
    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('NTD', color=color)
    ax1.plot(list_keys, list_orders, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.xaxis.set_major_locator(MultipleLocator(10))
    plt.xticks(rotation=90)
    ax1.grid()
    plt.tight_layout()
    uploadImage(fig, "sales")

    # 圖3(Avg Temp & Sales)
    fig, ax1 = plt.subplots()
    plt.title('Avg Temp & Sales')
    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temp(C)', color=color)
    ax1.plot(list_keys, list_avg_temps, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    plt.xticks(rotation=90)
    # instantiate a second axes that shares the same x-axis
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.plot(list_keys, list_orders, color=color)
    ax2.set_ylabel('NTD', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax1.xaxis.set_major_locator(MultipleLocator(10))  # x軸標籤間距
    ax1.grid()
    plt.tight_layout()
    # plt.figure(dpi=150)  # 像素設定
    # ax.grid() 網格
    uploadImage(fig, "temp_sales")

    response = {
        "statusCode": 200,
        "body": "export sucess"
    }

    return response


def exportImgF(event, context):
    s3 = boto3.client('s3')
    object = s3.get_object(Bucket='drinkstore-static', Key='json/forecast.json')
    serializedObject = object['Body'].read()
    forecast = json.loads(serializedObject)

    list_maxT = forecast["list_maxT"]
    list_minT = forecast["list_minT"]
    date1 = forecast["date_f"]
    elastic_net_f = forecast["elastic_net_f"]
    lasso_f = forecast["lasso_f"]
    elastic_net_score = forecast["elastic_net_score"]
    lasso_score = forecast["lasso_score"]

    # 圖1(Temp)
    fig, ax1 = plt.subplots()
    plt.title('Temp(C)', color="black")
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temp(C)')
    ax1.plot(date1, list_maxT, color='tab:red')
    ax1.plot(date1, list_minT, color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='black')
    plt.xticks(rotation=45)
    red_patch = mpatches.Patch(color='red', label='max temp')
    bue_patch = mpatches.Patch(color='blue', label='min temp')
    plt.legend(handles=[red_patch, bue_patch], bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
               ncol=2, mode="expand", borderaxespad=0.)
    ax1.grid()
    plt.tight_layout()
    uploadImage(fig, "temp_f")

    # 圖2(Sales)
    fig, ax1 = plt.subplots()
    plt.title('Sales', color="black")
    ax1.set_xlabel('Date')
    ax1.set_ylabel('NTD')
    ax1.plot(date1, elastic_net_f, color='tab:green')
    ax1.plot(date1, lasso_f, color='tab:orange')
    ax1.tick_params(axis='y', labelcolor='black')
    green_patch = mpatches.Patch(color='green', label='elastic_net_f')
    orange_patch = mpatches.Patch(color='orange', label='lasso_f')
    plt.legend(handles=[green_patch, orange_patch], bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
               ncol=2, mode="expand", borderaxespad=0.)
    plt.xticks(rotation=45)
    ax1.grid()
    ax1.text(0.83, -0.3, 'Accuracy(ElasticNet):%.6f' % elastic_net_score,
             horizontalalignment='center', color="green", fontsize=8,
             verticalalignment='top',
             transform=ax1.transAxes)
    ax1.text(0.855, -0.35, 'Accuracy(Lasso):%.6f' % lasso_score,
             horizontalalignment='center', color="orange", fontsize=8,
             verticalalignment='top',
             transform=ax1.transAxes)
    plt.tight_layout()
    uploadImage(fig, "sales_f")

    # 圖3(Avg Temp & Sales)

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temp(C)', color='black')
    ax1.plot(date1, list_maxT, color='tab:red', label="max temp")
    ax1.plot(date1, list_minT, color='tab:blue', label="min temp")
    ax1.tick_params(axis='y', labelcolor='black')
    plt.xticks(rotation=45)
    # instantiate a second axes that shares the same x-axis
    ax2 = ax1.twinx()
    ax2.plot(date1, elastic_net_f, color='tab:green')
    ax2.plot(date1, lasso_f, color='tab:orange')
    ax2.set_ylabel('NTD', color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    red_patch = mpatches.Patch(color='red', label='max temp')
    bue_patch = mpatches.Patch(color='blue', label='min temp')
    green_patch = mpatches.Patch(color='green', label='elastic_net_f')
    orange_patch = mpatches.Patch(color='orange', label='lasso_f')
    plt.legend(handles=[red_patch, bue_patch, green_patch, orange_patch], bbox_to_anchor=(0., 1.02, 1., .102),
               loc='lower left',
               ncol=4, mode="expand", borderaxespad=0.)

    ax1.grid()
    plt.tight_layout()
    uploadImage(fig, "forecast")

    response = {
        "statusCode": 200,
        "body": "export sucess"
    }

    return response


def uploadImage(fig, filename):
    img_data = io.BytesIO()
    fig.savefig(img_data, format='png', dpi=300)
    img_data.seek(0)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket("drinkstore-static")
    bucket.put_object(Body=img_data, ContentType='image/png', Key="image/forecasting/" + filename)
