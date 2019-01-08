

# python basics
import numpy as np
import pandas as pd
import time
import regex as re
import copy

# work with files
import glob
import ast
from PyPDF2 import PdfFileWriter, PdfFileReader

# for socrata push
from socrata.authorization import Authorization
from socrata import Socrata
import os
import requests
from requests.auth import HTTPBasicAuth



# local functions 
from .__init__ import *
from .helpers import access_dec_title, set_column_types, create_col_labels
from .metadata import access_to_socrata_mapping


'''
_create 
=======

'''

class create_asset(auth): 
    '''
    The create class generates an new asset to be pushed to socrata. 

    The asset class defines the broader object which will connect
    the various components of a socrata upload: metadata, data, and attachments.

    : attr name: name of the asset.
    : type name: str.
    : attr description: description of the data asset.
    : type description: str.
    : attr uid: the USAID GUID given prior to the upload.
    : type uid: str.
    : attr isParent: define whether the asset is a parent(Asset) or child(dataset). Default is child: False.
    : type isParent: bool

    '''
    # define parameters
    asset_name = 'asset name'
    asset_description = 'asset descripton'
    asset_uid = 'usaid_uid'
    isParent = False
    today = datetime.datetime.today().strftime('%Y-%m-%d-%H')
    folder_path = './'
    associated_datasets = [{}]
    datasets = []


    def read_asset_metadata(self, filename = 'asset_metadata.csv'):
        '''
        Read metadata from the .csv file with the first column as the field name and the second as the value. Place metadata in the correct format. 

        :param path: the path to the filename. Default: './'
        :type path: str. 
        :param filename: name of the csv file. Default: asset_metadata.csv
        :type filename: str. 
        '''
        # read metadata 
        metadata = pd.read_csv(self.folder_path+filename)

        # adjust for errors in metadata input.          
        metadata = metadata.fillna('')
        metadata = metadata.replace('N', 'No')
        metadata = metadata.replace('Y', 'Yes')

        # place into the dictionary format for ease of access . 
        metadata = metadata.set_index('Field').to_dict()['Value']

        # set asset attributes 
        self.asset_name = metadata['Title']
        self.asset_description = metadata['description']
        self.asset_uid = metadata['Unique-Identification'] + '-000V01'
        self.asset_metadata = access_to_socrata_mapping(metadata)
        self.informed_consent_file = metadata['Informed-Consent-Filename']
        self.consent_pagenumber = metadata['Informed-Consent-pagenumber']
        
        # return the asset metadata which will be used to 
        return metadata 


    def create_parent(self): 
        '''
        Prior to adding metadata and attachments to an parent (usaid asset), the asset must be created first. This
        step is not necessary for children or USAID datasets. 
        '''

        self.isParent = True

        # create the view of the asset 
        authen = HTTPBasicAuth(self.username, self.password)
        view_path = 'https://{}/api/views'.format(self.link)
        initial_metadata = '{"name": "'+self.asset_name+'", "metadata":{"isParent":true}}' 
        r = requests.post(view_path, auth=authen, data=initial_metadata)
        
        # save results from the create of the view 
        results = r.json()
        self.asset_fourfour = results['id']

        # publish the view of the asset 
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        publish_path = 'https://usaid-ddl.data.socrata.com/api/publishing/v1/revision/{}'.format(self.asset_fourfour)
        publish_metadata = '{"action":{"type":"replace"},"is_parent":true,"creation_source":"browser"}'

        r = requests.post(publish_path, auth=authen, data=publish_metadata, headers=headers)

        return self.asset_fourfour



    def push_attachments(self, windows=False): 
        '''
        The add_attachments() function takes all files with in the Attachments folder 
        in the folder_path directory and attaches the files to the document. 

        >>> create_asset.folder_path = './Asset/{asset_name}' # note there is not ending '/'
        >>> create_asset.add_attachments()
        '''

        filepaths = glob.glob(self.folder_path+'/Attachments/*')
        
        attachments = []

        for file_path in filepaths:

            # push the attachment to socrata, return the metadata format to add to asset metadata 
            attachment_metadata = push_attachment(file_path, self.asset_fourfour, self.link, self.username, self.password)

            split_value = '/'
            if windows == True: 
                split_value = "\\"

            # select the name from the longer file path
            name = file_path.rsplit(split_value, 1)[1]
            title = name.split('.')[0]

            # clean the title
            title = title.replace('%20', ' ')

            # check to find the DEC name
            if (len(name) == 12) and (name[-3:] == 'pdf'):
                #try:
                title = access_dec_title(title)
                #except:
                #    title = title

            # add the name and the title to the metadata dictionary 
            attachment_metadata['name'] = title

            # append to the attachments list 
            attachments.append(attachment_metadata)

        self.attachments = attachments 

        return attachments

    
    def add_consentfile(self):
        '''
        Add a file or a page within a file as the consent file. 

        :param filename: the name of the file within the Attachments folder of the folder_path directory to use as the informed consent file. 
        :type filename: str. 
        :param page_number: the page number where informed consent question is located. 
        :type page_number: str. 

        return 
            str: the string to place within the 'Informed Consent' metadata page. 
        '''

        if self.consent_pagenumber == '': 
            
            # access the socrata uid in the attachment which shared that attachement
            consent_assetid = [attach['asset_id'] for attach in self.attachments if attach['filename']==self.informed_consent_file][0]

            # create string for the award date 
            consent_metadata_value  = 'https://usaid-ddl-dev.data.socrata.com/api/views/{}/files/{} ({})'.format(self.asset_fourfour, consent_assetid, self.informed_consent_file)

        else: 

            # create the one page attachment and upload it to the asset; add to metadata attachment list. 
            # write pdf to new file - named Informed Consent Doc - {asset}.pdf
            inputpdf = PdfFileReader(open(self.folder_path+'/Attachments/'+self.informed_consent_file, "rb"))
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(int(self.consent_pagenumber)-1))
            export_path = self.folder_path+'Attachments/' + 'Informed Consent Document.pdf'
            with open(export_path, "wb") as outputStream:
                    output.write(outputStream)


            # push the pdf to socrata asset 
            consent_metadata = push_attachment(export_path, self.asset_fourfour, self.link, self.username, self.password)
            consent_metadata['name'] = 'Informed Consent Document'

            # add to the attachments 
            self.attachments.append(consent_metadata)

            # create the string to be placed in the 
            consent_metadata_value  = 'https://usaid-ddl-dev.data.socrata.com/api/views/{}/files/{} ({})'.format(self.asset_fourfour, consent_metadata['asset_id'], consent_metadata['name'])

            self.consent_metadata_value = consent_metadata_value

        return consent_metadata_value 


    def add_data(self, clean_missings: list = ['.', ' ', 'N/A', 'nan', 'missing', 'na', 'n/a'], split_data: bool = True, id_vars=[0], quiet:bool = False):
        '''
        The add_data function allows the user to load and clean the data to 
        prepare the data for being pushed to socrata. The function returns a list of dictionaries 
        in the form: `[{'name': str, 'desc': str, 'data': pd.DataFrame()}, ...]`. 

        This format is necessary because Socrata datasets cannot hold more than 350 columns. Thus, if a dataset has more than 
        350 columns the dataset must be separated. 
        
        :param clean_missings: the list of values which we replace with np.nan rather than the string form of missing. 
        :type clean_missings: list 
        :param split_data: to split the datasets if greater than 350 columns wide. 
        :type split_data: bool
        :param id_vars: the index location of the variables which identify a column in a dataset. 
        :type id_vars: list 
        :param quiet: print the progress of the dataset ingestion.
        :type quiet: bool

        return 
            list of `[{'name': str, 'desc': str, 'data': pd.DataFrame(), 'ds_num': int, 'sep_num': int, }, ...]`. 
        '''


        self.datasets = []
        # find all dataset folders within the Data folders
        dataset_folders = [folder for folder in os.walk(self.folder_path +'/Data') if folder.startswith('.')==False][0][1]
        
        if quiet == False: 
            print(dataset_folders)

        for index, ds in enumerate(dataset_folders): 
            
            if quiet == False: 
                print(ds)

            # set file to dataset 
            ds_folder_path = self.folder_path+'/Data/'+ds+'/'

            # read the metadata.csv file within the dataset folder 
            md_file = ds_folder_path + 'metadata.csv'
            ds_md = pd.read_csv(md_file).set_index('Field')

            # select key metadata
            name = ds_md.loc['distribution-title', 'Value'] 
            description = ds_md.loc['distribution-description', 'Value']
            uid = self.asset_uid +'-'+ ds_md.loc['GUID_suffix', 'Value']
            ds_file_name = ds_md.loc['distribution-downloadURL', 'Value']
            rowLabel = ds_md.loc['row', 'Value']
            codebook_name = ds_md.loc['distribution-describedBy', 'Value']
            codebook_path = ds_folder_path + codebook_name 
            codebook_columns = ds_md.loc['describedBy-columns', 'Value']

            

            ##### clean the data 

            #######  read data
            try: 
                data = pd.read_csv(ds_folder_path+'/'+ds_file_name, low_memory=False)
            except: 
                # sometimes the enconding needs to be set to latin 
                data = pd.read_csv(ds_folder_path+'/'+ds_file_name, low_memory=False, encoding = 'latin-1')

            ###### clean the data 
            data_clean = data.copy()

            for string_error in clean_missings: 
                data_clean = data_clean.replace(string_error, np.nan)

            isSame = data.equals(data_clean)

            if isSame == False: 
                ds_file_name = '_modified_'+self.today+'_' + ds_file_name
                # export the modified data for reference. 
                data.to_csv(ds_folder_path+ds_file_name, index=False)

            data_clean.columns = [col.strip() for col in data_clean.columns]

            #######################################
            ##### set the column mappings 
            #######################################

            data_columns = list(data_clean.columns)

            if codebook_columns !='[]': 

                codebook_columns = codebook_columns.replace(' ', '')

                to_adjust = [('[', '["'), (']', '"]'), (',', '","')]

                for pair in to_adjust: 
                    codebook_columns = codebook_columns.replace(pair[0], pair[1])

                column_list = ast.literal_eval(codebook_columns)
                skiprows = int(column_list[0][1])
                keepColumns = column_list[0][0]+', ' + column_list[1][0]

                # if the codebok is an excel document.
                if (codebook_path[-4:] == 'xlsx') or (codebook_path[-3:] == 'xls'):
                    # read the file as an excel
                    codes = pd.read_excel(codebook_path,
                                        skiprows=skip-1,  # subract one to account for indexing at 0,
                                          usecols=keepColumns).dropna()

                if codebook_path[-3:] == 'csv':
                    # read aas csv (generate a mapping to the excel coordinate format)
                    letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    column_maps = {letter[i]: i for i in range(0, 13)}

                    # adjust if the csv needs to be read as encoding = latin-1
                    try:
                        codes = pd.read_csv(codebook_path,
                                            skiprows=skiprows,  # subract one to account for indexing at 0,
                                            usecols=[column_maps[column_list[0][0]], column_maps[column_list[1][0]]]).dropna()

                    except:
                        codes = pd.read_csv(codebook_path,
                                            skiprows=skiprows,  # subract one to account for indexing at 0,
                                            usecols=[column_maps[column_list[0][0]],
                                                     column_maps[column_list[1][0]]],
                                            encoding='latin-1').dropna()

                # clean the columns 
                cb_cols = list(codes.columns)

                for col in list(codes.columns): 
                    codes[col] = codes[col].str.strip()

                # select only the columns which are in the data. 
                codes['ids_lower'] = [id.lower() for id in codes.iloc[:, 0].values]
                codes = codes.loc[codes['ids_lower'].isin(data_columns), :]
                codes = codes.drop_duplicates()
                col_ids = list(codes.ids_lower.values)

                num_matches = len(codes)

                # clean the descriptions
                col_desc = codes.iloc[:, 1].values # select the vlaue sof the second column
                col_desc = [str(desc).replace("'", ' ') for desc in col_desc]
                col_desc = [re.sub('[^A-Za-z0-9?,:;.()_-]+', ' ', desc).strip() for desc in col_desc]
                
                # generate a mapping 
                col_labels = {col_ids[i]: col_desc[i] for i in range(0, len(col_desc))}

            else: 
                col_labels = {}
                num_matches = 0

            
            ##### split data if necessary 

            # find the number of columns 
            num_columns = len(data_columns)

            # generate the id_dataframe which holds the ID var 
            id_df = data_clean.iloc[:, id_vars]

            if num_columns > 350: 

                rows_added = 1
                split_number = 1 
 
                while rows_added < num_columns: 
                    
                    # create the thinner dataframe
                    end = rows_added+350 
                    selection = data_clean.iloc[:, rows_added:end]
                    split_df = pd.concat([id_df, selection], axis=1)

                    # export the dataframe 
                    split_df.to_csv(ds_folder_path+ds_file_name.split('.')[0]+'-'+str(split_number)+'.csv')

                    # make the changes to the title and description 

                    # mappings 
                    ordinals = {'1': 'first', '2': 'second', '3': 'third', '4':'fourth', '5':'fifth', '6': 'sixth',
                             '7':'seventh', '8': 'eigth', '9': 'ninth', '10': 'tenth', '11': 'eleventh', '12': 'twelfth',
                             '13': 'thirteenth', '14': 'fourtheenth', '15': 'fifteenth'}
                    letters = '0abcdefghigklmnopqrstuvwxyz'

                    # generate title
                    ds_name = name + ': Section ' + str(split_number)

                    if split_number == 1: 
                        split_desc = description + ' In the process of migrating data to the current DDL platform, datasets with a large number of variables required splitting into multiple spreadsheets.  They should be reassembled by the user to understand the data fully.'
                    else: 
                        split_desc = 'In the process of migrating data to the current DDL platform, datasets with a large number of variables required splitting into multiple spreadsheets. They should be reassembled by the user to understand the data fully. This is the {} spreadsheet in the {}.'.format(ordinals[str(split_number)], name)

                    # add the letter the uid 
                    ds_uid = uid+letters[split_number]

                    # generate the dictionary 
                    ds_dict = {
                                'name': ds_name, 
                                'description': split_desc,
                                'uid': ds_uid, 
                                'data': split_df, 
                                'codebook_info':
                                 {
                                     'column_labels': col_labels, 
                                     'column_matches': num_matches, 
                                     'codebook_path': codebook_path
                                 }, 
                                 'rowLabel': rowLabel, 
                                 'split_number': split_number, 
                                 'dataset_number': index+1
                             }

                    # add to the dataset dictionary 
                    self.datasets.append(ds_dict)

                    # move the rows_added by 350 
                    rows_added = rows_added + 350 

                    split_number += 1

                

            else: 
                # if there are less than 350 columns, generate one dataset dictionary 
                    # generate the dictionary
                ds_dict = {
                    'name': name,
                    'description': description,
                    'uid': uid,
                    'data': data_clean,
                    'codebook_info':
                    {
                        'column_labels': col_labels,
                        'column_matches': num_matches,
                        'codebook_path': codebook_path
                    },
                    'rowLabel': rowLabel,
                    'split_number': -88,
                    'dataset_number': index+1
                }

                # add to the dataset dictionary
                self.datasets.append(ds_dict)

        return self.datasets


    def push_datasets(self, quiet:bool = True):
        '''
        After preparing the data using the `add_data()` method, push_datasets places the data and metadata within the 
        create_asset.datasets attribute and sets the create_asset.

        :param quiet: print the progress of the dataset ingestion.
        :type quiet: bool
        ''' 

        for index, dataset in enumerate(self.datasets): 

            ##### create the dataset
            # create revision and output
            (revision, output_schema) = Socrata(self.auth_obj).create(
                name=dataset['name'],
                description=dataset['description']
            ).df(dataset['data'])

            if quiet == False: 
                print(dataset['name']+' has been created.')

            ##### Access metadata - create the associated datasets metadata input 
            ds_fourfour = revision.attributes['fourfour']
            
            self.associated_datasets.append({
                                                'title': dataset['name'], 
                                                'description': dataset['description'], 
                                                'uid': ds_fourfour, 
                                                'urls': 
                                                {
                                                    'dataset': 'https://data.usaid.gov/d/{}'.format(ds_fourfour)
                                                }
                                            })

            

    
            ##### fix errors if they exist 

            # count the number of columns with errors
            (ok, errors) = output_schema.schema_errors()
            number_errors = len(errors)

            fail_cols = []
            # if there are errors in the upload
            if number_errors != 0:
                try:
                    # find the columns where there are errors
                    # select the columns of interest
                    for index in range(0, len(errors)):

                        keys = errors[index].keys()

                        for key in keys:

                            if list(errors[index][key].keys())[0] != 'ok':

                                fail_cols.append(key)

                    fail_columns = list(set(fail_cols))

                    # then we set the column types to the pandas
                    command_string = set_column_types(fail_columns)
                    (ok, new_output_schema) = eval(command_string)

                    # wait for changes to occur
                    (ok, output_schema) = new_output_schema.wait_for_finish()
                    assert ok, output_schema
                except:
                    print('Could not fix errors...')
      
            
            #### generate the column mappings 


            if dataset['codebook_info']['column_matches'] != 0: 

                # generate mapping from display names to id names, becuase the id names can sometime sbe different (map on id names )
                name_mapping = {output_schema.attributes['output_columns'][i]['display_name']: output_schema.attributes['output_columns'][i]['field_name'] for i in range(0, len(output_schema.attributes['output_columns']))}
                
                # generate new column_labels dictionary {field_name: label_value}
                col_labels_mapping = {}
                no_matches = 0
                for display_name in list(name_mapping.keys()): 
                    try: 
                        key = name_mapping[display_name]
                        value = dataset['codebook_info']['column_labels'][display_name]

                        col_labels_mapping[key] = value
                    except KeyError: 
                        no_matches += 1

                # generate the command string 
                command_string = create_col_labels(col_labels_mapping)

                if quiet == False: 
                    print('At column description transformation.')

                # run the command string
                (ok, new_output_schema) = eval(command_string)
                assert ok, new_output_schema

                (ok, output_schema) = new_output_schema.wait_for_finish()
                assert ok, output_schema

            # apply the revisions to the dataset 
            (ok, job) = revision.apply(output_schema=output_schema)

            #print progress
            job.wait_for_finish()

            ######## add the codebook to the attachments 
            try: 
                codebook_path = dataset['codebook_info']['codebook_path']
                codebook_name = codebook_path.rsplit('/', 1)[1]

                codebook_metadata = push_attachment(codebook_path, ds_fourfour, self.link, self.username, self.password)
                codebook_metadata['name'] = codebook_name.split('.')[0]
                print(codebook_metadata)

            except: 
                codebook_metadata = None



            ##### push dataset metadata 

            md = copy.deepcopy(self.asset_metadata)

            # make changes to the metadata for the dataset 
            md['metadata']['name'] = dataset['name']
            md['metadata']['description'] = dataset['description']
            md['metadata']['metadata']['collectionParent'] = self.asset_fourfour
            md['metadata']['metadata']['rowLabel'] = dataset['rowLabel']
            md['metadata']['privateMetadata']['custom_fields']['USAID Use Only']['USAID GUID'] = dataset['uid']
            md['attachments'] = self.attachments + [codebook_metadata]


            # push the metadata fields to socrata 
            # push and apply the edits to socrata, push_metadata function is form the push.py 
            r = push_metadata(ds_fourfour, self.link, self.username, self.password, md , '1')

            r = apply_revision(ds_fourfour, self.link, self.username, self.password, '1')
            
            if quiet=='False':
                print(r) 
                print('Metadata has been updated\n')
 


 
        return self.associated_datasets



    def push_asset_metadata(self, quiet:bool =True, rev_number:int = 0):
        '''
        This function concludes the creation of the data asset by pushing the asset metadata
        with the associated datasets. 

        :param quiet: print the progress of the asset metadata update. 
        :type quiet: bool. 

        return 
            response
        '''
        self.asset_metadata['metadata']['metadata']['additionalAccessPoints'] = self.associated_datasets
        self.asset_metadata['attachments'] = self.attachments 

        r = push_metadata(self.asset_fourfour, self.link,
                          self.username, self.password, self.asset_metadata, str(rev_number))

        r = apply_revision(self.asset_fourfour, self.link,
                           self.username, self.password, str(rev_number))

        if quiet == 'False':
            print(r)
            print('Metadata has been updated\n')


        return r




    def delete_asset(self, quiet = True): 
        '''
        Function to delete the data asset or datasets associated with the data asset. 

        :param quiet: print the results of the removal (True/False)
        :type quiet: bool. 

        return 

        '''
        delete_asset = input("Are you sure you want to delete the asset: "+self.asset_fourfour+'? (yes/no)')
        delete_dataset = input("Would you like to delete the associated datasets? (yes/no)")

        if delete_asset == 'yes':
            # detete the asset 
            r = self.client.delete(self.asset_fourfour)

            if quiet==False: 
                print(r)

        if delete_dataset == 'yes':

            # list of associated datasets 
            ds_fourfours = [ds['uid'] for ds in self.associated_datasets if ds!= {}]

            for ds in ds_fourfours: 
                r = self.client.delete(ds)

                if quiet==False: 
                    print(r)

        return r
