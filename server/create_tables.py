from cassandra.cluster import Cluster

cluster = Cluster()
session = cluster.connect()


KEYSPACE = "wiki"

session.execute("""CREATE KEYSPACE IF NOT EXISTS %s
    WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' } """ % KEYSPACE)
session.execute("""create table wiki.trends_24hours (date_time timestamp, n_view bigint, name text,
        h00 bigint, h01 bigint, h02 bigint, h03 bigint, h04 bigint, h05 bigint,
        h06 bigint, h07 bigint, h08 bigint, h09 bigint, h10 bigint, h11 bigint,
        h12 bigint, h13 bigint, h14 bigint, h15 bigint, h16 bigint, h17 bigint,
        h18 bigint, h19 bigint, h20 bigint, h21 bigint, h22 bigint, h23 bigint,
        primary key(date_time, name))""")

session.execute("""create table wiki.trends_30days (date_time timestamp, n_view bigint, name text,
        d00 bigint, d01 bigint, d02 bigint, d03 bigint, d04 bigint, d05 bigint,
        d06 bigint, d07 bigint, d08 bigint, d09 bigint, d10 bigint, d11 bigint,
        d12 bigint, d13 bigint, d14 bigint, d15 bigint, d16 bigint, d17 bigint,
        d18 bigint, d19 bigint, d20 bigint, d21 bigint, d22 bigint, d23 bigint,
        d24 bigint, d25 bigint, d26 bigint, d27 bigint, d28 bigint, d29 bigint,
        primary key(date_time, n_view, name))""")
