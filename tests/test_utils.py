"""
Tests for general functions in bin/utils.py
"""
import os
import sys
import unittest


sys.path.append(os.path.abspath(
    os.path.join(os.path.realpath(__file__), '../../')
))

import bin.utils as Classifier

TEST_DATA_DIR = (
    os.path.join(os.path.dirname(__file__), 'testfiles')
)

TEST_YAML_CONTENT = {'title':'East GLH MultiQC Report',
                     'subtitle': 'Cancer Endocrine Neurology',
                     'table_cond_formatting_rules': 
                        {'mqc-generalstats-picard-PCT_TARGET_BASES_20X': 
                            {'pass':[{'lt': 101}],
                             'warn': [{'eq': 98.0}, {'lt': 98.0}],
                             'fail': [{'eq': 95.0}, {'lt': 95.0}]},
                         'METRIC_Recall_snp':
                             {'pass': [{'eq': 1.0}], 'warn': [{'lt': 1.0}],
                              'fail': [{'lt': 0.99}]},
                         'Match_Sexes':
                            {True: [{'s_eq': 'pass'}],
                                'fail': [{'s_eq': 'fail'}],
                                'warn': [{'s_eq': 'NA'}]},
                         'FOLD_ENRICHMENT': 
                                {'pass': [{'gt': 1350}, {'lt': 1750}],
                                    'warn': [{'eq': 1750}, {'gt': 1750}],
                                    'fail': [{'lt': 1350}, {'eq': 1350},
                                             {'eq': 1800}, {'gt': 1800}]},
                         'mqc-generalstats-fastqc-percent_duplicates':
                                {'pass': [{'lt': 45.0}],
                                 'warn': [{'eq': 45.0}, {'gt': 45.0}],
                                 'fail': [{'eq': 50.0}, {'gt': 50.0}]}}}


class TestMapHeaderID(unittest.TestCase):
    """
    Tests for Classifier.map_header_id(config_field)
    """
    test_inputs = [
                   'mqc-generalstats-picard-PCT_TARGET_BASES_20X',
                   'METRIC_Recall_snp',
                   'Match_Sexes',
                   'FOLD_ENRICHMENT',
                   'mqc-generalstats-fastqc-percent_duplicates'
                    ]

    def test_map_header_id(self):
        """
        Testing if outputs as expected
        """
        expected_outputs = [
                            'PCT_TARGET_BASES_20X',
                            'METRIC.Recall_snp',
                            'Match_Sexes',
                            'FOLD_ENRICHMENT',
                            'percent_duplicates'
                            ]
        output_list = []
        for config_field in self.test_inputs:
            output_list.append(Classifier.map_header_id(config_field))
        self.assertEqual(output_list, expected_outputs,
                         "Expected outputs not the same")

    def test_not_found_map_header_id(self):
        """
        Test if given config field is not found
        """
        with self.assertRaises(NameError) as context:
            Classifier.map_header_id("unknown_field")
        self.assertEqual(str(context.exception),
                         "WARNING: unknown_field does not have an associated Header ID.",
                         "Error message does not match")


class TestReadConfig(unittest.TestCase):
    """
    Tests for read_config(yaml_file)
    """

    def test_reading_file(self):
        """
        Testing if the file opens as expected
        """
        tested_output = Classifier.read_config(f"{TEST_DATA_DIR}/config_example.yaml")
        self.assertEqual(tested_output, TEST_YAML_CONTENT,
                         "The example config_example.yaml file is not read as expected")


class TesGettUniqueParameters(TestReadConfig):
    """
    Tests for get_unique_parameters(unique_id, yaml_file)
    """
    
    def test_real_config_field(self):
        example_config_field = 'FOLD_ENRICHMENT'
        tested_output = Classifier.get_unique_parameters("FOLD_ENRICHMENT",
                                                        TEST_YAML_CONTENT)
        self.assertEqual(tested_output,
                         TEST_YAML_CONTENT['table_cond_formatting_rules']
                                          [example_config_field])

    def test_unknown_config_field(self):
        example_config_field = 'GC_Content'
        with self.assertRaises(NameError) as context:
            Classifier.map_header_id("unknown_field")
        self.assertEqual(str(context.exception),
                         "WARNING: unknown_field does not have an associated Header ID.",
                         "Error message does not match")
#class TestGetUniqueParameters():


#class TestGetSampleLists():


#class TestMultiqcData():



#class TestGetKeyValue():

#class TestGetStatus():


#class TestGetOutputFilename():


if __name__=='__main__':
    unittest.main()
