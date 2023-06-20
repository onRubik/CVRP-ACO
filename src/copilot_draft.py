#TODO: write a class that uses a genetic algorithm to solve a tsp problem (traveling salesman problem), the input of points is a csv file that includes two columns, the first one is a tuple that conteins inner lists of the combinations of the points, the second one is the distance between the points, a second csv file could be used if it speeds up the process to read the available points, containing only the points that are available to be visited, the output is a csv file that contains the best route to visit all


from data_integrity import dataIntegrity
from pathlib import Path
import numpy as np
import random
import operator
import pandas as pd
import matplotlib.pyplot as plt
import math
import csv
from itertools import combinations


class PilotController:
    def __init__(self, file_name: str, populationSize, generations, mutationRate, tournamentSize):
        self.file_name = file_name
        self.populationSize = populationSize
        self.generations = generations
        self.mutationRate = mutationRate
        self.tournamentSize = tournamentSize
        self.population = []
        self.fitness = []
        self.bestRoute = []
        self.bestDistance = 0


    def generatePopulation(self):
        img_path, os_type = dataIntegrity.imgFolder(self)
        img_path = Path(img_path)
        img_path = img_path.parent

        if os_type == 'Windows':
            comb_input_fix = str(img_path) + '\\input\\' + 'ran_dis_' + self.file_name + '.csv'
            points_input_fix = str(img_path) + '\\input\\' + 'ran_points_' + self.file_name + '.csv'
        if os_type == 'Linux':
            comb_input_fix = str(img_path) + '/input/' + 'ran_dis_' + self.file_name + '.csv'
            points_input_fix = str(img_path) + '/input/' + 'ran_points_' + self.file_name + '.csv'

        # read the csv file that contains the points into a list and convert the strings to floats rounded to six decimals
        with open(points_input_fix, 'r') as f:
            reader = csv.reader(f)
            points = list(reader)

        points = [[round(float(j), 6) for j in i] for i in points[1:]]
        self.points = points

        for i in range(0, self.populationSize):
            self.population.append(random.sample(self.points, len(self.points)))
        return self.population


    def fitnessFunction(self, route):
        distance = 0
        for i in range(0, len(route)):
            if i == len(route)-1:
                distance += route[i][1]
            else:
                distance += route[i][1] + route[i+1][1]
        return distance


    def rankRoutes(self):
        fitnessResults = {}
        for i in range(0, len(self.population)):
            fitnessResults[i] = self.fitnessFunction(self.population[i])
        return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = False)


    def selection(self, rankedRoutes):
        selectionResults = []
        df = pd.DataFrame(np.array(rankedRoutes), columns=["Index","Fitness"])
        df['cum_sum'] = df.Fitness.cumsum()
        df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
        for i in range(0, self.tournamentSize):
            selectionResults.append(self.population[rankedRoutes[i][0]])
        return selectionResults


    def matingPool(self, selectionResults):
        matingpool = []
        for i in range(0, len(selectionResults)):
            matingpool.append(selectionResults[i])
        return matingpool


    def breed(self, parent1, parent2):
        child = []
        childP1 = []
        childP2 = []
        geneA = int(random.random() * len(parent1))
        geneB = int(random.random() * len(parent1))
        startGene = min(geneA, geneB)
        endGene = max(geneA, geneB)
        for i in range(startGene, endGene):
            childP1.append(parent1[i])
        childP2 = [item for item in parent2 if item not in childP1]
        child = childP1 + childP2
        return child
    

    def breedPopulation(self, matingpool):
        children = []
        for i in range(0, len(matingpool)):
            child = self.breed(matingpool[i], matingpool[len(matingpool)-i-1])
            children.append(child)
        return children
    

    def mutate(self, individual):
        for swapped in range(len(individual)):
            if(random.random() < self.mutationRate):
                swapWith = int(random.random() * len(individual))
                city1 = individual[swapped]
                city2 = individual[swapWith]
                individual[swapped] = city2
                individual[swapWith] = city1
        return individual
    

    def mutatePopulation(self, population):
        mutatedPop = []
        for ind in range(0, len(population)):
            mutatedInd = self.mutate(population[ind])
            mutatedPop.append(mutatedInd)
        return mutatedPop
    

    def nextGeneration(self, currentGen):
        rankedRoutes = self.rankRoutes()
        selectionResults = self.selection(rankedRoutes)
        matingpool = self.matingPool(selectionResults)
        children = self.breedPopulation(matingpool)
        nextGeneration = self.mutatePopulation(children)
        return nextGeneration
    

    def geneticAlgorithm(self):
        pop = self.generatePopulation()
        progress = []
        progress.append(1 / self.rankRoutes()[0][1])
        print("Initial distance: " + str(1 / self.rankRoutes()[0][1]))
        for i in range(0, self.generations):
            pop = self.nextGeneration(pop)
            progress.append(1 / self.rankRoutes()[0][1])
        print("Final distance: " + str(1 / self.rankRoutes()[0][1]))
        self.bestRoute = self.rankRoutes()[0][0]
        # print the array of the best route
        print(self.population[self.bestRoute])
        # plot the points and lines connecting them in the best route
        plt.plot([i[0] for i in self.population[self.bestRoute]], [i[1] for i in self.population[self.bestRoute]], 'xb-')
        plt.show()
        self.bestDistance = 1 / self.rankRoutes()[0][1]
        print("Best Route: " + str(self.bestRoute))
        print("Best Distance: " + str(self.bestDistance))
        plt.plot(progress)
        plt.ylabel('Distance')
        plt.xlabel('Generation')
        plt.show()
        
        return self.bestRoute, self.bestDistance, progress
        