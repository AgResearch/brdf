#
# General purpose application level exception 
#
import exceptions

class brdfException(exceptions.Exception):
    def __init__(self,args=None):
        super(brdfException, self).__init__(args)
