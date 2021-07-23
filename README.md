# osm-travel
    
Compute travel distances and durations using OpenStreetMaps API
----
1) Coordinates from address with [nominatim](https://nominatim.org/release-docs/develop/api/Overview/)

2) Fastest Route with [OSRM](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md)
       
Usage:
------
Given a csv file with two columns of start and destination adresses, adds columns with the travel time and distance by car.

    python osm_travel.py my_cities.csv
    
   
