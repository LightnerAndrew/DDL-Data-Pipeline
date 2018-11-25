'''
Metadata
========


'''

# import local functions 
from .push_data import *



    

def access_to_socrata_mapping(metadata):

    # the col in meta_dict/
    for col in metadata:

        type_col = type(metadata[col])

        if type_col == str:
            metadata[col] = metadata[col].replace('"', '')

    ######################################
    #### some preparation for the mapping
    ######################################

    ########### set the licence

    type_license = metadata['license']

    if type_license == 'Public Domain U.S. Government':
        license = {'name': 'Public Domain U.S. Government',
                   'termsLink': 'https://www.usa.gov/government-works'}

        licenseId = 'USGOV_WORKS'

    else:
        license = {'logoUrl': 'images/licenses/cc40bynd.png',
                   'name': 'Creative Commons Attribution | NoDerivatives 4.0 '
                   'International License',
                   'termsLink': 'http://creativecommons.org/licenses/by-nd/4.0/legalcode'}
        licenseId = 'CC_40_BY_ND'

    ############ language

    language = metadata['language'].replace(']', '')

    ############ the odd string for the indirect identifiers field

    # the string is merely a set of {value}; {value}... if indirect identfiers is 'yes'

    if metadata['Indirect_Identifiers'].lower() == 'yes':

        # then create the string entended string
        base = 'Yes; '

        if metadata['Sex or gender'].lower() == 'yes':
            base += 'Sex or gender; '

        if metadata['Religion'].lower() == 'yes':
            base += 'Religion; '

        if metadata['Race / Ethnicity'].lower() == 'yes':
            base += 'Race / Ethnicity; '

        if metadata['Geographic subdivisions smaller than a State'].lower() == 'yes':
            base += 'Geographic subdivisions smaller than a state or second level administrative boundary (Includes: district, county, city/town/village, or address as **specifically linked to an individual**); '

        if metadata['Age'].lower() == 'yes':
            base += 'Age; '

        if metadata['Marital status'].lower() == 'yes':
            base += 'Marital status; '

        # omit the last ;
        base = base[:-2]

    else:

        base = 'no'

    ############ set home page

    if metadata['landingPage'] != '':

        home_page = metadata['landingPage']
    else:
        home_page = None

    ############ USAID Initiative

    if metadata['Initiative'] != '':
        initiative = metadata['Initiative']
    else:
        initiative = None

    ########### Value of data
    value = metadata['Data_Asset_Value']
    if metadata['Data_Asset_Value'] == '':
        value = 'Submission to the Development Data Library took place before the partner was asked to provide a summary of the value of the data.'

    value_deid = metadata['De-identification_Effort']
    if metadata['De-identification_Effort'] == '':
        value_deid = 'Submission to the Development Data Library took place before the partner was asked to provide a description of de-identification efforts.'

    ##################################
    ####### generate the mapping
    ##################################

    mapping = {'metadata': {'attribution': metadata['Submitter-Organization'],
                            'category': metadata['Category'],
                            'description': metadata['description'],
                            'name': metadata['Title'],

                            'tags':  metadata['keyword'].split(','),
                            'license':  license,
                            'licenseId': licenseId,
                            'metadata':  {
        'custom_fields': {'Common Core': {'Bureau Code': "184:15",
                                          'Language': language,
                                          'Last Update': '2017-07-15',
                                          'Program Code': metadata['programCode'],
                                          'Home Page': home_page,
                                          'publisher': 'USAID',
                                          'Update Frequency': None,
                                          'Access Level Comment': 'Under the terms of an agreement with USAID, a partner owns data it collects.  Under the authority of the license partners grant to USAID, USAID posts the data with a CC-BY license providing attribution to the partner.',

                                          },

                          'Data Asset Profile': {'Countries': metadata['spatial'],
                                                 'Gender Disaggregation': metadata['Gender-Disaggregation'].lower(),
                                                 'Individual Dataset Author':  metadata['Submitter-Organization'],
                                                 'Is Certified': 'true',
                                                 'Is Classified': 'no',
                                                 'Program Cycle Component': str(metadata['Program-Cycle']),
                                                 'Sustainable Development Goal': metadata['Sustainable-Development-Goal'],
                                                 'USAID Initiative': initiative,
                                                 'Source Link': None,
                                                 },

                          'Embargo Request': {'Embargo Requested?': 'no'},

                          'Proposed Access Level': {'Proposed Access Level': 'Public'},

                          'Research Fields': {'Does this dataset contain information on human subjects?': metadata['Human-Subjects'].lower(),
                                              'Informed consent obtained?': metadata['Informed-Consent'].lower(),
                                              'Is this Federally funded research?': metadata['Fed-Funded-Research'].lower()},

                          'Submission Profile': {'Award Completion Date': str(metadata['Award-Completion-Date']),
                                                 'Award Number': metadata['Award-Number'],
                                                 'COR/AOR Email':  metadata['COR-AOR-Email'],
                                                 'COR/AOR Name': metadata['COR-AOR'],
                                                 # need a mapping from regional in access to regional here.
                                                 'Operating Unit of Origin': metadata['Operating-Unit'],
                                                 'Submitter Work Email': metadata['Submitter-Email'],
                                                 'Submitting Organization DUNS Number': str(metadata['Duns#_x']),
                                                 'USAID Alternate Contact Email': metadata['USAID-Alternative-Email'],
                                                 'USAID Alternate Contact Name': metadata['USAID-Alternative'],
                                                 'Task Order Completion Date': None,
                                                 'Alternate Submitter Name': None,
                                                 'Alternate Submitter E-mail': None,
                                                 'Task Order Number': None,
                                                 }}},

        'privateMetadata': {'contactEmail': 'opendata@usaid.gov',
                            'custom_fields': {
                                'Metadata Management': {'Informed Consent': '',
                                                        'Meta Informed Consent': None,
                                                        'Risk-Utility Submitted': value_deid,
                                                        'Other Reference Materials': None,
                                                        'Other Reference Materials Titles': None,
                                                        },
                                'Risk Assessment': {'Data on Individuals': metadata['Human-Subjects'].lower(),
                                                    'Direct Identifiers on Individuals': metadata['Direct_Identifiers'].lower(),
                                                    'Indirect Identifiers': base,  # find string create for base above
                                                    'Indirect Identifiers on Individuals': metadata['Indirect_Identifiers'].lower(),
                                                    'Level of Effort Comment': metadata['De-identification_Effort'],
                                                    # metadata['Type_of_Individuals'] ,
                                                    'Types of Individuals': 'Non-U.S. Citizens',
                                                    'Value of Data': value},
                                'Submission Profile': {'Submitter Name': metadata['Submitter-Name']},
                                'USAID Use Only': {'USAID Data Steward': metadata['Data Steward Name'],
                                                   'USAID Data Steward Email': metadata['Data Steward Email'],
                                                   'USAID GUID': metadata['Unique-Identification']},
                                'USAID Use Only - Embargo Administration': {'Embargo Decision Rational': metadata['Embargo-Rationale'],
                                                                            'Embarge Decision Date': metadata['Embargo-Date']}


                            }
                            }
    }
    }

    return mapping
