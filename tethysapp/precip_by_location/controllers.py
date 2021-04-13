from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from tethys_sdk.workspaces import app_workspace
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import Button, MapView, DataTableView, MVLayer, MVView, TextInput
from .model import getAllData, getLocID, getClosestLatLong
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
                'county_state': row['county_state'],
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
                'color':  'rgba(255, 255, 0, 0.01)'
            }},
            'stroke': {'ol.style.Stroke': {
                'color': 'rgba(255, 255, 0, 0.01)',
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


@login_required()
def graph_ajax(request, locID):
    temperature_plot, precipitation_plot = create_graph(locID)
    context = {
        'temperature_plot': temperature_plot,
        'precipitation_plot': precipitation_plot
    }
    return render(request, 'precip_by_location/graph_ajax.html', context)


@login_required()
def graph(request):
    latitude_error = ''
    longitude_error = ''
    lat_input = TextInput(
        display_text='Latitude',
        name='latitude',
        error=latitude_error
        )
    long_input = TextInput(
        display_text='Longtiude',
        name='longitude',
        error=longitude_error
        )

    submit_button = Button(
        display_text='Submit',
        name='submit-button',
        icon='glyphicon glyphicon-ok',
        style='success',
        attributes={'form': 'view-graphs-form'},
        submit=True,
    )

    cancel_buton = Button(
        display_text='Cancel',
        name='cancel-button',
        icon='glyphicon glyphicon-remove',
        href=reverse('precip_by_location:home')
    )
    context = {
                'lat_input': lat_input,
                'long_input': long_input,
                'submit_button': submit_button,
                'cancel_button': cancel_buton
            }
    if request.POST and 'submit-button' in request.POST:
        import time
        start_time = time.time()
        has_errors = False
        latitude = request.POST.get('latitude', None)
        longitude = request.POST.get('longitude', None)
        
        if not latitude:
            has_errors = True
            latitude_error = 'Latitude is required'

        if not longitude:
            has_errors = True
            longitude_error = 'Longtiude is required'
        
        if not has_errors:
            #create the graphs here and return the render and stuff
            latitude, longitude = getClosestLatLong(latitude, longitude)
            temperature_plot, precipitation_plot = create_graph(getLocID(latitude, longitude))
            context['temperature_plot'] = temperature_plot
            context['precipitation_plot'] = precipitation_plot
            print("--- %s seconds to generate---" % (time.time() - start_time))
            return render(request, 'precip_by_location/graph.html', context)
        
        messages.error(request, "Please fix errors.")
    

    
    return render(request, 'precip_by_location/graph.html', context)
