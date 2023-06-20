#TODO: using the class in the copilot_controller.py file, create a new class in this file that will be used to run the genetic algorithm and plot the results, both the best route and the progress of the fitness function


from copilot_controller import PilotController


class mainModel:
    def runModel(self):
        file_name = 'ran1'
        populationSize = 100
        generations = 50
        mutationRate = 0.01
        tournamentSize = 20
        multiplier = 200
        n = 25
        newController = PilotController(file_name, populationSize, generations, mutationRate, tournamentSize, multiplier, n)
        # test_population = newController.generatePopulation()
        # print(test_population)
        # newController.generatePopulation()
        # print(newController.population)
        # rankedRoutes = newController.rankRoutes()
        # print('len rankedRoutes: ', len(rankedRoutes))
        # print('Ranked Routes: ')
        # print(rankedRoutes)
        # newController.selection(rankedRoutes)
        # run the genetic algorithm and then plot the results
        progress = newController.geneticAlgorithm()
        # print the array of the best route
        print(newController.bestRoute)
        # use the plotProgress function to plot the progress of the fitness function
        newController.plotProgress(progress)
        # plot the points and lines connecting them in the best route
        newController.plotBestRoute()
        ## newController.createRandomPointsWithDistance()


if __name__ == "__main__":
    newRunModel = mainModel()
    newRunModel.runModel()


