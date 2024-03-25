def load_points(self, points):
    cur = self.con.cursor()

    for row in cur.execute('''
        select
        case
            when exists (select 1 from stage_geo_points)
            then 1
            else 0
        end
    '''):
        print(int(row[0]))

    if int(row[0]) == 1:
        cur.execute('delete from stage_geo_points')
        self.con.commit()

    points = points.drop('index', axis=1)
    points = points.set_index('id')
    points.to_sql('stage_geo_points', self.con, if_exists='append', index_label='id')
    self.con.commit()

    cur.execute('''
        insert into geo_points(id, name, coordinates, delivery_freq_per_week, pall_avg, lbs_avg)
        select *
        from stage_geo_points
        where id not in (
            select id
            from geo_points
        )
    ''')
    self.con.commit()