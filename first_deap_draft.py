import random
import numpy as np
from deap import base, creator, tools, algorithms

# Define the fitness function for the TSP
def tsp_fitness(individual):
    total_distance = 0
    for i in range(len(individual) - 1):
        city1 = individual[i]
        city2 = individual[i + 1]
        distance = np.linalg.norm(city1 - city2)
        total_distance += distance
    # Add distance from last city to the first city
    total_distance += np.linalg.norm(individual[-1] - individual[0])
    return total_distance,

def main():
    # Create the TSP problem
    tsp_creator = creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    individual_creator = creator.create("Individual", list, fitness=tsp_creator)

    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(len(coordinates)), len(coordinates))
    toolbox.register("individual", tools.initIterate, individual_creator, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxPartialyMatched)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", tsp_fitness)

    random.seed(42)
    population_size = 100
    num_generations = 100

    # Generate the initial population
    population = toolbox.population(n=population_size)

    # Evolve the population
    for generation in range(num_generations):
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.2)
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=population_size)

    best_solution = tools.selBest(population, k=1)[0]
    best_distance = tsp_fitness(best_solution)[0]

    print("Best solution:", best_solution)
    print("Best distance:", best_distance)

if __name__ == "__main__":
    # Example input - a set of 2D coordinates
    coordinates = np.array([(0, 0), (1, 2), (3, 1), (5, 4), (2, 7)])

    main()
