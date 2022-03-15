// NOTE FROM PUZZLE AUTHOR: This script replaces code that originally ran server-side during the hunt.
// Reading this code is not intended as part of the solve path, and puzzle spoilers may lie ahead.
//
//
//
//
//
//
//  (Padding for spoilers)
//
//
//
//
//
//

const initSqlJs = window.initSqlJs;
const SQL = await initSqlJs({locateFile: file => window.puzzleStaticDirectory + "sql/sql-wasm.wasm"});

function initializeDb() {
    var createTable = "CREATE TABLE IF NOT EXISTS students (" +
    "    name text NOT NULL PRIMARY KEY," +
    "    enrollment_date text NOT NULL" +
    ");";

    var createTableTwo = "CREATE TABLE IF NOT EXISTS students_new (" +
    "    student_first_name text NOT NULL," +
    "    student_last_name text NOT NULL," +
    "    enrollment_date text NOT NULL," +
    "    PRIMARY KEY (student_first_name, student_last_name)" +
    ");";

    var insert = "INSERT INTO students (name, enrollment_date) VALUES" +
    "('Please', 'do')," +
    "('not', 'use')," +
    "('table', '\"students\"')," +
    "('anymore.', 'Student')," +
    "('data', 'has')," +
    "('all', 'been')," +
    "('moved', 'to')," +
    "('\"students_new\".', 'Thank')," +
    "('you.', '- Admins')" +
    ";";

    var insertTwo = "INSERT INTO students_new (student_first_name, student_last_name, enrollment_date) VALUES " +
    "('Aly', 'Schulze', '2019-11-15')," +
    "('Ariel', 'Thwaite', '2019-11-29')," +
    "('Bobby', 'Roberts', '2014-08-18')," +
    "('Chett', 'Wolcott', '2018-04-01')," +
    "('Cierra', 'Yewdale', '2013-11-27')," +
    "('Eddie', 'Ullyett', '2020-07-01')," +
    "('Igor', 'Xenopol', '2016-07-22')," +
    "('Issa', 'Vidhani', '2017-10-20')," +
    "('Yoko', 'Zanders', '2015-02-06')" +
    ";";

    const db = new SQL.Database();
    db.run(createTable);
    db.run(createTableTwo);
    db.run(insert);
    db.run(insertTwo);

    return db;
}

function runQuery(query) {
    // The SQLite client implementation used by the original Python back-end code
    // did not allow more than one statement to be executed at a time. Since this
    // behavior was a part of the original challenge of the puzzle, but isn't the
    // default for the JS SQLite implementation use here, we artificially enforce
    // the one statement per call limit in this method using a StatementIterator.
    const db = initializeDb();
    const iterator = db.iterateStatements(query);
    const iteration = iterator.next();
    if(iteration.done) {
        return [];
    }
    const statement = iteration.value;

    var result = [];
    try {
        while(statement.step()){
            result.push(statement.get());
        }
    } finally {
        statement.free();
    }

    const nextIteration = iterator.next();
    if(!nextIteration.done){
        nextIteration.value.free();
        throw new Error("You can only execute one statement at a time.")
    }

    return result;
}

function findStudents(name) {
    const query = `select * from students where name = '${name}'`
    try{
        return runQuery(query);
    } catch (error) {
        throw new Error(`SQLite error: Something went wrong with query ${query}: ${error.message}`)
    }
}
export { findStudents };
