##############################################################
# This module contains the base class and module level
# variables and functions for the biological resource description
# framework
#
# Author AgResearch NZ Ltd 6/2005
##############################################################

from types import *
from brdfExceptionModule import brdfException
from obmodule import ob


class op (ob):
    """ base class for all brdf op function and relation objects """
    def __init__(self):
        ob.__init__(self)

        self.obState.update({'OP' : 1})

#
# old constructor deprecated - now initialise obtuple in the initNew method
#
#    def __init__(self,obtuple):
#        """ constructor takes a tuple of one or more obs as an argument """
#        # base class does not use the obtuple
#        ob.__init__(self)
#
#        # arg must be a tuple
#        if type(obtuple) is not TupleType:
#            raise brdfException, "arg to brdf op constructor must be tuple of obs"
#
#        # arg must be a tuple of obs - check that all elements
#        # of the arg are descendants of ob. (Append True to ensure list
#        # has at least two elements)
#        aresubs = [ issubclass(type(obitem), ob) for obitem in obtuple] + [True]
#        if not reduce(lambda x,y: x&y, aresubs) :
#            raise brdfException, "arg to brdf op constructor must be tuple of objects descended from ob"
#
#
#        self.obtuple = obtuple
#
#        # now we know we are valid op can change ObState in base class
#        self.ObState ="OP"
#        
#        # ( descendants will check tuple for specific object types)
#            
