# chartXYgraphing
2d xy graphing using Chartjs


# Project current state
This project currently contains the backend to solve and graph a TSP problem (Traveling Salesman Problem) using a genetic algorithm & ant colony optimization (Python backend), Chartjs for the graphing component (frontend). In previous commits the project used p5js for the front end, but for the mean time it is way easier to set it up with Chartjs. The output process (backend) also saves local files with images created with matplotlib, and csv files with rather the points data, the distances and permutations or the best route created.

**Why permutations and not combinations?**
The objective is to implement this project to handle transportation and logistic operations, so in real scenario, the distance for a vehicle to move from A to B most often times won’t be the same as from B to A, why? Because of U-turns, detours, bridges, etc.


## Backend usage
The main.py in the main branch calls the necessary functions to perform an input-output process to solve the TSP problem with pre-acquired data.

The model.py file contains functions to create (x, y) data points from scratch that can be stored as a .csv file or in a relational database for later use.

An entire process can be completed using only .csv files as an input which is handled as a pandas dataframe later on to perform data query steps. **This approach is slow so it is highly advised to use an SQL engine for better performance**, this can be setup declaring the "sql" parameter as:
>sql = True

**Notice:**
- The current SQL engine tested for this project is sqlite3
- The ant colony optimization algorithm only support the sqlite3 engine at this state, the usage of a dataframe is under development

The model.py file also contains functions to update and handle the SQL database if needed.

## Frontend
No need to install any npm packages since it uses jsdelivr:
><script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

The index.html file can be opened without a server, it will ask for the “best route” csv file.


# Python
Python version in use = 3.11.4

To list current requirement:
> pip freeze requirement.txt

To install packages in requirement.txt:
> pip install -r requirement.txt
