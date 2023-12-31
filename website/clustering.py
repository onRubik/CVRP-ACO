class ClusteringService:
    def cluster_nearest_node(self, points, origin: str, max_pall: int, max_lbs: float):
        selected_columns = ['id']
        points_chosen = points_chosen[selected_columns].values
        flatten_chosen = points_chosen.flatten().astype(str)
        points_chosen_str = ', '.join([f"'{item}'" for item in flatten_chosen])

        self.cur = self.con.cursor()
        clusters = []
        discard = set()

        query_str = f"select id_2 from geo_permutations where id_1 = '{origin}' and id_2 in ({points_chosen_str}) order by distance desc"
        print(query_str)
        self.cur.execute(query_str)
        perm_rows = [row[0] for row in self.cur.fetchall()]

        for current_point in perm_rows:
            sum_pall = 0
            sum_lbs = 0
            if current_point in discard:
                continue

            sum_pall, sum_lbs = self.getGeoPointVolume(current_point)
            cluster = [current_point]
            discard.add(current_point)

            while True:
                nearest = self.getGeoNearest(current_point, origin, cluster, clusters)
                if nearest is not None:
                    pall, lbs = self.getGeoPointVolume(nearest)
                sum_pall += pall
                sum_lbs += lbs

                if sum_pall <= max_pall and sum_lbs <= max_lbs and nearest not in discard:
                    if nearest is not None:
                        cluster.append(nearest)
                    discard.add(nearest)
                    current_point = nearest
                else:
                    break

            if cluster:
                clusters.append(cluster)

        print('total clusters = ', len(clusters))
        return clusters
    

    def getGeoPointVolume(self, point_id):
        query_str = 'select pall_avg, lbs_avg from geo_points where id = ' + "'" + point_id + "'"
        self.cur.execute(query_str)
        row = self.cur.fetchone()
        pall = row[0]
        lbs = row[1]

        return float(pall), float(lbs)

    def getGeoNearest(self, point_id, origin, cluster, clusters):
        all_points = cluster + [item for sublist in clusters for item in sublist]

        all_points_set = set(all_points)

        points_str = ', '.join([f"'{item}'" for item in all_points_set])

        query_str = f"select id_2 from geo_permutations where id_1 = '{point_id}' " \
                    f"and distance = (select min(distance) from geo_permutations " \
                    f"where id_1 = '{point_id}' and id_2 not in ({points_str}) and id_2 <> '{origin}')"

        self.cur.execute(query_str)
        row = self.cur.fetchone()
        nearest = row[0] if row else None

        return nearest