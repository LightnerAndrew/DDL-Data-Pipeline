'''
Metadata
========


'''

# import local functions 
from .push_data import *



def ddl_metadata_format(field_path:list, _from:str, _to:str, change_datasets:bool=False, dataset_comma:bool=False):  
    '''
    This function fixes a spelling mistake or makes a field of interest for either the data asset/dataset of interest, 
    or a data asset and all associated datasets. 
    

    :param metadata_path: list where each value is the dictionary key for the value of interest. 
    For example if I want to change the COR/AOR name, I would pass ('metadata', 'custom_fields', 'Submission Profile', 'COR/AOR Name').
    :type metadata_path: list
    :param old_value: the string within the field you would like to replace. 
    :type old_value: str
    :param new_value: the string to replace the old_value. 
    :type new_value: str
    
    return 
        
    
    '''
    
    ### build the command string 

    new_metadata = '{' 
    
    for index, field in enumerate(field_path): 

        # add the key
        to_add = "'"+field+"'"+': '
        
        # if the key is not the last one, add brackets to indicate that the key refers to another dictionary 
        if index != len(field_path)-1: 
            to_add += '{'
            
        new_metadata += to_add
    
    ### access the old field value and replace error or string with new_value 
    
    md = client.get_metadata(uid)
    
    # create the query string 
    query = 'md'
    
    for index, field in enumerate(field_path):
        
        # add the slice of the additional pieice
        query += '["'+field+'"]'
        
    full_to_replace = eval(query)
    
    # replace the part of the string you want to replace with the other 
    if dataset_comma ==True: 
        new_field_value = full_to_replace.replace(old_value+',', new_value+',')
    else: 
        new_field_value = full_to_replace.replace(old_value, new_value)
        
        
    # add new field to the command and close the dictionary 
    new_metadata += '"'+new_field_value + '"'+ '}'*len(field_path)
    
    new_metadata = {'metadata': eval(new_metadata)}
    
    
    return new_metadata






def fix_errors_in_field(uid:str, field_path:list, _from:str, _to:str, login:dict, change_datasets:bool=False, dataset_comma:bool=False):  
    '''
    This function fixes a spelling mistake or makes a field of interest for either the data asset/dataset of interest, 
    or a data asset and all associated datasets. 
    
    :param uid: the uid of the asset in socrata to change: Socrata's fourfour. 
    :type uid: str
    :param metadata_path: list where each value is the dictionary key for the value of interest. 
    For example if I want to change the COR/AOR name, I would pass ('metadata', 'custom_fields', 'Submission Profile', 'COR/AOR Name').
    :type metadata_path: list
    :param old_value: the string within the field you would like to replace. 
    :type old_value: str
    :param new_value: the string to replace the old_value. 
    :type new_value: str
    :param login: the login for Socrata; dictonary of {link, username, password}
    :type login: dict 
    :param change_datasets: whether or not to make this change in the associated datasets (if exist)
    :type change_datasets: bool 
    :param dataset_comma: whether or not to add a ',' to the end of the dataset titles to allow the replace to work.
    :type dataset_comma: bool
    
    
    return 
        
    
    '''
    
    
    ####################
    ## change metadata for the asset 
    ####################
     
    ### set the new metadata dictionary 
    new_metadata = ddl_metadata_format(field_path, _from, _to, dataset_comma=False)

    
    # find the revision 
    revision_num = find_rev_number(uid, login)
    
    # add the metadata to the asset
    asset_meta_result = add_metadata(
                                      uid  = uid, 
                                      login= login, 
                                      metadata = new_metadata, 
                                     revision_number = str(revision_num)
                                    )

    # apply the changes 
    r = apply_metadata(id = uid, 
                           login = login, 
                        revision_number = str(revision_num), 
                       prod=True
                      )
    
    
    if change_datasets == True: 
        ###########################
        #### make changes for associated datasets 
        ###########################

        # if the associatedany c datasets exist 
        #try: 
        # get the metadata
        md = client.get_metadata(uid)

        # find only the ids of the datasets 
        links = md['metadata']['additionalAccessPoints']
        
        ds_ids = [links[i]['uid'] for i in range(0, len(links)) if len(links[i].keys()) != 0] 

        # for each in ds_ids: apply the new metadata 
        for fourfour in ds_ids: 

            ### set the new metadata dictionary 
            new_metadata = build_new_metadata(fourfour, metadata_path, old_value, new_value, login, dataset_comma=False)

            # find the revision number 
            revision_num = find_rev_number(fourfour, login)

            # add the metadata to the asset
            ds_result = add_metadata2(
                                      uid  = fourfour, 
                                      login= login, 
                                      metadata = new_metadata, 
                                     revision_number = str(revision_num)
                                    )

            # apply the changes 
            r = apply_metadata(id =  fourfour, 
                                   login = login, 
                              revision_number = str(revision_num), 
                               prod=True
                              )

        #except: 
        #    print('There are no associated datasets.')
    

    print('Metadata has been updated for '+uid)
    print('')
    return 
    
