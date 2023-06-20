from controller import Controller


class mainModel:
    def runModel(self):
        file_name = 'ran1'
        points_name = 'ran1'
        distance_name = 'ran1'
        n = 25
        multiplier = 200
        popSize = 100
        eliteSize = 20
        mutationRate = 0.01
        generations = 300
        plot = True
        pre_distance_calc = False

        newController = Controller(file_name, points_name, distance_name, n, multiplier, popSize, eliteSize, mutationRate, generations, plot, pre_distance_calc)
        newController.geneticAlgorithm()
        # newController.createRandomPointsWithDistance()
        pass


if __name__ == '__main__':
    newMainModel = mainModel()
    newMainModel.runModel()