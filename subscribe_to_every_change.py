import rethinkdb as r
conn = r.connect( "localhost", 28015).repl()

def run_massive_cf():
    dbs = r.db_list().run(conn)
    tables = r.db(dbs[0]).table_list().run(conn)
    initial = r.db(dbs[0]).table(tables[0]).changes().merge({'table':tables[0], 'database':dbs[0]})
    for database in dbs:
        tables = r.db(database).table_list().run(conn)    
        for table in tables:
            initial = initial.union(r.db(database).table(table).changes().merge({'table':table, 'database': database}))
    for change in initial.run(conn):
        print change
        if change['database'] == 'rethinkdb' and change['table'] == 'table_config':
            break
        
while True:
    try:
        run_massive_cf()
    except:
        pass
