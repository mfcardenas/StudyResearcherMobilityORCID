# Load libraries
import pymongo
import json
import xmltodict
import os
from pathlib import Path
import pandas as pd

def recursive_clean_function(dict_to_clean):
    """
    Function that deletes redundant words from the name of the fields of the dictionaries contained within the main one.
    This recursive function will be used in order to modify each dictionary located below the current level.
    This function does not return anything, since it modifies the original dictionary directly.
    Args:
        data_dict: information from a researcher stored in a python dictionary
    """
    # Iterate through all keys of the current dictionary
    for key_one in list(dict_to_clean):
        key_one_clean = key_one
        
        # Same cleaning process as described in clean_dict_names function
        if key_one_clean.count(':') == 1:
            key_one_clean = key_one.split(':')[1]
            dict_to_clean[key_one_clean] = dict_to_clean[key_one]
            del dict_to_clean[key_one]
        # If the current key starts with @ it is metadata that may not be relevant to query
        # and may add noise to the json that will be added to the DB, so it is deleted
        if key_one_clean[0]=='@':
            del dict_to_clean[key_one_clean]
            continue
            
        # If the fields (value associated with the current key key_one_clean) are stored in a dictionary
        if isinstance(dict_to_clean[key_one_clean], dict):
            # If the current field is a dictionary, and all the fields contained within start with "@" (metadata),
            # it will be removed from the main dictionary in order to reduce noise
            # If not, then the recursive function will be called again for the dictionary associated with key_one_clean
            if all(dict_key.startswith('@') for dict_key in list(dict_to_clean[key_one_clean])):
                del dict_to_clean[key_one_clean]
                continue
            else:
                recursive_clean_function(dict_to_clean[key_one_clean])

        # It may happen that the fields are stored in a list,
        # therefore it is required to fetch the information contained within and create a new dictionary
        # To do so, the keys will be the positions of the elements in the list
        if isinstance(dict_to_clean[key_one_clean], list):
            list_to_dict_data = {str(i):dict_to_clean[key_one_clean][i] 
                                 for i in range(len(dict_to_clean[key_one_clean]))}
            dict_to_clean.update({key_one_clean:list_to_dict_data})
            recursive_clean_function(dict_to_clean[key_one_clean])
            
            
def clean_dict_names(data_dict):
    """
    Function that deletes redundant words from the name of the fields in order to make the future queries easy to do.
    If the input is a nested dictionary, then a recursive function will be used in order to modify each dictionary
    located below the current level.
    This function does not return anything, since it modifies the original dictionary directly.
    Args:
        data_dict: information from a researcher stored in a python dictionary
    """
    for key_zero in list(data_dict):
        # Knowing that the keys always can contain one colon, if there is one then it may follow
        # the format 'person:person'. The first word is used by all the fields in the same level (excluding the ones
        # starting with'@'),
        # and the second one describes the field of interest. The last one should be maintained in order to find the fields
        # by doing easier querys
        key_zero_clean = key_zero
        if key_zero_clean.count(':') == 1:
            key_zero_clean = key_zero.split(':')[1]
            data_dict[key_zero_clean] = data_dict[key_zero]
            del data_dict[key_zero]
        
        # If data_dict is a nested dictionary, then recursion will be applied
        if isinstance(data_dict[key_zero_clean], dict):
            recursive_clean_function(data_dict[key_zero_clean])
            
            
def extract_information_from_xml(xml_dict):
    """
    Function that fetches the relevant information from the .xml file
    and returns a dictionary ready to be uploaded to the database as a document.
    If the xml file is not correct (i.e. wrong dictionary keys) an empty dictionary will be delivered.
    Args:
        xml_dict: information from a researcher stored in a dictionary
    Returns:
        researcher_data: dictionary that contains only the desired information 
        from the researcher if and only if the xml format is correct. If not, this dictionary will remain empty
    """
    researcher_data = {}
    # First ensure that the main key is 'record:record' in order to avoid reading wrong files
    if 'record:record' in xml_dict:
        # Now verify that the relevant keys are contained in the dictionary
         if all(key in xml_dict['record:record'] for key in ('person:person', 'activities:activities-summary')):
            # Extract the values for both keys and store it in a new dictionary that will contain
            # only the relevant information, and therefore avoiding noise
            researcher_data = {k: xml_dict['record:record'][k] for k in ('person:person', 'activities:activities-summary')}
            
            # In order to easily locate the document in the future (if the document needs to be updated or deleted for instance),
            # a unique id will be defined. Knowing that each person has its unique id, it will be used as the document identification,
            # since we want one document per person
            researcher_data['_id']=researcher_data['person:person']['@path'].split('/')[1]
            
            # Before adding the dictionary to the database, a function will be applied
            # in order to clean the names of the fields. This step will make the queries easier to write
            clean_dict_names(researcher_data)
                
    return researcher_data

def open_data_folders(data_folder_path, mongodb_collection):
    """
    Function that iterates over all the folders located in the given path and opens the .xml files within.
    Args:
        data_folder_path: folder that contains all the directories with the .xml
        mongodb_collection: location within the database where the documents will be stored    
    """
    # Iterate over each folder that contains .xml files
    task1 = {}
    for folder in os.listdir(data_folder_path):
        print(folder)
        # Iterate over each file and verify it has .xml format
        for file in os.listdir("".join([data_folder_path,"/",folder])):
            if not file.endswith('.xml'): 
                continue
            else:
                file_path = Path("".join([data_folder_path,"/",folder, "/", file]))
                with open(file_path, encoding='utf8') as xml_file:
                    # Transform the xml file to json, so the db input will be a dictionary
                    data_dict = xmltodict.parse(xml_file.read())
                    researcher_data = extract_information_from_xml(data_dict)
                    # Verify that the dictionary is not empty
                    if researcher_data:
                        if 'educations' in researcher_data['activities-summary']:
                            if 'affiliation-group' in researcher_data['activities-summary']['educations']:
                                # Verify if there is only one organization or there are more than one
                                # To do so, if there are many, then the main dictionary keys will be integers ('0', '1'...)
                                # If not, then the key 'last-modified-date' will be there instead of the integers
                                if 'last-modified-date' not in researcher_data['activities-summary']['educations']['affiliation-group']:
                                    for group in researcher_data['activities-summary']['educations']['affiliation-group']:
                                        group_info = researcher_data['activities-summary']['educations']['affiliation-group'][str(group)]
                                        organization = group_info['education-summary']['organization']
                                        country = organization['address']['country']
                                        if country not in task1:
                                            task1[country] = []
                                            task1[country].append(organization['name'])
                                        else:
                                            if organization['name'] not in task1[country]:
                                                task1[country].append(organization['name'])
                                else:
                                    group_info = researcher_data['activities-summary']['educations']['affiliation-group']
                                    organization = group_info['education-summary']['organization']
                                    country = organization['address']['country']
                                    if country not in task1:
                                        task1[country] = []
                                        task1[country].append(organization['name'])
                                    else:
                                        if organization['name'] not in task1[country]:
                                            task1[country].append(organization['name'])
                            
                            
                        # It may happen that the researcher has 'employments' field
                        if 'employments' in researcher_data['activities-summary']:
                            if 'affiliation-group' in researcher_data['activities-summary']['employments']:
                                # Verify if there is only one organization or there are more than one
                                # To do so, if there are many, then the main dictionary keys will be integers ('0', '1'...)
                                # If not, then the key 'last-modified-date' will be there instead of the integers
                                if 'last-modified-date' not in researcher_data['activities-summary']['employments']['affiliation-group']:
                                    for group in researcher_data['activities-summary']['employments']['affiliation-group']:
                                        group_info = researcher_data['activities-summary']['employments']['affiliation-group'][str(group)]
                                        organization = group_info['employment-summary']['organization']
                                        country = organization['address']['country']
                                        if country not in task1:
                                            task1[country] = []
                                            task1[country].append(organization['name'])
                                        else:
                                            if organization['name'] not in task1[country]:
                                                task1[country].append(organization['name'])
                                else:
                                    group_info = researcher_data['activities-summary']['employments']['affiliation-group']
                                    organization = group_info['employment-summary']['organization']
                                    country = organization['address']['country']
                                    if country not in task1:
                                        task1[country] = []
                                        task1[country].append(organization['name'])
                                    else:
                                        if organization['name'] not in task1[country]:
                                            task1[country].append(organization['name'])
    if task1:
        cols = ['Country', 'Institutions']
        rows = []
        for key, value in task1.items():
            rows.append([key, ", ".join(value).replace('"', '')])
        df = pd.DataFrame(rows, columns=cols)
        df.to_csv('informe_001.csv',encoding='utf-8-sig', index=False, sep="/")
        
def create_researchers_list(mongodb_client, data_folder_path):
    """
    Main function that aims to create a list with information from researchers stored in .xml files.
    Args:
        data_folder_path: folder that contains all the directories with the .xml
    """
    researchers_client = pymongo.MongoClient(mongodb_client)
    researchers_db = researchers_client["mydatabase"]
    researchers_col = researchers_db["universities_per_country"]
    open_data_folders(data_folder_path, researchers_col)
    
client="mongodb://localhost:27017/"
path="/BDORCID/ORCID_2021/ORCID_2021_10_summaries"