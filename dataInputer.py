#!/usr/bin/python
import sqlite3, argparse

PROG_DESC = """Takes python code and imports into sqlite structure."""
SQLITE_DB = 'codeRepo.sqlite'

def connectDB(db, verify=True):
   # verify database does already exist
   if verify && not os.path.isfile(db):
      sys.exit("Database does not exists! Exiting.")
   # connect to database
   return sqlite3.connect(db)

def main(args):
   conn = connectDB(args.db, verify=False)   
   buildTables(conn)
   for pyCode in args.inputs:
      importCode(pyCode, conn)

def buildTables(conn):
   createStmt = """ CREATE TABLE IF NOT EXISTS modules ( 
                    id INTEGER PRIMARY KEY, 
                    name VARCHAR UNIQUE NOT NULL, 
                    code BLOB NOT NULL )
                """
   conn.execute(createStmt)

# NOTE: need to add variable to database telling if compressed (and what compression?)
def importCode(pyCode, conn, compress=True):
   try:
      name = o.path.basename(pyCode)
      with open(pyCode) as f:
         data = f.read()
         if compress:
            from zlib import compress
            data = compress(data)
         blob = sqlite3.Binary(data)
      conn.execute("INSERT INTO modules (name, code) VALUES (?,?)", (name, blob) )
   except:
      raise #discover errors generated here

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description=textwrap.dedent(PROG_DESC))
   parser.add_argument('inputs', metavar='PYTHON_CODE', type=str, nargs='+',
                        help='A list of python scripts.')
   parser.add_argument('db', metavar='SQLITE_DB', type=str, default=SQLITE_DB,
                        help='an integer for the accumulator')
   parser.set_defaults(func=main)
   args = parser.parse_args()
   args.func(args)
