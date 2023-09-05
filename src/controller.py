import numpy as np
import random
import operator
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import trange


class Controller:
    def __init__(self, popSize: int, elite_size: int, mutation_rate: float, generations: int, plot: bool, sql: bool, con, ants_n, ants_iterations, ants_alpha, ants_beta, ants_evaporation_rate, ants_Q):
        self.popSize = popSize
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.plot = plot
        self.combination_distance = None
        self.sql = sql
        self.con = con
        self.cur = None
        self.ants_n = ants_n
        self.ants_iterations = ants_iterations
        self.ants_alpha = ants_alpha
        self.ants_beta = ants_beta
        self.ants_evaporation_rate = ants_evaporation_rate
        self.ants_Q = ants_Q


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
        distance = 0
        for i in range(len(route)-1):
            query_str = 'select distance from permutation_distance where x1 = '+str(route[i][0])+' and y1 = '+str(route[i][1])+' and x2 = '+str(route[i+1][0])+' and y2 = '+str(route[i+1][1])
            for row in self.cur.execute(query_str):
                segment_distance = row[0]
            distance += segment_distance

        query_str = 'select distance from permutation_distance where x1 = '+str(route[-1][0])+' and y1 = '+str(route[-1][1])+' and x2 = '+str(route[0][0])+' and y2 = '+str(route[0][1])
        for row in self.cur.execute(query_str):
            segment_distance = row[0]
        distance += segment_distance

        return distance


    def rankRoutes(self, population):
        fitnessResults = {}
        for i in range(0,len(population)):
            if not self.sql:
                fitnessResults[i] = 1 / float(self.dfFitnessFunction(population[i]))
            if self.sql:
                fitnessResults[i] = 1 / float(self.sqlFitnessFunction(population[i]))

        return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)


    def selection(self, popRanked, elite_size):
        selectionResults = []
        df = pd.DataFrame(np.array(popRanked), columns=["Index","Fitness"])
        df['cum_sum'] = df.Fitness.cumsum()
        df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
        
        for i in range(0, elite_size):
            selectionResults.append(popRanked[i][0])
        for i in range(0, len(popRanked) - elite_size):
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


    def breedPopulation(self, matingpool, elite_size):
        children = []
        length = len(matingpool) - elite_size
        pool = random.sample(matingpool, len(matingpool))

        for i in range(0,elite_size):
            children.append(matingpool[i])
        
        for i in range(0, length):
            child = self.breed(pool[i], pool[len(matingpool)-i-1])
            children.append(child)
        return children


    def mutate(self, individual, mutation_rate):
        for swapped in range(len(individual)):
            if(random.random() < mutation_rate):
                swapWith = int(random.random() * len(individual))
                
                city1 = individual[swapped]
                city2 = individual[swapWith]
                
                individual[swapped] = city2
                individual[swapWith] = city1
        return individual


    def mutatePopulation(self, population, mutation_rate):
        mutatedPop = []
        
        for ind in range(0, len(population)):
            mutatedInd = self.mutate(population[ind], mutation_rate)
            mutatedPop.append(mutatedInd)
        return mutatedPop


    def nextGeneration(self, currentGen, elite_size, mutation_rate):
        popRanked = self.rankRoutes(currentGen)
        selectionResults = self.selection(popRanked, elite_size)
        matingpool = self.matingPool(currentGen, selectionResults)
        children = self.breedPopulation(matingpool, elite_size)
        nextGeneration = self.mutatePopulation(children, mutation_rate)
        return nextGeneration


    def geneticAlgorithm(self, points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix):
        if self.sql:
            self.cur = self.con.cursor()
            selected_columns = ['x', 'y']
            points = points[selected_columns].values
            selected_df = pd.DataFrame(points, columns=selected_columns)
            array_string = selected_df.to_string(index=False, header=False)
            points = [line.split() for line in array_string.split('\n') if line]
            for item in points:
                item[0] = round(float(item[0]), 6)
                item[1] = round(float(item[1]), 6)

        progress = []
        if self.sql == False:
            self.combination_distance = combination_distance
        pop = self.initialPopulation(self.popSize, points)
        initial_distance = 1 / self.rankRoutes(pop)[0][1]
        print("Initial distance: " + str(initial_distance))
        
        for i in trange(0, self.generations):
            pop = self.nextGeneration(pop, self.elite_size, self.mutation_rate)
            progress.append(1 / self.rankRoutes(pop)[0][1])
        
        print("Final distance: " + str(1 / self.rankRoutes(pop)[0][1]))
        best_route_index = self.rankRoutes(pop)[0][0]
        best_route = pop[best_route_index]
        best_route = best_route + [best_route[0]]
        x = [item[0] for item in best_route]
        y = [item[1] for item in best_route]
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
                
        print('best_route = ', best_route)
        return best_route
    

    def antColonyAlgorithm(self, points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix):
        points_len = len(points)
        points_copy = points.copy()
        pheromone = np.ones((points_len, points_len))
        best_route = []
        best_route_distance = np.inf

        if self.sql:
            self.cur = self.con.cursor()
            selected_columns = ['x', 'y']
            points = points[selected_columns].values
            selected_df = pd.DataFrame(points, columns=selected_columns)
            array_string = selected_df.to_string(index=False, header=False)
            points = [line.split() for line in array_string.split('\n') if line]
            for item in points:
                item[0] = round(float(item[0]), 6)
                item[1] = round(float(item[1]), 6)

        progress = []
        if self.sql == False:
            self.combination_distance = combination_distance

        for i in trange(0, self.ants_iterations):
            routes = []
            routes_len = []

            for i in range(self.ants_n):
                visited = [False] * points_len
                current_point = np.random.randint(points_len)
                visited[current_point] = True
                route = [current_point]
                route_len = 0

                while False in visited:
                    unvisited = np.where(np.logical_not(visited))[0]
                    odds = np.zeros(len(unvisited))

                    for i, item in enumerate(unvisited):
                        segment_distance = self.antsDistance(points, current_point, item, next_point=False)

                        odds[i] = pheromone[current_point, item] ** self.ants_alpha / (segment_distance ** self.ants_beta)

                    odds /= np.sum(odds)
                    next_point = np.random.choice(unvisited, p=odds)
                    route.append(next_point)
                    route_len += self.antsDistance(points, current_point, item, next_point)
                    visited[next_point] = True
                    current_point = next_point

                route = route + [route[0]]
                route_len += self.antsReturnDistance(points_copy, route)
                routes.append(route)
                routes_len.append(route_len)

                if route_len < best_route_distance:
                    best_route = route
                    best_route_distance = np.sum(route_len)
                
                progress.append(best_route_distance)
            
            pheromone *= self.ants_evaporation_rate

            for route_zip, route_len_zip in zip(routes, routes_len):
                for i in range(points_len-1):
                    pheromone[route_zip[i], route_zip[i + 1]] += self.ants_Q / route_len_zip
                pheromone[route_zip[-1], route_zip[0]] += self.ants_Q / route_len_zip

        from_df = []
        for i in range(points_len+1):
            from_df.append(points_copy.loc[best_route[i], ['x', 'y']])
        
        x = [item[0] for item in from_df]
        y = [item[1] for item in from_df]
        df = pd.DataFrame(columns=['x','y'])
        df['x'] = x
        df['y'] = y
        df.to_csv(csv_output_fix, index=False)

        if self.plot:
            plt.plot(progress)
            plt.ylabel('Distance')
            plt.xlabel('Iterations')
            plt.savefig(progress_output_fix)
            plt.show()

            plt.plot(x,y,'o-', label='Cordinates')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.savefig(route_output_fix)
            plt.show()
        
        print("Final distance: " + str(best_route_distance))
        print('best_route = ', from_df)
        return from_df


    def antsDistance(self, points, current_point, item, next_point):
        if next_point == False:
            point_state = item
        else:
            point_state = next_point

        query_str = 'select distance from permutation_distance where x1 = '+str(points[current_point][0])+' and y1 = '+str(points[current_point][1])+' and x2 = '+str(points[point_state][0])+' and y2 = '+str(points[point_state][1])

        for row in self.cur.execute(query_str):
            segment_distance = row[0]
        
        return segment_distance
    

    def antsReturnDistance(self, points_copy, route):
        query_str = 'select distance from permutation_distance where x1 = '+str(points_copy.loc[route[-2], ['x']].iloc[0])+' and y1 = '+str(points_copy.loc[route[-2], ['y']].iloc[0])+' and x2 = '+str(points_copy.loc[route[-1], ['x']].iloc[0])+' and y2 = '+str(points_copy.loc[route[-1], ['y']].iloc[0])

        for row in self.cur.execute(query_str):
            segment_distance = row[0]
        
        return segment_distance