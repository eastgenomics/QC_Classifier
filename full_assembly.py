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
import json
import bin.utils as Classifier

parser = argparse.ArgumentParser(description='QC Classifier for multiqc data')
parser.add_argument('samplesheet', type=str,
                    help='Filepath to SampleSheet.csv file')
parser.add_argument('data', type=str,
                    help='filepath to multiqc.json file')
parser.add_argument('config', type=str,
                    help='filepath to config.yaml file')

args = parser.parse_args()
# List of samples
sample_sheet = args.samplesheet
MULTIQC_DATA_FILE = args.data
with open(MULTIQC_DATA_FILE, 'r', encoding='UTF-8') as file:
    multiqc_data = json.load(file)
sample_lists = Classifier.get_sample_lists(multiqc_data, sample_sheet)

# List of config_fields
YAML_FILE = args.config
yaml_content = Classifier.read_config(YAML_FILE)
config_fields = list(yaml_content["table_cond_formatting_rules"].keys())

# Generate a record for each config_field from the YAML file and
# for each sample from getSampleLists.
# IMPORTANT: May need to change order of nested for loop to optimise speed output.
def main():

    qc_report_output = {}

    for sample_list in sample_lists:

        # Script will first look at the sample_id from tuple
        sampleID = sample_list[0]
        sample_data = Classifier.get_sample_data(sampleID, multiqc_data)
        sample_summary = {}

        for config_field in config_fields:
            #print(config_field)
            headerID = Classifier.map_header_id(config_field)
            parameters = Classifier.get_unique_parameters(config_field,
                                                        yaml_content)
            value = sample_data.get(headerID)
            record_structure = []
            # If statement to apply an exception to a Unique ID that looks at percentages.
            # Parameters values are around the 100s,
            # Whereas associated values are around 1.0-0.9s
            if config_field == 'mqc-generalstats-picard-PCT_TARGET_BASES_20X':
                value = value*100

            # for all cases where value exists
            if value:
                # Get their statuses
                status = Classifier.get_status(value, parameters)
                # make record structure
                record_structure = {
                                    "sample_ID": sampleID,
                                    "value": value,
                                    "status": status
                                   }

            # If value does not exist, check if value is found in for example sample_id_L1_R1
            # First, it needs to check if there is any sample_id_reads detected
            elif sample_list[1]:
                if Classifier.get_sample_data(sample_list[1][0], multiqc_data).get(headerID):
                    sample_read_list = sample_list[1]
                    # If value found, then retrieve value and status for all elements in tuple
                    # (sample_id_L1_R1, sample_id_L1_R2, sample_id_L2_R1, sample_id_L2_R2)
                    for readID in sample_read_list:
                        sample_data = Classifier.get_sample_data(readID, multiqc_data)
                        value = sample_data.get(headerID)
                        status = Classifier.get_status(value, parameters)

                        # Make record structure list
                        record_call = {
                                        "sample_ID": readID,
                                        "value": value,
                                        "status": status
                                      }

                        record_structure.append(record_call)
                else:
                    print(f"Config field {config_field} not found in sample data {sampleID}")
            else:
                print(f"Config field {config_field} not found in sample data",
                    f"{sampleID}.\nAlso no sample reads detected.")

            if record_structure:
                message_from_classifier = {
                                            headerID:{
                                                      "thresholds": parameters,
                                                      "record": record_structure
                                                     }
                                           }

                sample_summary.update(message_from_classifier)

        qc_report_output.update({sampleID:sample_summary})

    with open('qc_report.json', 'w', encoding='UTF-8') as output_filename:
        json.dump(qc_report_output, output_filename)

if __name__ == "__main__":
    main()
