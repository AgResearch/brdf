#!/usr/bin/python

import sys
import types
import PgSQL
import csv
import re
import os
import math
import random
from datetime import date
import globalConf
import string

import nutrigenomicsConf
import databaseModule

def main():
    connection=databaseModule.getConnection()
    cur = connection.cursor()
    sql = "select * from ontologyob"
    rs = cur.execute(sql)
    print cur.fetchall()
    cur.close()
    
if __name__ == "__main__":
   main()


