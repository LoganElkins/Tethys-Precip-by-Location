from django.shortcuts import render
from tethys_sdk.workspaces import app_workspace
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import Button, MapView, DataTableView, MVLayer, MVView
from .model import getAllData
from .helpers import create_graph
import pandas as pd

@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    data = getAllData(testingHomePage=True)
    features = []
    lat_list = []
    long_list = []

    for index, row in data.iterrows():
        lat_list.append(row['latitude'])
        long_list.append(row['longitude'])
        location_feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['longitude'], row['latitude']],
            },
            'properties':{
                'location_id': row['location_id'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'prcp': row['prcp'],
                'tave': row['tave'],
                'tmin': row['tmin'],
                'tmax': row['tmax']
            }
        }
        features.append(location_feature)
    
    locations_feature_collection = {
        'type': 'FeatureCollection',
        'crs':{
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }
    style = {'ol.style.Style': {
        'image': {'ol.style.Circle': {
            'radius': 1,
            'fill': {'ol.style.Fill': {
                'color':  '#d84e1f'
            }},
            'stroke': {'ol.style.Stroke': {
                'color': '#ffffff',
                'width': 1
            }}
        }}
    }}

    locations_layer = MVLayer(
        source='GeoJSON',
        options=locations_feature_collection,
        legend_title='Locations',
        layer_options={'style': style},
        feature_selection=True
    )

    try:
        view_center=[sum(long_list) / float(len(long_list)), sum(lat_list)/ float(len(lat_list))]
    except ZeroDivisionError:
        view_center = [-98.6, 39.8]
    
    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=4.5,
        maxZoom=18,
        minZoom=2
    )

    precip_by_location_map = MapView(
        height='100%',
        width='100%',
        layers=[locations_layer],
        basemap='OpenStreetMap',
        view=view_options
    )

    context = {
        'precip_by_location_map': precip_by_location_map,
    }

    return render(request, 'precip_by_location/home.html', context)


@app_workspace
@login_required()
def list_data(request, app_workspace):
    data = getAllData(100)
    table_rows = []
    for index, row in data.iterrows():
        table_rows.append((row['latitude'], row['longitude'], row['prcp'], row['tave'], row['tmax'], row['tmin']))
    
    data_table = DataTableView(
        column_names=('Latitude', 'Longitude', 'Prcp', 'Tave', 'Tmax', 'Tmin'),
        rows = table_rows,
        searching=False,
        orderClasses=False,
        lengthMenu = [[10, 25, 50, -1], [10, 25, 50, "All"]],
    )

    context = {
        'data_table': data_table
    }

    return render(request, 'precip_by_location/list_data.html', context)


@login_required()
def graph(request, locID):
    temperature_plot, precipitation_plot = create_graph(locID)
    context = {
        'temperature_plot': temperature_plot,
        'precipitation_plot': precipitation_plot
    }
    return render(request, 'precip_by_location/graph.html', context)


@login_required()
def graph_ajax(request, locID):
    print("\n\n\nINSIDE GRAPH_AJAX FUNCTION\n\n")
    temperature_plot, precipitation_plot = create_graph(locID)
    context = {
        'temperature_plot': temperature_plot,
        'precipitation_plot': precipitation_plot
    }
    return render(request, 'precip_by_location/graph_ajax.html', context)