#!/usr/bin/python
import inspect, os, sys

def pyFunctionScrapper(pyFile):
   with open(pyFile) as f:
      path, basename = os.path.split(os.path.abspath(pyFile))
      module = basename.split('.')[0]
      functions = {}
      try:
         import module
      except:
         sys.path.append(path)
         vars()[module] = __import__(module, globals(), locals(), [module], -1)

      for funcName, funcObj in inspect.getmembers(eval(module), inspect.isfunction):
         funcDict = {}
         argspec = inspect.getargspec(funcObj)
         funcDict['args'] = argspec.args
         funcDict['varargs'] = argspec.varargs
         if argspec.keywords: 
            funcDict['kwargs'] = zip(argspec.keywords, argspec.defaults)

         functions[funcName] = funcDict
   return functions

if __name__ == '__main__':
   testFile = '../spongeCore.py'
   testFile = os.path.abspath(testFile)
   print pyFunctionScrapper(testFile)
