'''
DDL Data-pipeline 
=================

This code provides the Data Pipeline for the USAID Data Development Library. 

The library relies heavily on the Socrata API, socrata-py, and sodapy libraries. 

'''
# import third party packages 
from socrata.authorization import Authorization
from socrata import Socrata
import getpass
import sodapy as soda


# import local packages 
from .metadata import *
from ._edit import *




class auth(object):
    '''
    :attr prod: boolean on whether the data is pushed to the production or development instance of the DDL. 
    :type prod: bool

    '''

    # set the parameters
    prod = True
    link = 'usaid-ddl.data.socrata.com'
    api_key = 'QTmaBMt3nOu6yM4rFFLBcdkyg'

    def reset_environment(self):
        '''
        Reset between the production or development initiative after changing the prod attribute. 

        >>> auth.reset_instance()

        '''
        if self.prod == False:
            self.link = 'usaid-ddl-dev.data.socrata.com'
        else:
            self.link = 'usaid-ddl.data.socrata.com'
            

        self.auth_obj = Authorization(self.link, self.username, self.password)
        self.client = soda.Socrata(self.link, self.api_key, self.username, self.password)


    def login(self):
        '''
        Reset the password. 

        >>> auth.reset_login()

        '''

        # get the user information for the username and password
        self.username = input("Socrata user? (email address) ")
        self.password = getpass.getpass("Socrata password? ")

        # build the authentication object
        self.auth_obj = Authorization(self.link, self.username, self.password)
        self.client = soda.Socrata(self.link, self.api_key, self.username, self.password)


    def get_asset_dir(self): 

        directory = self.client.get('xz8w-ipus')

        directory = pd.DataFrame.from_records(directory)

        return directory






     
