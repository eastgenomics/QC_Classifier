import subprocess
import json
from ruamel.yaml import YAML


def getHeaderID(unique_id):
    '''
    Important concepts to understand this function:
        - Unique ID: Any ID found in config.yaml file found in the key called "table_cond_formatting_rules
        - Header ID: Any ID found inside multiqc_data.json. Sometimes Unique IDs and Header IDs are the same, but they are mostly different.
    
    This function gives the Header ID for any give Unique ID, 
    IMPORTANT: file "idUniqueIdRelationship.json" should be included to work.

    Input:
        - Unique ID
    Output:
        - Header ID

    '''
    # Use jq to extract header ID based on the current unique ID
    cmd = f'jq -r --arg UNIQUE "{unique_id}" \'first(.[] | select(.Unique_ID == $UNIQUE) | .Header_ID)\' idUniqueIdRelationship.json'
    header_id = subprocess.check_output(cmd, shell=True).decode().strip()
    return header_id


def getUniqueParameters(unique_id, yaml_file):

    '''
    This function outputs the list of conditions/parameters found in the config.yaml file.

    Input:
        - Unique ID string
        - "config.yaml" filename string
    Output:
        - parameters' dictionary for given Unique ID

    '''

    with open(yaml_file, 'r') as file:
        yaml_content = YAML().load(file)

    parameters = yaml_content["table_cond_formatting_rules"].get(unique_id)
    return parameters


def getSampleLists(multiqc_data):
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

def getControlLists(multiqc_data):
    '''
    Creates a structured list of controls used in the MultiQC run

    Input: 
        multiqc_data

    Output: 
        ([controlSample_snp_all, controlSample_snp_pass], [controlSample_indel_all, controlSample_indel_pass])
    '''

    # Get all relevant IDs first
    snp_ids = multiqc_data["report_saved_raw_data"]["multiqc_happy_snp_data"].keys()
    indel_ids = multiqc_data["report_saved_raw_data"]["multiqc_happy_indel_data"].keys()

    return snp_ids, indel_ids

def getSampleData(sample_id, multiqc_data):
    '''
    Given any kind of sample ID, retrieves its data from the multiqc_data.json file (in keys "report_saved_raw_data" and 
    "report_general_stats_data")

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
        data.update(multiqc_data["report_saved_raw_data"]["multiqc_happy_indel_data"].get(sample_id))
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

def getStatus(value, parameters):
    '''
    Function to determine the appropriate status based on given value and parameters.

    Inputs:
        Value (string or float)
        Parameters (dictionary of parameters from function getUniqueParameters)

    Output:
        Status: string with one of the following options:
                   "unknown", "pass", "warn" or "fail" 
                Status "unknown should be avoided.
    '''         

    status = "unknown" # Given default status if not classified

    # Iterate through possible status values i.e: pass-or-true/warn/fail
    for possible_status in list(parameters.keys()):

        conditions = parameters.get(possible_status)

        # Check if one of the possible status values is a boolean == True
        if possible_status == True:
            # If it is a boolean == True, check if value is a string == "true"
            # *IMPORTANT*, DISCUSS CAVEATS FOR FALSE
            if value == "true":
                status = "pass"
                continue
            else:
                # print('"The value is not a string "true"')
                continue

        # Iterate through the list of conditions for each possible status: 'gt', 'lt', 'eq', 's_eq'
        for condition in conditions:

            # Checking if any of the following conditions exist
            # Or statements are necessary to prevent any condition with value 0 to be treted as false 
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
                    status == possible_status

    return status # Returns the determined status