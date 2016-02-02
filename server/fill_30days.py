from datetime import datetime, timedelta
import pandas as pd
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, IntegerType, StructType, StructField, BooleanType


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(days=n)


def get_Ndays(date, n_days):
    # date : datetime
    # we will sum the views on the 30 days before date, and find the top 10 pages.

    # converting date to datetime
    print 'final date', date
    # date = datetime.strptime(date, '%Y-%m-%d')

    func = lambda x:  ':' not in x.lower() and 'wiki' not in x.lower() and len(x) > 3
    sqlfunc = udf(func, BooleanType())

    # initializing the dataframe
    df_30days = sqlContext.sql(
        """
        SELECT date_time, name, n_view FROM wiki.trends_24hours
        WHERE cast(date_time as date) = cast('{0}' as date)
        """.format(date.strftime('%Y-%m-%d'))
    )

    df_30days = df_30days.filter(sqlfunc(df_30days.name))
    # df_30days.show()

    for single_date in daterange(date - timedelta(days=n_days), date - timedelta(days=1)):
        # query in cassandra on the N days daterange
        print '--------------------------------'
        print 'current date', single_date.strftime("%Y-%m-%d")

        df = sqlContext.sql(
            """
            SELECT date_time, name, n_view FROM wiki.trends_24hours
            WHERE cast(date_time  as date) = cast('{0}' as date)
            """.format(single_date.strftime("%Y-%m-%d"))
        )

        df = df.filter(sqlfunc(df.name))
        # df.show()

        # appending results to the dataframe
        df_30days = df_30days.unionAll(df)

    # finding top 10 pages in the last 30 days:
    tops = df_30days.groupby('name').agg({'n_view': 'sum'}).withColumnRenamed("SUM(n_view)", "n_view")
    tops = tops.orderBy('n_view', ascending=False).limit(100)

    print ''
    print 'tops'
    print ''
    # tops.show()

    # creating column names
    columns = ['d0' + str(i) if i < 10 else 'd' + str(i) for i in range(n_days + 1)]
    columns.append('name')

    tops = tops.toPandas()
    df_30days = df_30days.toPandas()
    df_30days = df_30days.fillna(0)

    # creating empty dataframe with only column names
    df_30dtrends = pd.DataFrame(columns=columns)
    # filling the dataframe :

    for n in tops.name.values:
        print 'name', n
        dd = df_30days[df_30days.name == n].reset_index()
        entry = {columns[int((date - dd['date_time'][i]).days)]: [dd['n_view'][i]] for i in range(dd.shape[0])}
        entry['name'] = [n]
        df_30dtrends = df_30dtrends.append(pd.DataFrame.from_dict(entry), ignore_index=True)

    df_30dtrends['date_time'] = date

    print ''
    print 'trends'
    print df_30dtrends.dtypes
    print df_30dtrends.head()

    tops['date_time'] = date
    print tops.head()

    df_final = pd.merge(tops, df_30dtrends, how='inner', on=['date_time', 'name'])

    # merging into final dataFrame
    #df_final = pd.merge(tops, df_30dtrends, on='name', how='left')

    print ''
    print 'final'
    print df_final.head()

    df_final['date_time'] = df_final['date_time'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df_final = df_final.fillna(0)

    df_final = sqlContext.createDataFrame(df_final)
    df_final.show()

    rdd_final = df_final.map(lambda x: {'date_time': x[2], 'n_view': x[1], 'name': x[0], 'd00': x[3], 'd01': x[4], 'd02': x[5], 'd03': x[6], 'd04': x[7], 'd05': x[8], 'd06': x[9], 'd07': x[10], 'd08': x[11], 'd09': x[12], 'd10': x[13], 'd11': x[14], 'd12': x[15], 'd13': x[16], 'd14': x[17], 'd15': x[18], 'd16': x[19], 'd17': x[20], 'd18': x[21], 'd19': x[22], 'd20': x[23], 'd21': x[24], 'd22': x[25], 'd23': x[26], 'd24': x[27], 'd25': x[28], 'd26': x[29], 'd27': x[30], 'd28': x[31],  'd29': x[32]})

    rdd_final.saveToCassandra('wiki', 'trends_30days')

    return

if __name__ == "__main__":

    for date in daterange(datetime.strptime('2011-01-14', "%Y-%m-%d"), datetime.strptime('2011-03-31', "%Y-%m-%d")):

        get_Ndays(date, 30)
