from controller import Controller
from model import Model


class Main:
    def run(self):
        file_name = 'ran'
        points_name = 'ran_points_ran'
        distance_name = 'ran_dis_ran'
        n = 25
        multiplier = 200
        popSize = 100
        eliteSize = 20
        mutationRate = 0.01
        generations = 10
        plot = True
        sql = False
        con = None
        db_name = 'points.db'

        newModel = Model(file_name, points_name, distance_name, n, multiplier, db_name)
        newController = Controller(popSize, eliteSize, mutationRate, generations, plot, sql, con)
        newModel.imgFolder()
        points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix = newModel.dfInput()
        newController.geneticAlgorithm(points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix)


if __name__ == '__main__':
    newMain = Main()
    newMain.run()