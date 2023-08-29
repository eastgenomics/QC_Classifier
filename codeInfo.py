import mypackage.functions as Classifier
from ruamel.yaml import YAML
import json

# How to get list of samples
multiqc_data = json.load(open("multiqc_data.json"))
sample_lists = Classifier.getSampleLists(multiqc_data)

# How to get any sample data
sampleID = '123991777-23187R0015-23NGCEN9-9527-F-99347387'
sample_data = Classifier.getSampleData(sampleID, multiqc_data)

# How to get list of uniqueIDs
yaml_file = "CEN_multiqc_config_v2.1.0.yaml"
with open(yaml_file,'r') as file:
    yaml_content = YAML().load(file)
uniqueIDs = list(yaml_content["table_cond_formatting_rules"].keys())

# How to get any parameter
uniqueID = "FREEMIX"
parameters = Classifier.getUniqueParameters(uniqueID, "CEN_multiqc_config_v2.1.0.yaml")

# How to get any value
headerID = Classifier.getHeaderID(uniqueID)
value = sample_data.get(headerID)

# How to get any status
status = Classifier.getStatus(value, parameters)

# .json output Structure
record_structure = {sampleID:{"value": value, "status": status}}
record_output = {"record": record_structure}
