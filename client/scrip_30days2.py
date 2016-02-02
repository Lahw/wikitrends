import pandas as pd
from datetime import date, datetime, timedelta
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
import numpy as np


def past_date(date, n_days=30):
    return (date - timedelta(days=n_days)).strftime("%Y-%m-%d")


def time_delta(x, y):
    start = datetime.strptime(x, '%Y-%m-%d')
    end = datetime.strptime(y, '%Y-%m-%d')
    delta = (end - start).days
    # print 'time delta', delta
    return delta


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days=n)


def get_Ndays(date, n_days):
    # date : string
    # we will sum the views on the 30 days before date, and find the top 10 pages.

    # converting date to datetime
    date = datetime.strptime(date, '%Y-%m-%d')

    print past_date(date, n_days=n_days), date

    cluster = Cluster(['54.88.108.226'])
    session = cluster.connect()
    session.row_factory = dict_factory

    df = pd.DataFrame(columns=['date_time', 'name', 'n_view'])

    for single_date in daterange(date - timedelta(days=n_days), date):
        # query in cassandra on the 30 days daterange
        print single_date.strftime("%Y-%m-%d")
        rows = session.execute(
            """
        	SELECT date_time, name, n_view FROM wiki.trends_24hours
    		WHERE date_time = '{0}'
            AND n_view >= 100
            """.format(single_date.strftime("%Y-%m-%d"))
        )

        # transforming the result object in to a list
        rows = rows.current_rows

        # building dataframe with the query results
        for row in rows:
            df = df.append(pd.DataFrame.from_dict({k: [v] for k, v in row.items()}), ignore_index=True)

    print df.shape
    print 'query res :', df.head()

    # finding top 10 pages in the last 30 days:
    tops = df.groupby('name').sum().add_suffix('_sum').reset_index()
    tops = tops.sort_values(by='n_view_sum', ascending=False).iloc[:10, :]

    print ''
    print 'tops', tops.name.values
    print ''
    print tops.head

    # creating column names
    columns = ['d0' + str(i) if i < 10 else 'd' + str(i) for i in range(n_days)]
    columns.append('name')

    # creating empty dataframe with only column names
    df_30dtrends = pd.DataFrame(columns=columns)
    # filling the dataframe :
    for n in tops.name.values:
        print 'name', n
        dd = df[df.name == n].reset_index()
        entry = {columns[int((date - dd['date_time'][i]).days)]: [dd['n_view'][i]] for i in range(dd.shape[0])}
        entry['name'] = [n]
        df_30dtrends = df_30dtrends.append(pd.DataFrame.from_dict(entry), ignore_index=True)

    print ''
    print 'trends'
    print df_30dtrends.head()

    # merging into final dataFrame
    df_final = pd.merge(tops, df_30dtrends, on='name', how='left')

    print ''
    print 'final'
    print df_final.head()

    return


if __name__ == '__main__':

    get_Ndays('2011-02-05', 15)
