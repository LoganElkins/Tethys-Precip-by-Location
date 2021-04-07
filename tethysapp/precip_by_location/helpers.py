from plotly import graph_objs as go 
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tethys_gizmos.gizmo_options import PlotlyView
from .app import PrecipByLocation
from .model import getAllData, getLatLong

def create_graph(locID, height='520px', width='100%'):
    df = getAllData(location_id=locID)
    latitude, longiude = getLatLong(locID)
    months = df['month'].to_list()
    prcp = df['prcp'].to_list()
    avgTemp = df['tave'].to_list()
    minTemp = df['tmin'].to_list()
    maxTemp = df['tmax'].to_list()
    
    avgTemp = [(x * 9/5) + 32 for x in avgTemp]
    minTemp = [(x * 9/5) + 32 for x in minTemp]
    maxTemp = [(x * 9/5) + 32 for x in maxTemp]
    prcp = [(x/25.4) for x in prcp]
    for i in range(len(prcp)):
        if i != 0:
            prcp[i] = prcp[i] + prcp[i-1]
    data = [go.Scatter(x=months, y=avgTemp, name="Average Temperature"), go.Scatter(x=months, y=minTemp, name="Minimum Temperature"), go.Scatter(x=months, y=maxTemp, name="Maximum Temperature")]
    layout = {
        'title': 'Tepmerature From Last Nine Months for {0}, {1}'.format(latitude, longiude),
        'xaxis': {'title': 'Time'},
        'yaxis': {'title': 'Temperature (F)'}
    }
    figure = {'data': data, 'layout': layout}
    temperature_plot = PlotlyView(figure, height=height, width=width)
    data = [go.Scatter(x=months, y=prcp, name="Precipitation")]
    layout = {
        'title': 'Cumulative Precipitation for {0}, {1}'.format(latitude, longiude),
        'xaxis': {'title': 'Time'},
        'yaxis': {'title': 'Precipitation (in)'}
    }
    figure = {'data': data, 'layout': layout}
    precipitation_plot = PlotlyView(figure, height=height, width=width)
    return temperature_plot, precipitation_plot
    