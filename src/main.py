from controller import Controller
from model import Model


class Main:
    def run(self):
        # file_name = 'ran'
        file_name = 'geo_test_ants'
        # points_name = 'ran_points_ran'
        # points_name = 'perm_resize_export'
        points_name = 'points_resize_export'
        distance_name = 'ran_dis_ran'
        # n = 25
        n = 50
        multiplier = 200
        popSize = 100
        elite_size = 20
        mutation_rate = 0.01
        generations = 300
        # generations = 250
        # generations = 5
        plot = True
        sql = True
        con = None
        db_name = 'points.db'
        # ants_n = 25
        ants_n = 50
        ants_n_override = ants_n
        # ants_iterations = 100
        # ants_iterations = 50
        ants_iterations = 10
        # ants_iterations = 5
        # ants_iterations = 2
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
        dvrp = True
        from_clusters = True
        origin = 'way/506825578'
        max_pall = 22
        max_lbs = 38000

        newModel = Model(file_name, points_name, distance_name, n, multiplier, db_name, sql)
        newModel.imgFolder()
        con = newModel.initDb()
        # points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix = newModel.dfInput()
        points, route_output_fix, progress_output_fix, csv_output_fix, geojson_output_fix = newModel.dvrpInput()
        newController = Controller(popSize, elite_size, mutation_rate, generations, plot, sql, con, ants_n, ants_iterations, ants_alpha, ants_beta, ants_evaporation_rate, ants_Q, dvrp, from_clusters)
        # newController.geneticAlgorithm(points, combination_distance, route_output_fix, progress_output_fix, csv_output_fix)
        # _, coordinates = newController.dvrpGeneticAlgorithm(points, route_output_fix, progress_output_fix, csv_output_fix)
        # best_route_distance, _, coordinates = newController.dvrpAntColonyAlgorithm(points, route_output_fix, progress_output_fix, csv_output_fix, ants_n_override)
        # r_data = newModel.postGeojsonORSdirections(geojson_output_fix, coordinates, env_var_name='for_chartjs')
        # newModel.sqlInsertPostGeojsonORSdirections(r_data, best_route_distance)

        clusters = newController.geoSqlClusterNearestNode(origin, max_pall, max_lbs, points)
        print('\n')
        
        # file_index = 0
        all_clusters = []
        for item in clusters:
            print(item)
            ants_n_override = len(item)
            best_route_distance, df_cluster, coordinates = newController.dvrpAntColonyAlgorithm(item, route_output_fix, progress_output_fix, csv_output_fix, ants_n_override)
            print(df_cluster)
            # r_data = newModel.postGeojsonORSdirections(geojson_output_fix, coordinates, env_var_name='for_chartjs')
            # newModel.sqlInsertPostGeojsonORSdirections(r_data, best_route_distance)
            # file_index += 1

        # print(newModel.countGeoKeys(geo_count_name, folder_count_dir))
        # newModel.permGeo(geo_perm_name, folder_perm_dir)
        # newModel.pointsGeo(geo_perm_name, folder_perm_dir)

        # newModel.geoPermSqlUpdate(points)
        # newModel.geoPointsSqlUpdate(points)
        # remaining_quota = newModel.getGeoORSRateLimit(env_var_name='for_chartjs')
        # newModel.sqlGeoORSDistances(remaining_quota, env_var_name='for_chartjs')
        # newModel.getGeoORSRateLimit(env_var_name='for_chartjs')

        # newModel.freqGeoPointsSql()
        # newModel.pallLbsGeoPointsSql()

        newModel.closeDb()

        # print(newModel.countGeoKeys('resize_export','output'))


if __name__ == '__main__':
    newMain = Main()
    newMain.run()