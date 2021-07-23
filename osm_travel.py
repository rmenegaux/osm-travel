'''
Compute travel distances and durations using OpenStreetMaps API
----
1) Coordinates from address with nominatim
https://nominatim.org/release-docs/develop/api/Overview/

2) Fastest Route with OSRM
https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md
'''

import urllib.request
import json
import datetime
import sys

import pandas as pd

def get_coordinates_from_address(address):
    '''
    Returns latitude and longitude from a query, using the nominatim tool
    '''
    formatted_address = address.replace(' ', '+')
    url_request = 'http://nominatim.openstreetmap.org/search?q={}&format=json&polygon=1&addressdetails=1'.format(formatted_address)
    with urllib.request.urlopen(url_request) as response:
        html = response.read()
    location_info = json.loads(html)[0]
    print(location_info['display_name'])
    return float(location_info['lon']), float(location_info['lat'])


def get_fastest_route_coords(start_coordinates, dest_coordinates, travel_type='driving'):
    '''
    Finds the fastest route between coordinates in the supplied order.
    
    url structure:
    GET /route/v1/{profile}/{coordinates}?alternatives={true|false|number}&steps={true|false}&geometries={polyline|polyline6|geojson}&overview={full|simplified|false}&annotations={true|false}
    '''
    url_request = 'http://router.project-osrm.org/route/v1/{}/{:.6f},{:.6f};{:.6f},{:.6f}?overview=false'.format(
        travel_type, *start_coordinates, *dest_coordinates
    )
    with urllib.request.urlopen(url_request) as response:
        html = response.read()
    routes = json.loads(html)['routes'][0]
    # print(json.loads(html))
    return {'distance': routes['distance'], 'duration': routes['duration']}

def get_fastest_route(start_address, dest_address):
    '''
    Returns the driving duration and distance between two addresses
    '''
    start_coords = get_coordinates_from_address(start_address)
    dest_coords = get_coordinates_from_address(dest_address)
    
    route = get_fastest_route_coords(start_coords, dest_coords)
    distance = route['distance']/1000
    duration = datetime.timedelta(seconds=route['duration'])
    print('''
          Distance: {:.1f}km
          Time    : {}
          '''.format(distance, duration)
         )
    return {'distance': distance, 'duration': duration}


def compute_routes_csv(
    itineraries_file_name,
    distance_col='distance (km)',
    duration_col='duration',
    save_inplace=True,
    sep=','):
    '''
    Given a csv file with two columns of start and destination adresses,
    adds columns with the travel time and distance by car.
    
    If `save_inplace` is True (default), modifies the csv inplace, otherwise 
    creates a new csv file.
    '''
    itineraries = pd.read_csv(itineraries_file_name, sep=sep)
    print(itineraries.head())
    # itineraries = itineraries.loc[:, itineraries.columns[:2]]
    distances_durations = [
        get_fastest_route(start, dest) for start, dest in zip(
            itineraries.iloc[:, 0], itineraries.iloc[:, 1])
    ]
    itineraries['duration'] = [d['duration'] for d in distances_durations]
    itineraries['distance (km)'] = [d['distance'] for d in distances_durations]
    
    # Save the results as a csv
    results_file_name = itineraries_file_name if save_inplace else itineraries_file_name + '_travel'
    itineraries.to_csv(itineraries_file_name, index=False)
    print('Saved results to {}'.format(itineraries_file_name))
    
    return itineraries

__help__ = '''
    Usage:
    ------
    python osm_travel.py my_cities.csv
    
    Description:
    ------------
    Given a csv file with two columns of start and destination adresses,
        adds columns with the travel time and distance by car.
'''

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__help__)
    else:
        compute_routes_csv(sys.argv[1])
