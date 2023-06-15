from data_integrity import dataIntegrity
from pathlib import Path
import numpy as np
import random
import operator
import pandas as pd
import matplotlib.pyplot as plt
import math


# the genetic algorithm is based on Mr. Eric Stoltz work, for complete information please visit:
# https://towardsdatascience.com/evolution-of-a-salesman-a-complete-genetic-algorithm-tutorial-for-python-6fe5d2b3ca35


class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance


    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
    

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness= 0.0
    
    
    def routeDistance(self):
        if self.distance ==0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                fromCity = self.route[i]
                toCity = None
                if i + 1 < len(self.route):
                    toCity = self.route[i + 1]
                else:
                    toCity = self.route[0]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance

    
    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance())
        return self.fitness
    

class Controller:
    def __init__(self, file_name: str, n: int, multiplier, popSize: int, eliteSize: int, mutationRate: float, generations: int, plot: bool):
        self.file_name = file_name
        self.n = n
        self.multiplier = multiplier
        self.popSize = popSize
        self.eliteSize = eliteSize
        self.mutationRate = mutationRate
        self.generations = generations
        self.plot = plot


    def distanceXy(self, x0, y0, z0, x1, y1, z1):
        deltaX = x1 - x0
        deltaY = y1 - y0
        
        distance = math.sqrt(deltaX * deltaX + deltaY * deltaY)
        
        return distance


    def createRoute(self, cityList):
        route = random.sample(cityList, len(cityList))
        return route


    def initialPopulation(self, popSize, cityList):
        population = []

        for i in range(0, popSize):
            population.append(self.createRoute(cityList))
        return population


    def rankRoutes(self, population):
        fitnessResults = {}
        for i in range(0,len(population)):
            fitnessResults[i] = Fitness(population[i]).routeFitness()
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


    # def geneticAlgorithm(self, population, popSize, eliteSize, mutationRate, generations):
    def geneticAlgorithm(self):
        img_path, os_type = dataIntegrity.imgFolder(self)
        img_path = Path(img_path)
        img_path = img_path.parent

        if os_type == 'Windows':
            comb_input_fix = str(img_path) + '\\input\\' + 'comb_' + self.file_name + '.csv'
        if os_type == 'Linux':
            comb_input_fix = str(img_path) + '/input/' + 'comb_' + self.file_name + '.csv'

        df = pd.read_csv(comb_input_fix)
        
        population = []

        for i, row in df.iterrows():
            population.append(City(x=row['x'], y=row['y']))

        pop = self.initialPopulation(self.popSize, population)
        print("Initial distance: " + str(1 / self.rankRoutes(pop)[0][1]))
        
        for i in range(0, self.generations):
            pop = self.nextGeneration(pop, self.eliteSize, self.mutationRate)
        
        print("Final distance: " + str(1 / self.rankRoutes(pop)[0][1]))
        bestRouteIndex = self.rankRoutes(pop)[0][0]
        bestRoute = pop[bestRouteIndex]

        if self.plot:
            pop = self.initialPopulation(self.popSize, population)
            progress = []
            progress.append(1 / self.rankRoutes(pop)[0][1])

            for i in range(0, self.generations):
                pop = self.nextGeneration(pop, self.eliteSize, self.mutationRate)
                progress.append(1 / self.rankRoutes(pop)[0][1])

            plt.plot(progress)
            plt.ylabel('Distance')
            plt.xlabel('Generation')
            plt.show()

        print('bestRout = ', bestRoute)
        return bestRoute
    

    # def geneticAlgorithmPlot(self, population, popSize, eliteSize, mutationRate, generations):
    #     pop = self.initialPopulation(popSize, population)
    #     progress = []
    #     progress.append(1 / self.rankRoutes(pop)[0][1])
        
    #     for i in range(0, generations):
    #         pop = self.nextGeneration(pop, eliteSize, mutationRate)
    #         progress.append(1 / self.rankRoutes(pop)[0][1])
        
    #     plt.plot(progress)
    #     plt.ylabel('Distance')
    #     plt.xlabel('Generation')
    #     plt.show()


    def createRandomPoints(self):
        img_path, os_type = dataIntegrity.imgFolder(self)
        img_path = Path(img_path)
        img_path = img_path.parent

        if os_type == 'Windows':
            comb_input_fix = str(img_path) + '\\input\\' + 'comb_' + self.file_name + '.csv'
        if os_type == 'Linux':
            comb_input_fix = str(img_path) + '/input/' + 'comb_' + self.file_name + '.csv'

        arr = []
        for i in range(0,self.n):
            # arr.append("(" + str(int(random.random() * self.multiplier)) + "," + str(int(random.random() * self.multiplier)) + ")")
            arr.append([int(random.random() * self.multiplier), int(random.random() * self.multiplier)])
        df = pd.DataFrame(arr, columns=['x','y'])
        df.to_csv(comb_input_fix, index=False)


    # def readPoints(self):
    #     img_path, os_type = dataIntegrity.imgFolder(self)
    #     img_path = Path(img_path)
    #     img_path = img_path.parent

    #     if os_type == 'Windows':
    #         comb_input_fix = str(img_path) + '\\input\\' + 'comb_' + self.file_name + '.csv'
    #     if os_type == 'Linux':
    #         comb_input_fix = str(img_path) + '/input/' + 'comb_' + self.file_name + '.csv'

    #     arr = []

    #     for i in range(0,self.n):
    #         arr.append(City(x=int(random.random() * self.multiplier), y=int(random.random() * self.multiplier)))

    #     return arr