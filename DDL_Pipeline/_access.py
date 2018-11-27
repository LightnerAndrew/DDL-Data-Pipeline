

from .__init__ import *
from .helpers import DictQuery, nested_set, find_path, iter_paths
'''
_access
========
'''


class access_asset(auth):
    '''



    '''
    # define parameters
    asset_name = 'asset name'
    asset_description = 'asset descripton'
    asset_uid = 'usaid_uid'
    asset_fourfour = 'four-four'
    isParent = True
    associated_datasets = []
    datasets = []

    def get_metadata(self):
        '''
        This function access the view of the dataset and replaces the name, uid, parent, and associated datasets attributes with 
        the values on the socrata platform for a given asset. 
        '''
        
        # access metadata via the sodapy get_metadata function (attached the the client created in the auth class)
        metadata = self.client.get_metadata(self.asset_fourfour)

        # set the basic fields 
        self.asset_name = metadata['name']
        self.asset_description = metadata['description']
        try: 
            self.isParent = DictQuery(metadata).get("metadata|isParent")
            self.asset_uid = DictQuery(metadata).get("privateMetadata|custom_fields|USAID Use Only|USAID GUID")
            
            # access the ids of datasets if they exist 
            links = DictQuery(metadata).get("metadata|additionalAccessPoints")
            self.associated_datasets = links

            if links != None: 
                self.child_fourfours = [links[i]['uid'] for i in range(0, len(links)) if len(links[i].keys()) != 0]
                self.child_names = [links[i]['title'] for i in range(0, len(links)) if len(links[i].keys()) != 0]
            else: 
                self.child_fourfours = []
                self.child_names = []

        except: 
            Exception('The asset is missing key metadata fields.')


        # save all the metadata for future use
        self.metadata = metadata

        return metadata

    def get_data(self, join=True):
        '''
        The get_data() function accesses the data in the asset specified via the `access_asset()` 
        '''
        
        datasets = []
        for index, ds_fourfour in enumerate(self.child_fourfours): 
            
            # download the data in json format. 
            data = self.client.get(ds_fourfour)

            # access column descriptions
            md = self.client.get_metadata(ds_fourfour)
            col_descriptions = {md['columns'][i]['fieldName']: md['columns'][i]['description'] for i in range(0, len(md['columns']))}

            # turn json into a pandas dataframe
            data = pd.DataFrame.from_records(data)

            # append results to datasets 
            datasets.append({
                            'name': self.child_names[index], 
                            'fourfour': ds_fourfour, 
                            'data': data, 
                            'description': md['description'], 
                            'column_labels': col_descriptions
                            })
                        
        self.datasets = datasets 
        
        return datasets


    def get_attachments(self): 
        '''
        Download the attachemnts to the data asset or dataset of interest. 
        '''
        return



    def save_asset(sefl, folder_path:str): 
        '''
        To save the asset in the directory of choice. The save_asset function also accesses the attachments of the asset. 
        :folder_path: 
        '''


        return 


        




        

        
