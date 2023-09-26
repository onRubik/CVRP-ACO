from controller import Controller
from model import Model


class Main:
    def run(self):
        file_name = 'ran'
        # points_name = 'ran_points_ran'
        points_name = 'perm_resize_export'
        distance_name = 'ran_dis_ran'
        n = 25
        multiplier = 200
        popSize = 100
        elite_size = 20
        mutation_rate = 0.01
        generations = 300
        plot = True
        sql = True
        con = None
        db_name = 'points.db'
        ants_n = 25
        ants_iterations = 50
        ants_alpha = 1
        ants_beta = 1
        ants_evaporation_rate = 0.5
        ants_Q = 1
        geo_name = 'export'
        reduced_size = 50
        geo_count_name = 'resize_export'
        folder_count_dir = 'output'
        geo_perm_name = 'resize_export'
        folder_perm_dir = 'output'

        newModel = Model(file_name, points_name, distance_name, n, multiplier, db_name, sql)
        newModel.imgFolder()
        con = newModel.initDb()
        points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix = newModel.dfInput()
        # newController = Controller(popSize, elite_size, mutation_rate, generations, plot, sql, con, ants_n, ants_iterations, ants_alpha, ants_beta, ants_evaporation_rate, ants_Q)
        # newController.geneticAlgorithm(points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix)
        # newModel.closeDb()

        # newModel.permGeo(geo_perm_name, folder_perm_dir)
        # newModel.getGeoORSFreeToken(env_var_name='for_chartjs')
        newModel.geoSqlUpdate(points)
        newModel.closeDb()


if __name__ == '__main__':
    newMain = Main()
    newMain.run()