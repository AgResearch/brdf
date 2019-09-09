#-----------------------------------------------------------------------+
# Name:		securityProcedures.py           				|
#									|
# Description:	classes that implements security procedures              |
#		                                                        |
#                                                                	|
#=======================================================================|
# Copyright 2005 by AgResearch (NZ).					|
# All rights reserved.							|
#									|
#=======================================================================|
# Revision History:							|
#									|
# Date      Ini Description						|
# --------- --- ------------------------------------------------------- |
# 11/2005    AFM  initial version                                       |
#-----------------------------------------------------------------------+
import sys
import types
import csv
import re
import os
import math
import random
from datetime import date
import globalConf
from brdfExceptionModule import brdfException
import logging




# set up logger if we want logging
securitymodulelogger = logging.getLogger('securityProcedures')
securitymodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'securityprocedures.log'))
#hdlr = logging.FileHandler('c:/temp/sheepgenomicsforms.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
securitymodulehdlr.setFormatter(formatter)
securitymodulelogger.addHandler(securitymodulehdlr) 
securitymodulelogger.setLevel(logging.INFO)        

""" --------- module variables ----------"""
""" currently staff roles are defined here rather than in the
database for performance reasons. The database tables that are designed
for this information are
staffob
stafflist
stafflistmembershiplink
"""
stafflists = {
    'pgc' : [
         'sarkara',
         'scotta',
    	 'griffithsa',
    	 'waught',
    	 'kardailskyi',
    	 'ellisonn',
    	 'franzmayrb',
    	 'favillem',
    	 'collettev',
    	 'allana',
    	 'jjjonesc',
    	 'barrettb',
    	 'hancockk',
    	 'richardk',
         'mccullocha',
         'macleanp',
         'albertn'],
    'bioinformatics' : [
         'khana',
         'simond',
         'smithiesr',
         'mitchellj',
         'molenaara',
         'maqbooln',
         'mccullocha',
         'moragar',
    	 'xxxjonesc',
         'mcewanj',
         'brauningr',
         'bechera',
         'park-ngz',
         'doddsk',
         'phuas',
         'lindsayp',
         'macleanp',
         'caom'
         ],
    'aft' : [
         'johnsonr',
         'voiseyc',
         'xxxvoiseyc',
         'xxxfleetwoodd',
         'johnsonl',
         'prattj',
         'xxxrasmussens',
         'macleanp',
         'brauningr',
         'caom'
         ],
    'cervine' : [
         'lic',
         'harpera'
         ],
    'microbial' : [
         'parkngz',
         'lambies',
         'mccullocha'
         ],
    'lic' : [
         'nobody',
         'mccoards',
         'mccullocha',
         'pachecod',
         'khana',
         'parkngz'
         ],
    'dba' : [
         'nobody',
         'mccullocha',
         'macleanp',
         'moragar',
         'collettev'    # temp added 19/3/2012 so can access seqs
         ]

}





""" --------- module methods ------------"""

def getLSIDRuleBasedPermission(objectlsid, username = 'nobody', resourcename = 'information summary', policyDict = {}, defaultResult = False):
    """
    This procedure is used to apply a (semantic) rule-based security policy - for example, a rule based
    on the LSID of an object.

    It is attached to objects using the securityFunction table and is usually called by the runSecurityFunctions method. This means
    the call can refer to....

    resourcename
    self.username
    self.databaseFields['xreflsid']

    This table can be used to attach this procedure either to all objects of a certain type,
    or to individual objects
    

    This method applies rules about access to the information summary and information map sections of the
    standard page.

    A policy consists of a nested dictionary and tuple structure as (for example) follows : 
    {
        'information summary ' : 
        [
           ('deny' , {
               '.*' : None
            }),
           ('allow' , {
               '^PGC' : ['pgc','bioinformatics'],
               '^NCBI' : ['all users']
            })
        ],
        'information map' :
        [
           ('deny' , {
               '.*' : None
            }),
           ('allow' , {
               '^PGC' : ['pgc','bioinformatics'],
            })
        ]
    }

    This defines polices for the information summary and information map parts of the
    brdf page.

    each policy consists of deny and allow tuples - the order determines which is applied first

    each deny or allow tuple consists of a dictionary - the keys of which are regular expressions and
    the value of which is either a  list of staff-list names, or None - if no list is given , the
    rule is applied to all users

    If the regular expression is matched when applied to the LSID, then
    the indicated permission is set.

    Thus the above policy would result in information summaries being available for PGC seqs to
    just PGC and bioinformatics ; but for NCBI sequences to members of all users

    """

    result = defaultResult # it may be that no decision is reached from the policy , if (e.g.) no matches are founf
                           # - in this case the default result is returned

       
    #stafflists = {
    #    'pgc' : ['bloggs']
    #}


    securitymodulelogger.info("checking security on %s for %s using %s"%(resourcename,username,str(policyDict)))
    securitymodulelogger.info("using stafflist %s"%(str(stafflists)))
    securitymodulelogger.info("using lsid %s"%objectlsid)
    
    

    # if there is a policy for this resource in the policy dictionary we were passed
    if resourcename in policyDict:
        
        policy = policyDict[resourcename]

        # a policy is a list of (normally two) tuples -each tuple defines an allow/deny accessmask that we must evaluate
        for accessmask in policy:

            # each access mask is a binary tuple - the first element is either allow or deny. The second
            # element is a dictionary , with patterns as key and lists of user groups as value.

            # evaluate the access mask. 
            if accessmask[0] == 'allow':
                mask = True
            else:
                mask = False

            securitymodulelogger.info("applying %s mask using %s"%(accessmask[0],str(accessmask[1])))
                
            for pattern in accessmask[1].keys():
                
                securitymodulelogger.info("matching %s "%(pattern))
                

                # if we get a match - i.e. this mask applies to this object
                if re.search(pattern, objectlsid,re.IGNORECASE) != None:

                    # if there is no list of staff roles , then the mask applies to
                    # all users
                    if accessmask[1][pattern] == None:

                        securitymodulelogger.info("setting mask to %s from match to %s (no roles)"%(mask,pattern))

                        
                        result = mask
                    else:
                        for stafflist in accessmask[1][pattern]:
                            securitymodulelogger.info("checking membership of %s in %s"%(username.lower(),str(stafflist)))
                            
                            if username.lower() in stafflists[stafflist]:
                                securitymodulelogger.info("setting mask to %s from match to %s using stafflist %s"%(mask,pattern,stafflist))
                                result = mask

    else:
        securitymodulelogger.info("warning : no policy for %s found in %s"%(resourcename,str(policyDict)))
        
    return result


                
        
    
def main():
    print getLSIDRuleBasedPermission(None, 'PGC.blah blah', username = 'smith', resourcename = 'information summary', \
                                     policyDict =     {
        'information summary' : 
        [
           ('deny' , {
               '.*' : None
            }),
           ('allow' , {
               '^PGC' : ['pgc','bioinformatics'],
               '^NCBI' : None
            })
        ],
        'information map' :
        [
           ('deny' , {
               '.*' : None
            }),
           ('allow' , {
               '^PGC' : ['pgc','bioinformatics'],
            })
        ]
    }, defaultResult = False)
        
if __name__ == "__main__":
   main()


