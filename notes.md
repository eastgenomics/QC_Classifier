# Notes on created functions

### How to get list of samples
```
sample_list = Classifier.get_sample_lists(args.samplesheet)
```
### How to get list of config fields
```
yaml_content = Classifier.read_config(args.config)
config_fields = list(yaml_content["table_cond_formatting_rules"].keys())
```
### How to get any parameter
```
header_id = Classifier.map_header_id(config_field)
parameters = Classifier.get_unique_parameters(config_field, yaml_content)
```
### How to get any value
```
key_values = Classifier.get_key_value(multiqc_data, sample, header_id)
```
### How to get any status
```
status = Classifier.get_status(value, parameters)
```
### .json output Structure (example)
```
{
    {
    "Summary":{
        "SampleID_1": "pass", 
        "SampleID_2": "warn"

    },
   "Details":
        {
       "SampleID_1":
            {
            "Metric_1":
                {
                "threshold": "json like structure from config file",
                "record":
                    [
                        {
                        "sample":"SampleID_1_R1",
                        "value": 1.0,
                        "status": "pass"
                        },
                        {
                        "sample":"SampleID_1_R1",
                        "value": 1.0,
                        "status": "pass"
                        }
                    ]
                }
            }   
        }
    }
}
```