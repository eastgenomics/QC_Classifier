import mypackage.functions as Classifier
from ruamel.yaml import YAML
import json

'''
We have all the functions needed to generate the individual 
outputs that wee need, all we have to do is join everything together in
a complex dictionary. 

All inputs:
    - idUniqueIDRelationship.json
    - multiqc_data.json
    - .yaml file

Output:
We will add more complexity as we go through it but starting with the following
    {"record":["sample_ids":{"Value":1.0, "Status":"pass"}]}

Next step of complexity
    {"thresholds": parameters, "record":["sample_ids":{"Value":1.0, "Status":"pass"}]}

Future next step of complexity
    {Header_ID: {"thresholds": parameters, "record":["sample_ids":{"Value":1.0, "Status":"pass"}]}}


'''

# List of samples
multiqc_data = json.load(open("multiqc_data.json"))
sample_lists = Classifier.getSampleLists(multiqc_data)

# List of uniqueIDs
yaml_file = "CEN_multiqc_config_v2.1.0.yaml"
with open(yaml_file,'r') as file:
    yaml_content = YAML().load(file)
uniqueIDs = list(yaml_content["table_cond_formatting_rules"].keys())

# Generate a record for each uniqueID from the YAML file and for each sample from getSampleLists.
# IMPORTANT: May need to change order of nested for loop to optimise speed output.
for uniqueID in uniqueIDs:
    print(uniqueID)
    headerID = Classifier.getHeaderID(uniqueID)

    for sample_list in sample_lists:
        # Script will first look at the sample_id from tupple
        sampleID = sample_list[0]
        sample_data = Classifier.getSampleData(sampleID, multiqc_data)

        # Creating an empty variable for output .json structure
        record_structure = None

        parameters = Classifier.getUniqueParameters(uniqueID, "CEN_multiqc_config_v2.1.0.yaml")
        value = sample_data.get(headerID)

        # If statement to apply an exception to a Unique ID that looks at percentages
        # Parameters values are around the 100s
        # Whereas associated values are around 1.0-0.9s
        if uniqueID == 'mqc-generalstats-picard-PCT_TARGET_BASES_20X':
            value = value*100

        # for all casses where value exists
        if value:
            # Get their statuses
            status = Classifier.getStatus(value, parameters)
            # make record structure
            record_structure = {sampleID:{"value": value, "status": status}}
        # If value does not exist, check if value is found in for example sample_id_L1_R1
        elif Classifier.getSampleData(sample_list[1][0], multiqc_data).get(headerID):
            sample_read_list = sample_list[1]
            record_structure = []

            # If value found, then retrieve value and status for all elements in tupple
            # (sample_id_L1_R1, sample_id_L1_R2, sample_id_L2_R1, sample_id_L2_R2)
            for sample_readID in sample_read_list:
                sample_data = Classifier.getSampleData(sample_readID, multiqc_data)
                value = sample_data.get(headerID)
                status = Classifier.getStatus(value, parameters)
                # Make record structure list
                record_call = {sample_readID:{"value": value, "status": status}}
                record_structure.append(record_call)
        else:
            print(f"Unique ID {uniqueID} not found in sample data.")
            break

        if record_structure:    
            messageFromClassifier = {"thresholds": parameters,"record" : record_structure}
            print(messageFromClassifier)





