from django.http import HttpResponseServerError

import sqlite3, logging
from sqlite3 import Error
from multiprocessing import Queue, Process

logger = logging.getLogger(__name__)

CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS students (
    name text NOT NULL PRIMARY KEY,
    enrollment_date text NOT NULL
)
'''

CREATE_TABLE_TWO = '''
CREATE TABLE IF NOT EXISTS students_new (
    student_first_name text NOT NULL,
    student_last_name text NOT NULL,
    enrollment_date text NOT NULL,
    PRIMARY KEY (student_first_name, student_last_name)
)
'''

INSERT = '''
INSERT INTO students (name, enrollment_date) VALUES
('Please', 'do'),
('not', 'use'),
('table', '"students"'),
('anymore.', 'Student'),
('data', 'has'),
('all', 'been'),
('moved', 'to'),
('"students_new".', 'Thank'),
('you.', '- Admins')
;
'''

INSERT_TWO = '''
INSERT INTO students_new (student_first_name, student_last_name, enrollment_date) VALUES
('Aly', 'Schulze', '2019-11-15'),
('Ariel', 'Thwaite', '2019-11-29'),
('Bobby', 'Roberts', '2014-08-18'),
('Chett', 'Wolcott', '2018-04-01'),
('Cierra', 'Yewdale', '2013-11-27'),
('Eddie', 'Ullyett', '2020-07-01'),
('Igor', 'Xenopol', '2016-07-22'),
('Issa', 'Vidhani', '2017-10-20'),
('Yoko', 'Zanders', '2015-02-06')
;
'''

def initialize_db():
    db = sqlite3.connect("file::memory:", uri = True)
    cursor = db.cursor()
    cursor.execute(CREATE_TABLE)
    cursor.execute(INSERT)
    cursor.execute(CREATE_TABLE_TWO)
    cursor.execute(INSERT_TWO)
    cursor.execute('PRAGMA hard_heap_limit=2000000')
    db.commit()
    return db

# Returns the query results as rows
def run_query(query, result_queue):
    try:
        db = initialize_db()
        cursor = db.cursor()
        cursor.execute(query)
        result_queue.put(cursor.fetchmany(1000))
    except (Error, sqlite3.Warning) as e:
        result_queue.put(HttpResponseServerError("SQLite error: Something went wrong with query {}: {}".format(query, e)))
    except:
        logger.exception('Unknown error running query')
        result_queue.put(HttpResponseServerError("Unknown error."))

# Returns the query results as rows
def run_query_in_process(query):
    try:
        result_queue = Queue()
        p = Process(target=run_query,args=(query,result_queue,))
        p.start()
        p.join(1)
        if(p.is_alive()):
            p.kill()
            p.join()
            return HttpResponseServerError("Query timed out.")
        result = result_queue.get()
        result_queue.close()
        result_queue.join_thread()
        return result
    except:
        logger.exception('Unknown error')
        return HttpResponseServerError("Unknown error.")

