from flask import Flask, render_template, request
application = Flask(__name__)

from cassandra.cluster import Cluster
import datetime
import os
import csv
cluster = Cluster(['54.165.225.67'])
session = cluster.connect()


@application.route('/')
@application.route('/index')
def index():
    path_to_data = 'static/data/'
    if request.args.get('date'):
        dict_piechart = []
        date_string = str(request.args.get('date'))
        print "DATE: " + str(date_string)
        sum_view = 0
        searched_time = datetime.datetime.strptime(date_string, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        date_range = ''
        for j in range(1, 32):
            for i in range(0, 24):
                    if i < 10 and j < 10:
                        date_range += "'2011-01-0" + str(j) + " 0" + str(i) + ":00:00', "
                    elif i < 10:
                        date_range += "'2011-01-" + str(j) + " 0" + str(i) + ":00:00', "
                    elif j < 10:
                        date_range += "'2011-01-0" + str(j) + " " + str(i) + ":00:00', "
                    else:
                        date_range += "'2011-01-25 " + str(i) + ":00:00', "
        date_range = date_range[:-2]
        date_range = ''
        for i in range(0, 24):
            if i < 10:
                date_range += "'2011-01-25 0" + str(i) + ":00:00', "
            else:
                date_range += "'2011-01-25 " + str(i) + ":00:00', "
        date_range = date_range[:-2]
        query = "SELECT name, n_view FROM wiki.wikitrends WHERE date_time IN (" + date_range + ") ORDER BY n_view DESC LIMIT 100"
        # query = "SELECT name, n_view FROM wiki.wikitrends WHERE date_time = '2011-01-25 01:00:00' ORDER BY n_view DESC LIMIT 100"
        raws = session.execute(query)
        for raw in raws:
            print raw
            dict_piechart.append({'category': raw.name, 'measure': int(raw.n_view)})
            sum_view += raw.n_view

        dict_piechart = [{'category': 'All', 'measure': sum_view}] + dict_piechart

        with open(os.path.join(application.root_path, path_to_data + 'data_piechart.csv'), 'wb') as f:
            w = csv.DictWriter(f, dict_piechart[0].keys())
            w.writeheader()
            for row in dict_piechart:
                w.writerow(row)

        # Line chart
        from random import randint
        dict_linechart = []
        for line in dict_piechart:
            current_name = line['category']
            for year in range(2008, 2038):
                dict_linechart.append({'group': current_name, 'category': year, 'measure': randint(0, 10)})
        # my_dict = [{ 'group': "All", 'category': 2008, 'measure': 289309 },
        #             { 'group': "All", 'category': 2009, 'measure': 234998 },
        #             { 'group': "All", 'category': 2010, 'measure': 310900 },
        #             { 'group': "All", 'category': 2011, 'measure': 223900 },
        #             { 'group': "All", 'category': 2012, 'measure': 234600 },
        #             { 'group': "Sam", 'category': 2008, 'measure': 81006.52 },
        #             { 'group': "Sam", 'category': 2009, 'measure': 70499.4 },
        #             { 'group': "Sam", 'category': 2010, 'measure': 96379 },
        #             { 'group': "Sam", 'category': 2011, 'measure': 64931 },
        #             { 'group': "Sam", 'category': 2012, 'measure': 70350 },
        #             { 'group': "Peter", 'category': 2008, 'measure': 63647.98 },
        #             { 'group': "Peter", 'category': 2009, 'measure': 61099.48 },
        #             { 'group': "Peter", 'category': 2010, 'measure': 87052 },
        #             { 'group': "Peter", 'category': 2011, 'measure': 58214 },
        #             { 'group': "Peter", 'category': 2012, 'measure': 58625 },
        #             { 'group': "Rick", 'category': 2008, 'measure': 23144.72 },
        #             { 'group': "Rick", 'category': 2009, 'measure': 14099.88 },
        #             { 'group': "Rick", 'category': 2010, 'measure': 15545 },
        #             { 'group': "Rick", 'category': 2011, 'measure': 11195 },
        #             { 'group': "Rick", 'category': 2012, 'measure': 11725 },
        #             { 'group': "John", 'category': 2008, 'measure': 34717.08 },
        #             { 'group': "John", 'category': 2009, 'measure': 30549.74 },
        #             { 'group': "John", 'category': 2010, 'measure': 34199 },
        #             { 'group': "John", 'category': 2011, 'measure': 33585 },
        #             { 'group': "John", 'category': 2012, 'measure': 35175 },
        #             { 'group': "Lenny", 'category': 2008, 'measure': 69434.16 },
        #             { 'group': "Lenny", 'category': 2009, 'measure': 46999.6 },
        #             { 'group': "Lenny", 'category': 2010, 'measure': 62180 },
        #             { 'group': "Lenny", 'category': 2011, 'measure': 40302 },
        #             { 'group': "Lenny", 'category': 2012, 'measure': 42210 },
        #             { 'group': "Paul", 'category': 2008, 'measure': 7232.725 },
        #             { 'group': "Paul", 'category': 2009, 'measure': 4699.96 },
        #             { 'group': "Paul", 'category': 2010, 'measure': 6218 },
        #             { 'group': "Paul", 'category': 2011, 'measure': 8956 },
        #             { 'group': "Paul", 'category': 2012, 'measure': 9380 },
        #             { 'group': "Steve", 'category': 2008, 'measure': 10125.815 },
        #             { 'group': "Steve", 'category': 2009, 'measure': 7049.94 },
        #             { 'group': "Steve", 'category': 2010, 'measure': 9327 },
        #             { 'group': "Steve", 'category': 2011, 'measure': 6717 },
        #             { 'group': "Steve", 'category': 2012, 'measure': 7035 }
        with open(os.path.join(application.root_path, path_to_data + 'data_linechart.csv'), 'wb') as f:
            w = csv.DictWriter(f, dict_linechart[0].keys())
            w.writeheader()
            for row in dict_linechart:
                w.writerow(row)
    return render_template('index.html')

if __name__ == '__main__':
    application.run(debug=True)
