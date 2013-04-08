#!/usr/bin/python
# For serverless databases
import sqlite3
# For parsing command line arguements and tab completion of those arguments
import argparse, textwrap, argcomplete
import os

PROG_DESC = """Takes python code and imports into sqlite structure."""
SQLITE_DB = 'codeRepo.sqlite'
DB_COMPRESSED = True

def connectDB(db, verify=True):
   # verify database does already exist
   if verify and not os.path.isfile(db):
      sys.exit("Database does not exists! Exiting.")
   # connect to database
   return sqlite3.connect(db)


def buildTables(conn):
   createStmt = """ CREATE TABLE IF NOT EXISTS modules ( 
                    id INTEGER PRIMARY KEY, 
                    name VARCHAR UNIQUE NOT NULL, 
                    code BLOB NOT NULL )
                """
   conn.execute(createStmt)
   conn.commit()

def importer(args):
   conn = connectDB(args.db, verify=False) # cannot test existence here...
   buildTables(conn)
   for pyCode in args.inputs:
      importModules(pyCode, conn)

# NOTE: need to add variable to database telling if compressed (and what compression?)
def importModules(pyCode, conn, compress=DB_COMPRESSED):
   """ This function imports a python script into the repository aspect of the database."""
   try:
      name = os.path.basename(pyCode)
      with open(pyCode) as f:
         data = f.read()
         if compress:
            from zlib import compress
            data = compress(data)
         blob = sqlite3.Binary(data)
      conn.execute("INSERT INTO modules (name, code) VALUES (?,?)", (name, blob) )
      # consider returning the record id of the module inserted?
      # recordId = conn.execute("SELECT id FROM modules WHERE name=?", name)
      conn.commit()
   except:
      raise #discover errors generated here

def exporter(args):
   conn = connectDB(args.db) 
   exportModules(args.recordId, conn)

def exportModules(recordId, conn, compress=DB_COMPRESSED):
   try:
      name, blob = conn.execute("SELECT name, code FROM modules WHERE id=?", recordId).fetchone()
      data = bytes(blob)
      if compress:
         from zlib import decompress
         data = decompress(data)
      #NOTE: assume for now writing to current directory
      with open(name, 'w') as f:
         f.write(data)
   except:
      raise #discover errors generated here

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description=textwrap.dedent(PROG_DESC))
   parser.add_argument('-db', metavar='SQLITE_DB', type=str, default=SQLITE_DB,
                        help='an integer for the accumulator')
   subparsers = parser.add_subparsers(help='sub-command help')

   # input new code
   importParser = subparsers.add_parser('import', help='Import code into SPONGE')
   importParser.add_argument('inputs', metavar='PYTHON_CODE', type=str, nargs='+',
                        help='A list of python scripts.')
   importParser.set_defaults(func=importer)

   # export code
   exportParser = subparsers.add_parser('export', help='Export code from SPONGE')
   exportParser.add_argument('recordId', type=str, help='Record id in table.')
   exportParser.set_defaults(func=exporter)
   
   argcomplete.autocomplete(parser)
   args = parser.parse_args()
   
   args.func(args)
