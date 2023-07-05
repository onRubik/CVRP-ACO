# p5XYgraphing
2d xy graphing using p5js


# Project current state
This project currently contains the backend to solve and graph a TSP problem (Traveling Salesman Problem) using a genetic algorithm and matplotlib. The p5js frontend component is in development.


## Usage
The main.py in the main branch calls the necessary functions to perform an input-output process to solve the TSP process with pre-acquired data.

The model.py file contains functions to create (x, y) data points from scratch that can be stored as a .csv file or in a relational database for later use.

An entire process can be completed using only .csv files as an input which is handled as a pandas dataframe later on to perform data query steps. **This approach is slow so it is highly advised to use an SQL engine for better performance**, this can be setup declaring the "sql" parameter as:
>sql = True

**Notice:** The current SQL engine tested for this project is sqlite3 

The model.py file also contains functions to update and handle the SQL database if needed.


# Python
Python version in use = 3.9.16

To list current requirement:
> pip freeze requirement.txt

To install packages in requirement.txt:
> pip install -r requirement.txt
