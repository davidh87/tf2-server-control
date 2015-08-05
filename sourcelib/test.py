#!/usr/bin/python

from SourceQuery import SourceQuery
import sys

server = SourceQuery('91.121.95.23', 27013)
#print server.ping()
print server.info()
print server.player()
print server.rules()
