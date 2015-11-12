
def download_file(url, local_filename):
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    
    
@app.route('/convert_pdf_to_text/')
def convert_pdf_to_text():
    import uuid
    filename = str(uuid.uuid4()) + '.pdf'
    print 'downloading'
    download_file(request.args['url'], filename)
    print 'downloaded'
    f = {'results': os.popen('pdf2txt.py %s' % (filename)).read()}
    os.system('rm %s' % (filename))
    return jsonify(**f)

@app.route('/get_databases/')
def get_databases():
    f = {'results': r.db_list().run(conn)}
    return jsonify(**f)
    
@app.route('/get_tables_for_each_database/')
def get_tables_for_each_database():
    f = {'results': dict([(db, r.db(db).table_list().run(conn)) for db in r.db_list().run(conn)])}
    return jsonify(**f)
    
@app.route('/get_keys_for_each_table_for_each_database/')
def get_keys_for_each_table_for_each_database():
    f = {'databases_to_tables': dict([(db, sorted(r.db(db).table_list().run(conn))) for db in r.db_list().run(conn)])}
    f['databases'] = sorted(r.db_list().run(conn))
    f['tables_to_keys'] = {} # tuple as key (db, table) -> keys
    for database in f['databases']:
        for table in f['databases_to_tables'][database]:
            rows = list(r.db(database).table(table).run(conn))
            keys = [row.keys() for row in rows]
            keys = list(itertools.chain.from_iterable(keys))
            f['tables_to_keys'][database+'_'+table] = sorted(list(set(keys)))
    return jsonify(**f)
    
@app.route('/get_tables_for_database/')
def get_tables_for_database():
    f = {'results': dict([(db, r.db(db).table_list().run(conn)) for db in r.db_list().run(conn)])}
    return jsonify(**f)
        
    
@app.route('/get_keys_for_table/')
def get_keys_for_table():
    if not request.args.get('db') in r.db_list().run(conn):
        f = {'error': 'db not in list of dbs'}
    elif not request.args.get('table') in r.db(request.args['db']).table_list().run(conn):
        f = {'error': 'table not in list of tables'}
    else:
        rows = list(r.db(request.args['db']).table(request.args['table']).run(conn))
        keys = [row.keys() for row in rows]
        keys = list(itertools.chain.from_iterable(keys))
        f = {'results': sorted(list(set(keys)))}
    return jsonify(**f)
    
@app.route('/cron_log/')
def cron_log():
    clog = os.popen('grep CRON /var/log/syslog').read()
    f = {'results': clog.split('\n')[::-1]}
    return jsonify(**f)    

@app.route('/get_percentage/')    
def get_percentage():
    """
    peoplesnsa.com/get_percentage/?database=opa&table=closed_case_summaries&column_to_match=Complaints&match_what=.*?Force Review Board.*?&column_for_numerator=is_sustained&numerator_boolean=True
    database
    table 
    column_to_match
    match_what
    column_for_numerator
    numerator_boolean
    """
    base = r.db(request.args['database']).table(request.args['table']).filter(lambda case: case[request.args['column_to_match']].match(request.args['match_what']))
    denominator = base.count().run(conn)
    
    numerator = base.filter({request.args['column_for_numerator']: bool(request.args['numerator_boolean'])}).count().run(conn) 
    
    if denominator:
        percentage = float(numerator)/denominator
        percentage = "{:.0%}".format(percentage)+' (%s/%s)' % (numerator, denominator)
    else:
        percentage = 'Error: No denominator'    
    f = {'numerator': numerator, 'denominator': denominator, 'percentage': percentage, 'request': request.args}
    return jsonify(**f)    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
