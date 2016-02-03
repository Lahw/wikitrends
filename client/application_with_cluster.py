from flask import Flask, render_template, request
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
import os
import csv
import re
application = Flask(__name__)


def cleaner(name):
    black_list = ['Main_Page', '404_error', 'Special:Random', 'Wikipedia:Hauptseite', 'Wikipedia:Portada', 'Special:AutoLogin', 'Spezial:Suche',
                  'Spezial:Search', 'Portal:Huvudsida', 'Spezial:Zuf%C3%A4llige_Seite', 'index.html', 'Wikipedia:P%C3%A1gina_principal', 'w/index.php',
                  'Special:Watchlist', 'Special:Search', 'Main20Page', 'Pagina_principale', 'A9diaAccueil_principal', 'Hauptseite', 'Hoofdpagina', 'C3B3wna',
                  'C3A1gina_principal', 'Accueil_principal', 'P%C3%A1gina_principal', 'Strona_g%C5%82%C3%B3wna', 'Search']

    min_length = 3
    pattern = re.compile(r'(%[A-Z0-9][A-Z0-9]){1}')
    if name in black_list or len(name) < min_length or pattern.match(name):
        return None
    name = re.split(':|/', name)
    if len(name) <= 3:
        name = name[-1]
    else:
        name = name[-2] + name[-1]
    if name in black_list or pattern.match(name):
        return None
    return name


cluster = Cluster(['54.88.108.226'])
session = cluster.connect()
session.row_factory = dict_factory

# Param
nb_pages = 10


@application.route('/')
@application.route('/index')
def index():
    path_to_data = 'static/data/'
    default_date = 'Exemple: 2011-01-31'
    if request.args.get('date'):
        date_string = str(request.args.get('date'))
        default_date = date_string
        for mode in ['24hours', '30days']:
            if mode == '24hours':
                prefix = 'h'
            else:
                prefix = 'd'
            dict_piechart = []
            dict_linechart = []
            query = "SELECT * FROM wiki.trends_" + mode + " WHERE date_time = '" + date_string + \
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
                    dict_piechart.append({'category': clean_name, 'measure': int(raw['n_view'])})
                    range_indices = range(24) if mode == '24hours' else range(30)
                    for indice in range_indices:
                        indice_string = str(indice) if indice >= 10 else "0" + str(indice)
                        dict_linechart.append({'category': int(indice_string), 'group': clean_name, 'measure': int(raw[prefix + indice_string])})
                        if not prefix + indice_string in sum_view_per_hour.keys():
                            sum_view_per_hour[prefix + indice_string] = int(raw[prefix + indice_string])
                        else:
                            sum_view_per_hour[prefix + indice_string] += int(raw[prefix + indice_string])
                    sum_view += raw['n_view']
                    cpt += 1

            if dict_piechart != []:
                dict_piechart = [{'category': 'All', 'measure': sum_view}] + dict_piechart

                with open(os.path.join(application.root_path, path_to_data + 'data' + mode + '_piechart.csv'), 'wb') as f:
                    w = csv.DictWriter(f, dict_piechart[0].keys())
                    w.writeheader()
                    for row in dict_piechart:
                        w.writerow(row)

            if dict_linechart != []:
                sorted_keys = sum_view_per_hour.keys()
                sorted_keys.sort()
                dict_linechart = [{'category': int(key[1:]), 'group': 'All', 'measure': sum_view_per_hour[key]} for key in sorted_keys] + dict_linechart

                with open(os.path.join(application.root_path, path_to_data + 'data' + mode + '_linechart.csv'), 'wb') as f:
                    w = csv.DictWriter(f, dict_linechart[0].keys())
                    w.writeheader()
                    for row in dict_linechart:
                        w.writerow(row)

    return render_template('index.html', default_date=default_date)


if __name__ == '__main__':
    application.run(debug=True)
