"""
We have all the functions needed to generate the individual 
outputs that we need, all we have to do is join everything together in
a complex dictionary. 

All inputs:
    - idUniqueIDRelationship.json
    - multiqc_data.json
    - config.yaml file

Output:

    {
     SampleID:[
               HeaderID:{
                         "thresholds": parameters,
                         "record":[
                                   "sample_ids":{
                                                 "value":1.0,
                                                 "status":status
                                                }
                                  ]
                        }
               ]
    }

"""
import argparse
## FUNCTIONS that may be deleted
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

def get_control_lists(multiqc_data):
    """
    Creates a structured list of controls used in the MultiQC run

    Input: 
        multiqc_data (variable which must have gone through json.load())
            i.e.: multiqc_data = json.load(open("multiqc_data.json"))

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
import json
import bin.utils as Classifier

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments

    Returns:
        args : Namespace
          Namespace of passed command line argument inputs
    """
    parser = argparse.ArgumentParser(description='QC Classifier for multiqc data')

    parser.add_argument('samplesheet', type=str,
                        help='Filepath to SampleSheet.csv file')
    parser.add_argument('data', type=str,
                        help='filepath to multiqc.json file')
    parser.add_argument('config', type=str,
                        help='filepath to config.yaml file')
    args = parser.parse_args()

    return args


def main():
    """
    Main entry point to run all functions
    """
    args = parse_args()
    # List of samples
    sample_sheet = args.samplesheet
    sample_list = Classifier.get_sample_lists(sample_sheet)

    # Multiqc data
    multiqc_data_file = args.data
    multiqc_data = Classifier.get_multiqc_data(multiqc_data_file)

    # List of config_fields
    yaml_file = args.config
    yaml_content = Classifier.read_config(yaml_file)
    config_fields = list(yaml_content["table_cond_formatting_rules"].keys())

    qc_report_output = {}
    for sample in sample_list:
        sample_summary = {}
        for config_field in config_fields:
            header_id = Classifier.map_header_id(config_field)
            parameters = Classifier.get_unique_parameters(config_field,
                                                          yaml_content)
            key_values = Classifier.get_key_value(multiqc_data,
                                                  sample,
                                                  header_id)

            if key_values:
                record = []
                for key_value in key_values:
                    key = key_value
                    value = key_values[key]
                    status = Classifier.get_status(value, parameters)
                    record_call = {
                                    "sample": key,
                                    "value": value,
                                    "status": status
                                  }
                    record.append(record_call)

                record = {
                          header_id:{
                                     "thresholds": parameters,
                                     "record": record
                                    }
                         }
                sample_summary.update(record)

        qc_report_output.update({sample:sample_summary})

    # Saving output
    with open('qc_report.json', 'w', encoding='UTF-8') as output_filename:
        json.dump(qc_report_output, output_filename)

if __name__ == "__main__":
    main()
