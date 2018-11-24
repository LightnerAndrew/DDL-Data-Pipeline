

class create(auth):
    '''
    The create class generates an new asset to be pushed to socrata.

    :attr isParent: define whether the asset is a parent (Asset) or child (dataset). Default is child: False.
    :type isParent: bool

    '''

    def push(self):

        # set the parameters

        # call the push functions

        success = True
        return success

    class asset(auth):

        # define parameters
        name = 'asset name'
        description = 'asset descripton'
        uid = 'usaid_uid'
        fourfour = 'four-four'
        parent = False
        associated_datasets = None


class edit(auth):
    '''
    The edit class allows the user to modify the data, metadata, and attachments associated
    with an asset within the Socrata plaftorm

    '''
    class asset(auth):

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
            self.asset_rev_number = find_rev_number(
                self.fourfour, self.link, self.username, self.password)

            return self.asset_rev_number

        def access_basic_metadata(self):
            '''
            This function access the view of the dataset and replaces the name, uid, parent, and associated datasets attributes with
            the values on the socrata platform for a given asset.
            '''
            x = 'need to return to this'

            return

        class datasets():
            '''
            The edit.datasets class allows the user to change the column types, delete particular rows or columns, or replace the dataset entirely.

            '''

            def soemthing(self):
                print('something')

        class metadata(object):

            class fix_error(object):

                # set parameters
                _from = '{}'
                _to = '{}'
                field_path = ['metadata', 'metadata', 'custom_fields']

                def perform(self):

                    #
                    self.metadata = {'metadata': 'soemting'}





'''
