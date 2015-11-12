# run with: ipython -i interactive_rethinkdb.py
import rethinkdb as r
conn = r.connect( "localhost", 28015).repl()
db = r.db('opa')
tables = db.table_list().run(conn)
initial = db.table(tables[0]).changes().merge({'table':tables[0]})

for table in tables[1:]:
    initial = initial.union(db.table(table).changes().merge({'table':table}))
for change in initial.run(conn):
    print 'change', change
