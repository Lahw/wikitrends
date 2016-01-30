import functools
import glob


def proc(f):
    global sc
    f = f.split('/')[-1]
    to_datetime = lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:8] + ' ' + x[9:11] + ':' + x[11:13] + ':' + x[13:15]
    r = sc.textFile('file:///mnt/wikidata/wikistats/' + str(f))
    r = r.map(lambda x: x.split(' '))
    r = r.filter(lambda x: int(x[2]) > 10)
    r = r.map(lambda x: {'date_time': to_datetime(f[11:26]), 'name': x[1], 'n_view': int(x[2])})
    return r

# get the big rdd
rdd = sc.union([proc(f) for f in glob.glob("/mnt/wikidata/wikistats/*")])

##############
## Compute sum
##############
# 1. group by name / month / day
# 2. sum the n_view
# 3. rebuild
rdd_24hours_sum = rdd.map(lambda x: (x['name'] + ' ' + x['date_time'][:10], x['n_view'])) \
                     .reduceByKey(lambda a, b: a + b) \
                     .map(lambda x: {'name': x[0].split(' ')[0], 'date_time': x[0].split(' ')[1], 'n_view': x[1]})


def create_entry(x):
    res_dict = {}
    res_dict['name'] = x[0].split(' ')[0]
    res_dict['date_time'] = x[0].split(' ')[1]
    for entry in x[1].split(','):
        res_dict['h' + entry.split(' ')[0]] = int(entry.split(' ')[1])
    for hour in range(0, 24):
        if hour < 10:
            key_name = 'h0' + str(hour)
        else:
            key_name = 'h' + str(hour)
        if key_name not in res_dict.keys():
            res_dict[key_name] = 0
    return res_dict
############################
## Get n_view for each hour
############################
# same logic as before
rdd_24hours_hours = rdd.map(lambda x: (x['name'] + ' ' + x['date_time'][:10], x['date_time'][11:13] + ' ' + str(x['n_view']))) \
                       .reduceByKey(lambda a, b: a + ',' + b) \
                       .map(lambda x: create_entry(x))


############################
## Join everything !
############################
df_24hours_sum = sqlContext.createDataFrame(rdd_24hours_sum)
df_24hours_hours = sqlContext.createDataFrame(rdd_24hours_hours)
keep = [df_24hours_sum[c] for c in df_24hours_sum.columns] + [df_24hours_hours[c] for c in df_24hours_hours.columns if c not in ['name', 'date_time']]
df_24hours = df_24hours_sum.join(df_24hours_hours, (df_24hours_sum['name'] == df_24hours_hours['name']) & (df_24hours_sum['date_time'] == df_24hours_hours['date_time']), joinType='outer').select(*keep)


#############################
## Format & Save to Cassandra
#############################
# ugly but didn't find anything better
rdd_24hours = df_24hours.map(lambda x: {'date_time': x[0], 'n_view': x[1], 'name': x[2], 'h00': x[3], 'h01': x[4], 'h02': x[5], 'h03': x[6], 'h04': x[7], 'h05': x[8], 'h06': x[9], 'h07': x[10], 'h08': x[11], 'h09': x[12], 'h10': x[13], 'h11': x[14], 'h12': x[15], 'h13': x[16], 'h14': x[17], 'h15': x[18], 'h16': x[19], 'h17': x[20], 'h18': x[21], 'h19': x[22], 'h20': x[23], 'h21': x[24], 'h22': x[25], 'h23': x[26]})
rdd_24hours.saveToCassandra('wiki', 'trends_24hours')
