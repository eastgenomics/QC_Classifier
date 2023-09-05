"""Python version 3.10.12 """
import json
import yaml
from pathlib import Path


def map_header_id(config_field):
    """
    Important concepts to understand this function:
        - Config field: Any ID found in config.yaml file found in the key called 
                     "table_cond_formatting_rules"
        - Header ID: Any ID found inside multiqc_data.json. Sometimes Config Fileds
                     and Header IDs are the same, but they are mostly different.
    
    This function gives the Header ID for any give Unique ID, 
    IMPORTANT: file "idUniqueIdRelationship.json" should be included to work.

    Input:
        - Config Field
    Output:
        - Header ID

    """
    # First get file from resources/ folder
    config_header_filepath = Path(__file__).parent.joinpath('..','resources',
                                                            'idUniqueIdRelationship.json')
    print(config_header_filepath)
    with open(config_header_filepath,
              'r', encoding='UTF-8') as file:
        config_field_relationship = json.load(file)
    id_mapping = {item["Unique_ID"]: item["Header_ID"] for item in config_field_relationship}
    header_id = id_mapping.get(config_field)

    return header_id

def read_config(yaml_file):
    """This function reads any .yaml file in a .json-like structure.

    Args:
        yaml_file (str): filename and relative path of the config.yaml file
    Output:
        - yaml_contents (dictionary): contents of config.yaml file
    """
    with open(yaml_file, 'r', encoding='UTF-8') as file:
        yaml_file = yaml.safe_load(file)
    return yaml_file

def get_unique_parameters(unique_id, yaml_file):

    """
    This function outputs the list of conditions/parameters found in the config.yaml file.

    Input:
        - Config field (str): fields found in table_cond_formatting_rules from the "config.yaml"
                              file.
        - Output from read_config('config.yaml') function.
    Output:
        - parameters (dictionary): Conditions for the given config field.

    """

    parameters = yaml_file["table_cond_formatting_rules"].get(unique_id)
    return parameters


def get_sample_lists(multiqc_data):
    '''
    Creates a structured list of samples used in the MultiQC run

    Input: 
        multiqc_data (variable which must have gone through json.load())
            - i.e.: multiqc_data = json.load(open("multiqc_data.json"))

    Output: 
        List of tuples with sample IDs for each sample patient
    
    Basic structure of one tuple:
        (sample_id, (sample_id_L1_R1, sample_id_L1_R2, sample_id_L2_R1, sample_id_L2_R2))
    '''

    # Get all IDs first
    sample_ids = multiqc_data["report_data_sources"]["VerifyBAMID"]["all_sections"].keys()
    record_ids = multiqc_data["report_data_sources"]["FastQC"]["all_sections"].keys()

    # Final output of function
    sample_lists = []

    for sample_id in sample_ids:
        record_list = []
        # Treat sample_id as a string that can be found is some IDs found in record IDs
        substring = sample_id
        for item in record_ids:
            if substring in item:
                # store record IDs in list
                record_list.append(item)
        # append sample ID with corresponding record IDs as a tupple
        sample_lists.append((sample_id,tuple(record_list)))
    return sample_lists

def get_control_lists(multiqc_data):
    """
    Creates a structured list of controls used in the MultiQC run

    Input: 
        multiqc_data (variable which must have gone through json.load())
            - i.e.: multiqc_data = json.load(open("multiqc_data.json"))

    Output: 
        Tuple with sample IDs from the multiQC.json data in 
        multiqc_happy_indel_data and multiqc_happy_snp_data

    Basic structure of output:
        ([controlSample_snp_all, controlSample_snp_pass], 
         [controlSample_indel_all, controlSample_indel_pass])
    """

    # Get all relevant IDs first
    snp_ids = multiqc_data["report_saved_raw_data"]["multiqc_happy_snp_data"].keys()
    indel_ids = multiqc_data["report_saved_raw_data"]["multiqc_happy_indel_data"].keys()

    return snp_ids, indel_ids


def get_sample_data(sample_id, multiqc_data):
    '''
    Given any kind of sample ID, retrieves its data from the multiqc_data.json file 
    (in keys "report_saved_raw_data" and "report_general_stats_data")

    Input:
        - Sample ID string (string from fuctions getControlLists or getSampleLists)
        - multiqc_data 

    Output:
        - dictionary with all data associated with given sample_id and multiqc_data
    '''
    #print(f"I got {sample_id}")

    raw_data_keys = multiqc_data["report_saved_raw_data"].keys()
    data = {}

    # If and elif statements only are applicable when given ids from getControlLists
    if "_INDEL_" in sample_id:
        data.update(multiqc_data["report_saved_raw_data"]
                                ["multiqc_happy_indel_data"].get(sample_id))
    elif "_SNP_" in sample_id:
        data.update(multiqc_data["report_saved_raw_data"]["multiqc_happy_snp_data"].get(sample_id))
    # Most sample IDs will go through the following else statement.
    else:
        for item in multiqc_data["report_general_stats_data"]:
            general_data = item.get(sample_id)
            if general_data:
                data.update(general_data)
        for key in raw_data_keys:
            raw_data = multiqc_data["report_saved_raw_data"][key].get(sample_id)
            if raw_data:
                data.update(raw_data)

    return data

def get_status(value, parameters):
    '''
    Function to determine pass/warn/fail status based on given value and parameters.

    Inputs:
        Value (string or float)
        Parameters (dictionary of parameters from function getUniqueParameters)

    Output:
        Status: string with one of the following options:
                   "unknown", "pass", "warn" or "fail" 
                Status "unknown" should be avoided.
    '''

    status = "unknown" # Given default status if not classified

    # Iterate through possible status values i.e: pass-or-true/warn/fail
    for possible_status in list(parameters.keys()):

        conditions = parameters.get(possible_status)

        # Check if one of the possible status values is a boolean == True
        if isinstance(possible_status, bool) and possible_status is True:
            # For possible status, check if it is a boolean and the boolean is equal to True
            #TODO: DISCUSS CAVEATS FOR FALSE
            # Check if the string is equal to "true"
            if value == "true":
                status = "pass"

        # Iterate through the list of conditions for each possible status: 'gt', 'lt', 'eq', 's_eq'
        for condition in conditions:

            # Checking if any of the following conditions exist
            # Or statements are necessary to prevent any condition with value
            # 0 to be treated as false
            if condition.get('gt') or condition.get('gt') == 0:
                if value > condition.get('gt'):
                    #print(f"gt than {condition['gt']}")
                    status = possible_status

            if condition.get('lt') or condition.get('lt') == 0:
                if value < condition['lt']:
                    #print(f"lt than {condition['lt']}")
                    status = possible_status

            if condition.get('eq') or condition.get('eq') == 0:
                if value == condition['eq']:
                    #print(f"eq than {condition['eq']}")
                    status = possible_status

            if condition.get('s_eq'):
                if value == condition['s_eq']:
                    #print(f"s_eq to {condition['s_eq']}")
                    status = possible_status

    return status # Returns the determined status
