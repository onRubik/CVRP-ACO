from model import Model
from pathlib import Path
import numpy as np
import random
import operator
import pandas as pd
import matplotlib.pyplot as plt
import math
from itertools import permutations
import csv
from tqdm import trange


class Controller:
    def __init__(self, popSize: int, eliteSize: int, mutationRate: float, generations: int, plot: bool, sql: bool, con, db_path):
        self.popSize = popSize
        self.eliteSize = eliteSize
        self.mutationRate = mutationRate
        self.generations = generations
        self.plot = plot
        self.combination_distance = pd.DataFrame()
        self.sql = sql
        self.con = con
        self.db_path = db_path


    def createRoute(self, cityList):
        route = random.sample(cityList, len(cityList))
        return route


    def initialPopulation(self, popSize, cityList):
        population = []

        for i in range(0, popSize):
            population.append(self.createRoute(cityList))
        return population
    

    def dfFitnessFunction(self, route):
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
    

    def sqlFitnessFunction(self, route):
        perm = str()


    def rankRoutes(self, population):
        fitnessResults = {}
        for i in range(0,len(population)):
            if not self.sql:
                fitnessResults[i] = 1 / float(self.dfFitnessFunction(population[i]))
            if self.sql:
                fitnessResults[i] = 1 / float(self.sqlFitnessFunction(population[i]))

        return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)


    def selection(self, popRanked, eliteSize):
        selectionResults = []
        df = pd.DataFrame(np.array(popRanked), columns=["Index","Fitness"])
        df['cum_sum'] = df.Fitness.cumsum()
        df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
        
        for i in range(0, eliteSize):
            selectionResults.append(popRanked[i][0])
        for i in range(0, len(popRanked) - eliteSize):
            pick = 100*random.random()
            for i in range(0, len(popRanked)):
                if pick <= df.iat[i,3]:
                    selectionResults.append(popRanked[i][0])
                    break
        return selectionResults


    def matingPool(self, population, selectionResults):
        matingpool = []
        for i in range(0, len(selectionResults)):
            index = selectionResults[i]
            matingpool.append(population[index])
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


    def breedPopulation(self, matingpool, eliteSize):
        children = []
        length = len(matingpool) - eliteSize
        pool = random.sample(matingpool, len(matingpool))

        for i in range(0,eliteSize):
            children.append(matingpool[i])
        
        for i in range(0, length):
            child = self.breed(pool[i], pool[len(matingpool)-i-1])
            children.append(child)
        return children


    def mutate(self, individual, mutationRate):
        for swapped in range(len(individual)):
            if(random.random() < mutationRate):
                swapWith = int(random.random() * len(individual))
                
                city1 = individual[swapped]
                city2 = individual[swapWith]
                
                individual[swapped] = city2
                individual[swapWith] = city1
        return individual


    def mutatePopulation(self, population, mutationRate):
        mutatedPop = []
        
        for ind in range(0, len(population)):
            mutatedInd = self.mutate(population[ind], mutationRate)
            mutatedPop.append(mutatedInd)
        return mutatedPop


    def nextGeneration(self, currentGen, eliteSize, mutationRate):
        popRanked = self.rankRoutes(currentGen)
        selectionResults = self.selection(popRanked, eliteSize)
        matingpool = self.matingPool(currentGen, selectionResults)
        children = self.breedPopulation(matingpool, eliteSize)
        nextGeneration = self.mutatePopulation(children, mutationRate)
        return nextGeneration


    def geneticAlgorithm(self, points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix):
        progress = []
        self.combination_distance = combination_distance
        pop = self.initialPopulation(self.popSize, points)
        initial_distance = 1 / self.rankRoutes(pop)[0][1]
        print("Initial distance: " + str(initial_distance))
        
        for i in trange(0, self.generations):
            pop = self.nextGeneration(pop, self.eliteSize, self.mutationRate)
            progress.append(1 / self.rankRoutes(pop)[0][1])
        
        print("Final distance: " + str(1 / self.rankRoutes(pop)[0][1]))
        bestRouteIndex = self.rankRoutes(pop)[0][0]
        bestRoute = pop[bestRouteIndex]
        bestRoute = bestRoute + [bestRoute[0]]
        x = [item[0] for item in bestRoute]
        y = [item[1] for item in bestRoute]
        df = pd.DataFrame(columns=['x','y'])
        df['x'] = x
        df['y'] = y
        df.to_csv(csv_output_fix, index=False)

        if self.plot:
            plt.plot(progress)
            plt.ylabel('Distance')
            plt.xlabel('Generation')
            plt.savefig(progress_output_fix)
            plt.show()

            plt.plot(x,y,'o-', label='Cordinates')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.savefig(route_output_fix)
            plt.show()
                
        print('bestRoute = ', bestRoute)
        return bestRoute