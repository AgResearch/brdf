#Script to import the user-friendly field-names from the csv file into the database.

#Import the postgres module
import csv
import databaseModule

connection = databaseModule.getConnection()
queryCursor = connection.cursor()

sql = "select max(obid) from ontologyOb"
queryCursor.execute(sql)
print 'Max obid for ontologyOb is: ' + str(queryCursor.fetchall()[0][0])
sql = "select max(obid) from ontologyTermFact"
queryCursor.execute(sql)
print 'Max obid for ontologyTermFact is: ' + str(queryCursor.fetchall()[0][0])

reader = csv.reader(open("DatabaseNames.csv"))

for table_name, column_name, user_friendly_name in reader:
    
    #Rename the "friendly" name when not displayed to NULL...
    if user_friendly_name == '** not displayed **' :
        user_friendly_name = 'NULL'
    else : #...otherwise, put single-quotes around the name, to avoid the NULL being entered as a string
        user_friendly_name = "'" + user_friendly_name + "'"
        
    #If the table doesn't already have an entry in the ontologyob table, create one
    sql = """ select obid from ontologyOb where ontologyName = 'BRDFTABLE_%s';""" % table_name
    queryCursor.execute(sql)
    if len(queryCursor.fetchall()) == 0 :
        sql = """
        insert into ontologyob(
          ontologyName,
          ontologyDescription,
          xreflsid)
        values(
          'BRDFTABLE_%s',
          'This ontology contains column names and descriptions for the %s table',
          'ontology.BRDFTABLE_%s');""" % (table_name, table_name, table_name)
        queryCursor.execute(sql)

   #Irrespectively of whether an entry was or wasn't just created...
    sql = """
    insert into ontologyTermFact(
      ontologyob,
      xreflsid,
      termname,
      termdescription)
    select
      obid,
      'ontology.BRDFTABLE_%s.%s',
      '%s',
      %s
    from
      ontologyOb
    where
      ontologyName = 'BRDFTABLE_%s';""" % (table_name, column_name, column_name, user_friendly_name, table_name)
    queryCursor.execute(sql)
    
    sql = """
    insert into ontologyTermFact2(
      ontologyTermID,
      factNameSpace,
      attributeName,
      attributeValue)
    select
      obid,
      'DISPLAY',
      'DISPLAYNAME',
      %s
    from
      ontologytermfact 
    where
      ontologyob = (select obid from ontologyob where ontologyName = 'BRDFTABLE_%s') and
      termname = '%s';""" % (user_friendly_name, table_name, column_name)
    queryCursor.execute(sql)
    
connection.commit()
connection.close()
exit;
