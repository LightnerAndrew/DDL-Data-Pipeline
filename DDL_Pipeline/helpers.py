
import requests
from urllib import request
import base64
import urllib
import pandas as pd


def create_col_labels(col_dict):

    start = "output_schema"

    for key in col_dict:
        add = ".change_column_metadata('"+key + \
            "', 'description').to('"+col_dict[key].replace("'", '')+"')"
        start += add
    end = ".run()"

    final_command = start+end

    return final_command



def set_column_types(list_of_fails):
    '''
    Transform all columns where ingestion errors are recorded into text columns. 
    Returns the string of a command to be run with `eval()`. 
    
    :param list_of_fails: list of columns where ingestion errors exist. 
    :type list_of_fails: list
    
    return 
        str. of command
    '''
    command = "output_schema.change_column_transform('"

    print('Errors to be fixed:')
    print(list_of_fails)

    for index, col in enumerate(list_of_fails):

        command += col+"').to('to_text(`"+col+"`)')"

        length = len(list_of_fails)

        if index != length-1:
            command += ".change_column_transform('"
        else:
            command += ".run()"

    return command



def iter_paths(d):
    def iter1(d, path):
        paths = []
        for k, v in d.items():
            if isinstance(v, dict):
                paths += iter1(v, path + [k])
            paths.append((path + [k], v))
        return paths
    return iter1(d, [])






def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value





class DictQuery(dict):
    def get(self, path, default=None):
        keys = path.split("|")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break

        return val




def find_path(md: dict, field: str) -> str:
    '''
    This function finds the path to a nested key in the format 'top/middle/field'. 

    >>> find_path(md={'the': {'example: 123}}, field = 'example')
    'the/example'


    '''
    # the iter_path function changes the dictionary into (list(path), value) format, we take the first object (list) in each observation
    paths = [result[0] for result in iter_paths(md)]

    try:
        # returns the first result in the path.
        results = [r for r in paths if r[-1] == field][0]

        # build the link.
        path = results[0]

        if 1 < len(results):
            for index, key in enumerate(results[1:]):
                path += '|'+key

    except IndexError:

        print('The field does not exist in this asset.')

        return

    return path


def dec_documents(query):
    '''
    Provided a query the in the format of the DEC API (see https://www.usaid.gov/developer/development-experience-clearinghouse-dec-api).
    return a dataset with the values of the first response.

    :param query: the query of interest from the DEC API
    :type query: str.

    return
        dataframe of first result of the search.

    '''
    # parameters
    url_start = 'http://dec.usaid.gov/api/qsearch.ashx?q='

    # encode for base64
    encode_pre = str.encode(query)
    # encode to base64
    encoded = base64.urlsafe_b64encode(encode_pre)
    # url encode
    url_encode = urllib.parse.quote(encoded)
    # return json type
    data_type = '&rtype=JSON'
    # place query together
    final_query = url_start+url_encode+data_type

    # get request
    r = requests.get(final_query)
    JSON = r.json()

    # place in dataframe
    data = pd.DataFrame()
    series = pd.DataFrame(JSON['Records'][0]).loc['value']

    # generate index column
    data['index'] = list(series.index)
    # extract values from their list if only one value.
    data['values'] = [val[0] if val != [] and len(
        val) <= 1 else val for val in series.values]

    # set index and transpose
    data = data.set_index('index').transpose().reset_index(drop=True)

    return data



def access_dec_title(doc_id):

    # change structure to match the __-___-___ pattern
    doc_id = doc_id[0:2]+'-'+doc_id[2:5]+'-'+doc_id[5:]
    print('Attempting to change ' + doc_id+' to a DEC title.')

    # get title
    title = dec_documents(
        '(Documents.Document_ID:('+doc_id+'))')['Title'].values[0]

    print(title)

    return title
