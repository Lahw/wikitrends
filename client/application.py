from flask import Flask, render_template, request
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
import os
import csv
import re
application = Flask(__name__)


def cleaner(name):
    black_list = ['Main_Page', '404_error', 'AutoLogin', 'Search', 'Suche', 'Hauptseite', 'Huvudsida',
                  'Specjalna:Szukaj', 'Watchlist', 'index.html', 'Wikipedia:P%C3%A1gina_principal']
    min_length = 3
    pattern = re.compile(r'(%[A-Z0-9][A-Z0-9]){4}')
    if name in black_list or len(name) < min_length or pattern.match(name):
        return None
    name = re.findall(r"[\w']+", name)
    if len(name) < 2:
        name = name[len(name) - 1]
    else:
        name = name[-2] + name[-1]
    return name

cluster = Cluster(['54.88.108.226'])
session = cluster.connect()
session.row_factory = dict_factory

# Param
black_list = ['Main_Page', 'Special:Search', '%']
min_length = 3
pattern = re.compile(r'(%[A-Z\d][A-Z\d]){4}')
nb_pages = 10


@application.route('/')
@application.route('/index')
def index():
    path_to_data = 'static/data/'
    if request.args.get('date'):
        date_string = str(request.args.get('date'))

        ##########
        # 24 hours
        ##########
        dict24hours_piechart = []
        dict24hours_linechart = []
        query = "SELECT * FROM wiki.trends_24hours WHERE date_time = '" + date_string + \
                "' ORDER BY n_view DESC LIMIT 50;"
        raws = session.execute(query)
        sum_view = 0.
        sum_view_per_hour = {}
        cpt = 0
        for raw in raws:
            if cpt >= nb_pages:
                break
            clean_name = cleaner(raw['name'])
            if clean_name is not None:
                dict24hours_piechart.append({'category': clean_name, 'measure': int(raw['n_view'])})
                for hour in range(24):
                    hour_string = str(hour) if hour >= 10 else "0" + str(hour)
                    dict24hours_linechart.append({'category': int(hour_string), 'group': clean_name, 'measure': int(raw['h' + hour_string])})
                    if not 'h' + hour_string in sum_view_per_hour.keys():
                        sum_view_per_hour['h' + hour_string] = int(raw['h' + hour_string])
                    else:
                        sum_view_per_hour['h' + hour_string] += int(raw['h' + hour_string])
                sum_view += raw['n_view']
                cpt += 1

        dict24hours_piechart = [{'category': 'All', 'measure': sum_view}] + dict24hours_piechart
        sorted_keys = sum_view_per_hour.keys()
        sorted_keys.sort()
        dict24hours_linechart = [{'category': int(key[1:]), 'group': 'All', 'measure': sum_view_per_hour[key]} for key in sorted_keys] + dict24hours_linechart

        with open(os.path.join(application.root_path, path_to_data + 'data24hours_piechart.csv'), 'wb') as f:
            w = csv.DictWriter(f, dict24hours_piechart[0].keys())
            w.writeheader()
            for row in dict24hours_piechart:
                w.writerow(row)

        with open(os.path.join(application.root_path, path_to_data + 'data24hours_linechart.csv'), 'wb') as f:
            w = csv.DictWriter(f, dict24hours_linechart[0].keys())
            w.writeheader()
            for row in dict24hours_linechart:
                w.writerow(row)

    ############
    ## 30 days
    ############
    # Compute all dates
        # from datetime import datetime, timedelta
        # import pandas as pd
        # date_min = datetime.strptime('2011-01-01', '%Y-%m-%d')
        # date_max = datetime.strptime(date_string, '%Y-%m-%d')
        # date_minus30days = max(date_max - timedelta(days=30), date_min)
        # delta = date_max - date_minus30days

        # all_dates_string = '('
        # for i in range(delta.days + 1):
        #     all_dates_string += "'" + str(date_minus30days + timedelta(days=i))[:10] + "',"
        # all_dates_string = all_dates_string[:-1] + ')'

        # dict30days_piechart = []
        # dict30days_linechart = []
        # query = "SELECT * FROM wiki.trends_24hours WHERE date_time IN " + all_dates_string + \
        #         " AND n_view > 100000;"
        # df_30hours = pd.DataFrame()
        # raws = session.execute(query)
        # for raw in raws:
        #     df_30hours = df_30hours.append(raw, ignore_index=True)
        # df_30hours.groupby('name')['n_view'].sum().reset_index().sort_values('n_view', ascending=False)[:10]
    return render_template('index.html')

if __name__ == '__main__':
    application.run(debug=True)
