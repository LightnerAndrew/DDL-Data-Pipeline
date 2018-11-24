

from .__init__ import *
from .push_data import find_rev_number, push_metadata, apply_revision
from .helpers import DictQuery, nested_set, find_path, iter_paths
from .metadata import *  



class edit_asset(auth):

    # define parameters
    name = 'asset name'
    description = 'asset descripton'
    uid = 'usaid_uid'
    fourfour = 'four-four'
    parent = False
    associated_datasets = None

    def find_rev_number(self):
        '''
        Access the revision number to the asset. 
        '''
        self.rev_number = find_rev_number(self.fourfour, self.link, self.username, self.password)

        return self.rev_number




    def access_metadata(self):
        '''
        This function access the view of the dataset and replaces the name, uid, parent, and associated datasets attributes with 
        the values on the socrata platform for a given asset. 
        '''
        
        # access metadata via the sodapy get_metadata function (attached the the client created in the auth class)
        metadata = self.client.get_metadata(self.fourfour)

        # set the basic fields 
        self.name = metadata['name']
        self.description = metadata['description']
        self.parent = DictQuery(metadata).get("metadata|isParent")
        self.uid = DictQuery(metadata).get("privateMetadata|custom_fields|USAID Use Only|USAID GUID")
        
        # access the ids of datasets if they exist 
        links = DictQuery(metadata).get("metadata|additionalAccessPoints")


        if links != None: 
            self.child_fourfours = [links[i]['uid'] for i in range(0, len(links)) if len(links[i].keys()) != 0]
            self.child_names = [links[i]['uid'] for i in range(0, len(links)) if len(links[i].keys()) != 0]
        else: 
            self.child_fourfours = []
            self.child_names = []


        # save all the metadata for future use
        self.metadata = metadata

        return metadata




    def find_url(self): 
        '''
        Find the url for the asset of interest. 
        '''
        if self.prod == False: 
            url = 'https://{}/d/{}'.format(self.link, self.fourfour)
        else: 
            url = 'https://data.usaid.gov/d/{}'.format(self.fourfour)


        return url




class edit_metadata(edit_asset):

    # set parameters
    _from = '{}'
    _to = '{}'
    _to_fordatasets = ''
    field = ''
    change_datasets = False
    new_field = False


    def check_fieldname(self): 
        '''
        This function checks whether the field name provided exists within the current asset. 
        If not, the user will have to specify 'new_field' as true and the `fix_error_in_field()` function
        will not work.

        : 
        '''
        return find_path(self.metadata, self.field)
        

    def perform_field_edits(self, quiet = True, replace=True):
        '''
        Edit a portion of a field where there was previously was a field input. 

        :param replace: to replace the entire field to the edit_metadata._to attribute or to replace only the string in the edit_metadata._from attribute to the _to attribute. 
        :type replace: bool.
        :param quiet: print the results of the edits; default = False. 
        :type quiet: bool. 

        >>> edit_metadata().edit_field(replace=True) 

        return 
            response
        
        '''
        # find the revision number for the asset 
        self.rev_number = find_rev_number(self.fourfour, self.link, self.username, self.password)

        # define fix errors in field 
        field_path = find_path(self.metadata, self.field)

        # access previous value 
        prior = DictQuery(self.metadata).get(field_path)

        if replace==False: 
            new = prior.replace(self._from, self._to)
        else: 
            new = self._to

        # create the new dictionary using string manipulation 
        new_metadata = {}
        nested_set(new_metadata, field_path.split('|'), new)

        # add the 'metadata' header to the dictionary. 
        new_metadata = {'metadata': new_metadata}

        # push and apply the edits to socrata, push_metadata function is form the push.py 
        r = push_metadata(self.fourfour, self.link, self.username, self.password, new_metadata, self.rev_number)
        r = apply_revision(self.fourfour, self.link, self.username, self.password, self.rev_number)

        if quiet == False: 

            print(self.name)
            print(r)
            print('')

        # make associated change changes in datasets if promted 
        if self.change_datasets == True:
            
            # create list of child uids 
            for child_44 in self.child_fourfours: 
                
                # find revision number for the child
                rev_number = find_rev_number(child_44, self.link, self.username, self.password)

                # create a new replace if the dataset has a different add-on to the string ({string},)
                if replace == False: 
                    new = prior.replace(self._from, self._to+self._to_fordatasets)
                else: 
                    new = self._to

                # create a new dictionary to push in the metadata change. 
                new_metadata = {}
                nested_set(new_metadata, field_path.split('|'), new)

                # add the 'metadata' header to the dictionary.
                new_metadata = {'metadata': new_metadata}


                r = push_metadata(child_44, self.link, self.username, self.password, new_metadata, rev_number)
                r = apply_revision(child_44, self.link, self.username, self.password, rev_number)

                if quiet == False: 
                    print(child_44)
                    print(r)
                    print('')

        return r




                


                


        




        

        
