from controller import Controller
from model import Model


class mainModel:
    def runModel(self):
        file_name = 'ran'
        points_name = 'ran_points_ran'
        distance_name = 'ran_dis_ran'
        n = 25
        multiplier = 200
        popSize = 100
        eliteSize = 20
        mutationRate = 0.01
        generations = 300
        plot = True

        newController = Controller(file_name, points_name, distance_name, n, multiplier, popSize, eliteSize, mutationRate, generations, plot)
        # newController.createRandomPointsWithDistance()
        newController.geneticAlgorithm()


if __name__ == '__main__':
    newMainModel = mainModel()
    newMainModel.runModel()