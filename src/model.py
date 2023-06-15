from controller import Controller


class mainModel:
    def runModel(self):
        file_name = 'ran1'
        n = 25
        multiplier = 200
        popSize = 100
        eliteSize = 20
        mutationRate = 0.01
        generations = 300
        plot = True

        newController = Controller(file_name, n, multiplier, popSize, eliteSize, mutationRate, generations, plot)
        newController.geneticAlgorithm()
        pass


if __name__ == '__main__':
    newMainModel = mainModel()
    newMainModel.runModel()