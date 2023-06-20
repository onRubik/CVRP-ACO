from copilot_draft import PilotController


class mainModel:
    def runModel(self):
        file_name = 'ran1'
        populationSize = 100
        generations = 300
        mutationRate = 0.01
        tournamentSize = 20
        newController = PilotController(file_name, populationSize, generations, mutationRate, tournamentSize)
        # test_population = newController.generatePopulation()
        # print(test_population)
        # newController.generatePopulation()
        # print(newController.population)
        # rankedRoutes = newController.rankRoutes()
        # print('len rankedRoutes: ', len(rankedRoutes))
        # print('Ranked Routes: ')
        # print(rankedRoutes)
        # newController.selection(rankedRoutes)
        newController.geneticAlgorithm()


if __name__ == "__main__":
    newRunModel = mainModel()
    newRunModel.runModel()

