'''
push_data library 
=================


'''



# python basics
import numpy as np
import pandas as pd  
import datetime
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import ast


# for socrata push
from socrata.authorization import Authorization
from socrata import Socrata


# local functions 


# define today 



def find_rev_number(fourfour:str, link:str, username:str, password:str)-> str: 
    '''
    Each time a change is made and accepted in socrata, the revision is created and accepted. To make a new change, the user must first create a revision at the next number. For example, if the last revision was revision 1. We neeed to create revision two. This must be specified in a string format for the function to create the correct revision.

    :param fourfour: Socrata ID which follows the format: four-four. ex: fdsf-43ewf.
    :type fourfour: str.
    :param link: the URL address of the socrata site. For dev: usaid-ddl-dev.data.socrata.com; For prod: usaid-ddl.data.socrata.com. For prod, this is the link even though the public facing website is data.usaid.gov.
    :type link: str.
    :param username: the e-mail to the socrata account.
    :type username: str.

    return 
        int: next revision number 

    '''
    # create the link
    link = 'https://{}/api/publishing/v1/revision/{}'.format(link, fourfour)
    
    # pass the link with the appropriate headers. 
    authen = HTTPBasicAuth(username, password)

    # generate new path
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    # apply the metadata changes
    r = requests.get(link, auth=authen, headers=headers)
    
    number = str(len(r.json()))
    
    return number


def push_metadata(fourfour:str, link:str, username:str, password:str, metadata:dict, revision_number:str): 
    '''
    PUT metadata for the socrata asset of choice. 

    :param fourfour: Socrata ID which follows the format: four-four. ex: fdsf-43ewf. 
    :type fourfour: str. 
    :param link: the URL address of the socrata site. For dev: usaid-ddl-dev.data.socrata.com; For prod: usaid-ddl.data.socrata.com. For prod, this is the link even though the public facing website is data.usaid.gov. 
    :type link: str. 
    :param username: the e-mail to the socrata account. 
    :type username: str. 
    :param metadata: dictionary in the format necessary to push to socrata. To find the structure, save and explore the return dictionary for the  `access_metadata()` function. Also, note that a leading 'metadata' key is necessary during the upload. Thus, a correct dictionary would be: {'metadata': {the dictionary returned from the function}}. 
    :type metadata: dict 
    :param revision_number: each time a change is made and accepted in socrata, the revision is created and accepted. To make a new change, the user must first create a revision at the next number. For example, if the last revision was revision 1. We neeed to create revision two. This must be specified in a string format for the function to create the correct revision. 
    :type revision_number: str. 

    return 
        request results(hopefully 200)
    '''


    auth = HTTPBasicAuth(username, password)
    headers = {'Content-Type': 'application/json'}

    # if a non-zero revision is selected, we must create a revision before we can  put data in the revision.
    if revision_number != '0':
        # post the revision to the uid
        r = requests.post('https://{}/api/publishing/v1/revision/{}'.format(link, fourfour), auth=auth, headers=headers)

    # put the metadata: socrata asset. 
    r=requests.put('https://{}/api/publishing/v1/revision/{}/{}'.format(link, fourfour, revision_number), auth=auth, headers=headers, data=json.dumps(metadata))


    return r


def apply_revision(fourfour: str,  link: str, username: str, password:str, revision_number: str):
    '''
    Apply any revision to a dataset. This completes the revision; if another change is necessary, create a new revision. 


    :param fourfour: Socrata ID which follows the format: four-four. ex: fdsf-43ewf.
    :type fourfour: str.
    :param link: the URL address of the socrata site. For dev: usaid-ddl-dev.data.socrata.com; For prod: usaid-ddl.data.socrata.com. For prod, this is the link even though the public facing website is data.usaid.gov.
    :type link: str.
    :param username: the e-mail to the socrata account.
    :type username: str.
    :param revision_number: each time a change is made and accepted in socrata, the revision is created and accepted. To make a new change, the user must first create a revision at the next number. For example, if the last revision was revision 1. We neeed to create revision two. This must be specified in a string format for the function to create the correct revision.
    :type revision_number: str.

    return
        request results(hopefully 200)
    '''
    
    
    auth=HTTPBasicAuth(username, password)
    headers={'Content-Type': 'application/json'}

    url='https://{}/api/publishing/v1/revision/{}/{}/apply'.format(link, fourfour, revision_number)

    response = requests.put(url, auth=auth, headers=headers)

    return response


def push_attachment(file_path:str, fourfour:str, link:str, username:str, password:str)
    '''
    Push an attachment to the socrata asset of selection. 
    
    :param file_path: relative path to the file to be pushed to sorcata. 
    :type file_path: str. 
    :param fourfour: Socrata ID which follows the format: four-four. ex: fdsf-43ewf.
    :type fourfour: str.
    :param link: the URL address of the socrata site. For dev: usaid-ddl-dev.data.socrata.com; For prod: usaid-ddl.data.socrata.com. For prod, this is the link even though the public facing website is data.usaid.gov.
    :type link: str.
    :param username: the e-mail to the socrata account.
    :type username: str.
    :param password: password to the socrata account. 
    :type password: str. 

    return 
        list in format to be added to the attachments metadata. 

    '''

    # request parameters. 
    url = 'https://{}/api/views/{}/files.txt'.format(link, fourfour)
    authen = HTTPBasicAuth(self.username, self.password)
    
    # load file 
    file = {'file': open(file_path, 'rb')}
    
    # push file to socrata 
    response = requests.post(url, files=file, auth=auth)

    # format results to be set in the metadata 
    json = response.json() 

    metadata_input = {
                    'asset_id': json['file'],
                    'filename': json['nameForOutput'],
                     }

    return metadata_input
