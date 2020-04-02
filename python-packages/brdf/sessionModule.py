#
# this module contains constants and methods for maintaining
# session information in brdf applications
#
#
import sha, base64, string
from datetime import date
import time
from workFlowModule import staffOb


def getSessionToken(privateKey, userName):
    """ this method returns a session token """
    t = time.gmtime()
    timestamp = time.strftime("%d%m%y%H%M%S",t)
    bob = sha.new(privateKey+userName+timestamp)
    #return timestamp+base64.encodestring(bob.hexdigest())
    return timestamp+bob.hexdigest()

def getFullName(connection, loginName):
    """ this method queries the database to obtain a full name given
    a login name"""

    fullName = "nobody"
    
    # get user object
    user = staffOb()
    user.initFromDatabase(string.lower("%s"%loginName),connection)

    # stub code until we get this working
    return user.databaseFields['fullname']


def main():
    print getSessionToken('#^456%^$%64664gdgrrtyr$%64^$%^$%^$%&%&','Wes Barris')
    #t=time.gmtime()
    #print 
        
if __name__ == "__main__":
   main()



