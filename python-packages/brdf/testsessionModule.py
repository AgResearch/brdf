#
# this module contains constants and methods for maintaining
# session information in brdf applications
#
#
from pkg_resources import require
require("PyCAPTCHA")

import sha, base64, string
from datetime import date
import time
import os
#from workFlowModule import staffOb

import Captcha
from Captcha.Visual import Tests



def getSessionToken(privateKey, userName):
    """ this method returns a session token  - could be used for a number of things """
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



def getCaptchaSession(filepath):
    """ This method creates a captcha object and saves it persistently. """
    factoryName = "brdfcaptchafactory" #getSessionToken("captcha","nobody")
    factory =  Captcha.PersistentFactory(os.path.join(filepath, factoryName))
    session = factory.new(getattr(Tests, Tests.__all__[0]))
    session.render().save(os.path.join(filepath,"%s.jpg"%(session.id)),"JPEG")
    return (factoryName,session.id)


def checkCaptchaSolution(filepath, factoryName, sessionid, word):
    factory =  Captcha.PersistentFactory(os.path.join(filepath, factoryName))
    session = factory.get(sessionid)
    return session.testSolutions([word])


def main():
    #print getSessionToken('#^456%^$%64664gdgrrtyr$%64^$%^$%^$%&%&','Wes Barris')
    #t=time.gmtime()
    #print
    test = getCaptchaSession("/tmp")
    print test   #e.g. ('brdfcaptchafactory', 'Fvk81ytnJTDDTVMHq5z0r7di')
    #print checkCaptchaSolution("/tmp","brdfcaptchafactory","7EjgtgoprG0OCXHOtsrANjSg","store")
    #print checkCaptchaSolution("/tmp","brdfcaptchafactory","aEGtxtF2rsi6VJBn3u0OtyDQ","clean")
    print checkCaptchaSolution("/tmp","brdfcaptchafactory",test[1],"clean")


    
    #print test
    #print test[1].id
    
        
if __name__ == "__main__":
   main()



