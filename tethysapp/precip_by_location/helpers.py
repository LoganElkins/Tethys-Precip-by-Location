from plotly import graph_objs as go 
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tethys_gizmos.gizmo_options import PlotlyView
from .app import PrecipByLocation
from .model import getAllDataNew, getLatLong

def create_graph(locID, latitude, longitude, height='520px', width='100%'):
    df = getAllDataNew(location_id_param=locID)
    # latitude, longiude = getLatLong(locID)
    months = df['month'].to_list()
    prcp = df['prcp'].to_list()
    avgTemp = df['tave'].to_list()
    minTemp = df['tmin'].to_list()
    maxTemp = df['tmax'].to_list()
    avgTempDict = {}
    prcpDict = {}
    minTempDict = {}
    maxTempDict = {}
    for i in range(len(months)):
        avgTempDict[months[i]] = avgTemp[i]
        prcpDict[months[i]] = prcp[i]
        minTempDict[months[i]] = minTemp[i]
        maxTempDict[months[i]] = maxTemp[i]
    newAvgTemp = []
    newMinTemp = []
    newMaxTemp = []
    newPrcp = []
    months.sort()
    for i in range(len(months)):
        newAvgTemp.append(avgTempDict[months[i]])
        newMinTemp.append(minTempDict[months[i]])
        newMaxTemp.append(maxTempDict[months[i]])
        newPrcp.append(prcpDict[months[i]])
    print(months)
    print(avgTemp)
    newAvgTemp = [(x * 9/5) + 32 for x in newAvgTemp]
    newMinTemp = [(x * 9/5) + 32 for x in newMinTemp]
    newMaxTemp = [(x * 9/5) + 32 for x in newMaxTemp]
    newPrcp = [(x/25.4) for x in newPrcp]
    for i in range(len(newPrcp)):
        if i != 0:
            newPrcp[i] = newPrcp[i] + newPrcp[i-1]
    data = [go.Scatter(x=months, y=newAvgTemp, name="Avg Temperature"), go.Scatter(x=months, y=newMinTemp, name="Min Temperature"), go.Scatter(x=months, y=newMaxTemp, name="Max Temperature")]
    layout = {
        'title': 'Tepmerature Data for {0}, {1}'.format(latitude, longitude),
        'xaxis': {'title': 'Time'},
        'yaxis': {'title': 'Temperature (F)'}
    }
    figure = {'data': data, 'layout': layout}
    temperature_plot = PlotlyView(figure, height=height, width=width)
    data = [go.Scatter(x=months, y=newPrcp, name="Precipitation")]
    layout = {
        'title': 'Cumulative Precipitation for {0}, {1}'.format(latitude, longitude),
        'xaxis': {'title': 'Time'},
        'yaxis': {'title': 'Precipitation (in)'}
    }
    figure = {'data': data, 'layout': layout}
    precipitation_plot = PlotlyView(figure, height=height, width=width)
    return temperature_plot, precipitation_plot