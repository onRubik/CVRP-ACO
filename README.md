#  CVRP-ACO
Graphing vehicle routes using plotly.graph_objects and openrouteservice API.


#  Project current state
This project currently contains the backend to solve a CVRP problem (Constrained Vehicle Routing Problem) using an ACO algorithm (Ant Colony Optimization). A plotly.graph_objects.Scattermapbox ('style':  "open-street-map") as graphing and frontend component.


**Why permutations and not combinations?**
The objective is to implement this project to handle transportation and logistic operations. In a real scenario the distance for a vehicle to move from A to B most often times won’t be the same as from B to A, why? Because of U-turns, detours, bridges, etc.


##  Backend usage

**utils.py file functions:**
-  **ETL steps to get raw geojson data and prepare to be solved by the ACO algorithm.**

**cdvrp.py file functions:**
-  **Solves CVRP problem and load routes data.**  

The main.py file starts a Flask service to load and display the solved routes in street maps.

**Notice:**
- Usage of a relational database is intended to store input/output data.
- The current SQL engine tested for this project is sqlite3.


##  Frontend
"Load Points" will load a solution set. This set must be completed before hand using both utils.py & cdvrp.py.

"File" option can be used to load manually a set from a csv file.


#  Geo data
If you want to get real coordinates you can use https://overpass-turbo.eu/

For example, you can query points with a “park” description around 70 km from Dallas City:

```
[out:json][timeout:25];
(
node["leisure"="park"](around:70000,32.7767,-96.7970);
way["leisure"="park"](around:70000,32.7767,-96.7970);
relation["leisure"="park"](around:70000,32.7767,-96.7970);
);
out center;
```


Both utils.py & Flask service uses https://openrouteservice.org/ API to get the distance between permutations of the points. You will need to set your api key as an environment variable like:

>export ORS_API_KEY="your api key"

Currently the API is meant to use the openrouteservice free token so it's fixed to get less than 2000 requests per day and with a delay time of 40 per minute.


#  Python

Python version in use = 3.11.4

To list current requirement:
> pip freeze requirement.txt

To install packages in requirement.txt:
> pip install -r requirement.txt
