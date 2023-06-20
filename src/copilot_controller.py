#TODO: write a class that uses a genetic algorithm to solve a tsp problem, that being the traveling salesman problem, there are two csv files that are used as input, the first one contains the points as x and y coordinates which are the points available to be visited, the second one contains two columns, the first one is a tuple that conteins inner lists of the combinations of the points, the second one is the distance between the points the output is a csv file that contains the best route to visit all the points and return to the starting point


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
from itertools import permutations


class PilotController:
    def __init__(self, file_name: str, populationSize, generations, mutationRate, tournamentSize, multiplier, n: int):
        self.file_name = file_name
        self.populationSize = populationSize
        self.generations = generations
        self.mutationRate = mutationRate
        self.tournamentSize = tournamentSize
        self.multiplier = multiplier
        self.n = n
        self.population = []
        self.fitness = []
        self.bestRoute = []
        self.bestDistance = 0
        self.combination_distance = pd.DataFrame()


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


    # def fitnessFunction(self, route):
    #     distance = 0
    #     for i in range(0, len(route)):
    #         if i == len(route)-1:
    #             distance += route[i][1]
    #         else:
    #             distance += route[i][1] + route[i+1][1]
    #     return distance


    def fitnessFunction(self, route):
        distance = 0
        for i in range(len(route)-1):
            segment_distance = self.combination_distance.where((self.combination_distance['x1']==route[i][0]) & (self.combination_distance['y1']==route[i][1]) & (self.combination_distance['x2']==route[i+1][0]) & (self.combination_distance['y2']==route[i+1][1]))
            segment_distance = segment_distance.dropna()
            segment_distance = segment_distance.iloc[0, 4]
            distance += segment_distance
        
        segment_distance = self.combination_distance.where((self.combination_distance['x1']==route[-1][0]) & (self.combination_distance['y1']==route[-1][1]) & (self.combination_distance['x2']==route[0][0]) & (self.combination_distance['y2']==route[0][1]))
        segment_distance = segment_distance.dropna()
        segment_distance = segment_distance.iloc[0, 4]
        distance += segment_distance

        return distance


    def rankRoutes(self):
        self.fitness = {}
        for i in range(0, len(self.population)):
            self.fitness[i] = self.fitnessFunction(self.population[i])
        self.fitness = sorted(self.fitness.items(), key=operator.itemgetter(1), reverse=False)
        return self.fitness


    def selection(self, rankedRoutes):
        selectionResults = []
        for i in range(0, self.tournamentSize):
            selectionResults.append(rankedRoutes[i][0])
        return selectionResults
    

    def matingPool(self, selectionResults):
        matingpool = []
        for i in range(0, len(selectionResults)):
            index = selectionResults[i]
            matingpool.append(self.population[index])
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
            child = self.breed(matingpool[i], matingpool[len(matingpool)-1-i])
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
        popRanked = self.rankRoutes()
        selectionResults = self.selection(popRanked)
        matingpool = self.matingPool(selectionResults)
        children = self.breedPopulation(matingpool)
        nextGeneration = self.mutatePopulation(children)
        return nextGeneration
    

    def geneticAlgorithm(self):
        img_path, os_type = dataIntegrity.imgFolder(self)
        img_path = Path(img_path)
        img_path = img_path.parent

        if os_type == 'Windows':
            comb_input_fix = str(img_path) + '\\input\\' + 'ran_dis_' + self.file_name + '.csv'
        if os_type == 'Linux':
            comb_input_fix = str(img_path) + '/input/' + 'ran_dis_' + self.file_name + '.csv'

        self.combination_distance = pd.read_csv(comb_input_fix)

        pop = self.generatePopulation()
        progress = []
        initial_rank = self.rankRoutes()[0][1]
        progress.append(1 / initial_rank)
        print("Initial rank: " + str(1 / initial_rank))
        print("Initial distance: " + str(initial_rank))
        for i in range(0, self.generations):
            pop = self.nextGeneration(pop)
            progress.append(1 / self.rankRoutes()[0][1])
        
        print("Final rank: " + str(1 / self.rankRoutes()[0][1]))
        print("Final distance: " + str(self.rankRoutes()[0][1]))
        self.bestRoute = pop[self.rankRoutes()[0][0]]
        self.bestDistance = self.rankRoutes()[0][1]
        return progress
    

    def plotProgress(self, progress):
        plt.plot(progress)
        plt.ylabel('Distance')
        plt.xlabel('Generation')
        plt.show()


    def plotBestRoute(self):
        x = []
        y = []
        for i in range(0, len(self.bestRoute)):
            x.append(self.bestRoute[i][0])
            y.append(self.bestRoute[i][1])
        plt.plot(x, y, 'xb-')
        plt.ylabel('Y')
        plt.xlabel('X')
        plt.show()


    def createRandomPoints(self):
        img_path, os_type = dataIntegrity.imgFolder(self)
        img_path = Path(img_path)
        img_path = img_path.parent

        if os_type == 'Windows':
            comb_input_fix = str(img_path) + '\\input\\' + 'ran_' + self.file_name + '.csv'
        if os_type == 'Linux':
            comb_input_fix = str(img_path) + '/input/' + 'ran_' + self.file_name + '.csv'

        arr = []
        for i in range(0,self.n):
            arr.append([int(random.random() * self.multiplier), int(random.random() * self.multiplier)])

        df = pd.DataFrame(arr, columns=['x','y'])
        df.to_csv(comb_input_fix, index=False)

    
    def createRandomPointsWithDistance(self):
        img_path, os_type = dataIntegrity.imgFolder(self)
        img_path = Path(img_path)
        img_path = img_path.parent

        if os_type == 'Windows':
            perm_input_fix = str(img_path) + '\\input\\' + 'ran_dis_' + self.file_name + '.csv'
            points_input_fix = str(img_path) + '\\input\\' + 'ran_points_' + self.file_name + '.csv'
        if os_type == 'Linux':
            perm_input_fix = str(img_path) + '/input/' + 'ran_dis_' + self.file_name + '.csv'
            points_input_fix = str(img_path) + '/input/' + 'ran_points_' + self.file_name + '.csv'
        
        arr = []
        dist_list = []

        for i in range(0,self.n):
            arr.append([round(random.random() * self.multiplier, 6), round(random.random() * self.multiplier, 6)])
        
        df = pd.DataFrame(arr, columns=['x','y'])
        df.to_csv(points_input_fix, index=False)
        # comb = list(combinations(arr, 2))
        perm = list(permutations(arr, 2))
        for index, item in enumerate(perm):
            distance = float(math.sqrt((item[1][0] - item[0][0])**2 + ((item[1][1] - item[0][1])**2)))
            # dist_list.append([item, distance])
            dist_list.append([item[1][0], item[0][0], item[1][1], item[0][1], distance])
        
        df = pd.DataFrame(dist_list, columns=['x2', 'x1', 'y2', 'y1','distance'])
        df.to_csv(perm_input_fix, index=False)