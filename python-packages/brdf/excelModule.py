""" This modules provides a lightweight API to access Excel data.
    There are many ways to read Excel data, including ODBC. This module
    uses ADODB and has the advantage of only requiring a file name and a
    sheet name (no setup required).
"""

import win32com.client

class ExcelDocument(object):
    """ Represents an opened Excel document.
    """

    def __init__(self,filename):
        self.connection = win32com.client.Dispatch('ADODB.Connection')
        self.connection.Open(
            'PROVIDER=Microsoft.Jet.OLEDB.4.0;'+
            'DATA SOURCE=%s'%filename+
            ';Extended Properties="Excel 8.0;HDR=1;IMEX=1"'
        )

    def sheets(self):
        """ Returns a list of the name of the sheets found in the document.
        """
        result = []
        recordset = self.connection.OpenSchema(20)
        while not recordset.EOF:
            result.append(recordset.Fields[2].Value)
            recordset.MoveNext()
        recordset.Close()
        del recordset
        return result

    def sheet(self,name):
        """ Returns a sheet object by name. Use sheets() to obtain a list of
            valid names.
        """
        return ExcelSheet(self,name)
            
    def __del__(self):
        self.close()

    def close(self):
        """ Closes the Excel document. It is automatically called when
            the object is deleted.
        """
        try:
            self.connection.Close()
            del self.connection
        except:
            pass

def strip(value):
    """ Strip the input value if it is a string and returns None
        if it had only whitespaces """
    if isinstance(value,basestring):
        value = value.strip()
        if len(value)==0:
            return None
    return value

class ExcelSheet(object):
    """ Represents an Excel sheet from a document, gives methods to obtain
        column names and iterate on its content.
    """
    def __init__(self,document,name):
        self.document = document
        self.name = name

    def columns(self):
        """ Returns a list of column names for the sheet.
        """
        recordset = win32com.client.Dispatch('ADODB.Recordset')
        recordset.Open(u'SELECT * FROM [%s]'%self.name,self.document.connection,0,1)
        try:
            return [field.Name for field in recordset.Fields]
        finally:
            recordset.Close()
            del recordset
                
    def __iter__(self):
        """ Returns a paged iterator by default. See paged().
        """
        return self.paged()

    def naive(self):
        """ Returns an iterator on the data contained in the sheet. Each row
            is returned as a dictionary with row headers as keys.
        """
        # SLOW algorithm ! A lot of COM calls are performed.
        recordset = win32com.client.Dispatch('ADODB.Recordset')
        recordset.Open(u'SELECT * FROM [%s]'%self.name,self.document.connection,0,1)
        try:
            while not recordset.EOF:
                source = {}
                for field in recordset.Fields:
                    source[field.Name] = strip(field.Value)
                yield source
                recordset.MoveNext()
            recordset.Close()
            del recordset
        except:
            # cannot use "finally" here because Python doesn't want
            # a "yield" statement inside a "try...finally" block. 
            recordset.Close()
            del recordset
            raise
    
    def paged(self,pagesize=128):
        """ Returns an iterator on the data contained in the sheet. Each row
            is returned as a dictionary with row headers as keys. pagesize is
            the size of the buffer of rows ; it is an implementation detail but
            could have an impact on the speed of the iterator. Use pagesize=-1
            to buffer the whole sheet in memory.
        """
        # FAST algorithm ! It is about 10x faster than the naive algorithm
        # thanks to the use of GetRows, which dramatically decreases the number
        # of COM calls.
        recordset = win32com.client.Dispatch('ADODB.Recordset')
        recordset.Open(u'SELECT * FROM [%s]'%self.name,self.document.connection,0,1)
        try:
            fields = [field.Name for field in recordset.Fields]
            ok = True
            while ok:
                rows = recordset.GetRows(pagesize)
                if recordset.EOF:
                    # close the recordset as soon as possible
                    recordset.Close()
                    recordset = None
                    ok = False

                fields_values = zip(fields,rows)
                for i in xrange(len(rows[0])):
                    source = {}
                    for field,values in fields_values:
                        source[field] = strip(values[i])
                    yield source
        except:
            if recordset is not None:
                recordset.Close()
                del recordset
            raise

if __name__=='__main__':
    for line in ExcelDocument('test.xls').sheet('Feuil1$'):
        print line

