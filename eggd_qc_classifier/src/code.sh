#!/bin/bash
# eggd_QC_Classifier 0.0.1
# Generated by dx-app-wizard.



# Basic execution pattern: Your app will run on a single machine from
# beginning to end.
#
# Your job's input variables (if any) will be loaded as environment
# variables before this script runs.  Any array inputs will be loaded
# as bash arrays.
#
# Any code outside of main() (or any entry point you may add) is
# ALWAYS executed, followed by running the entry point itself.
#
# See https://documentation.dnanexus.com/developer for tutorials on how
# to modify this file.

main() {

    echo "Value of sample_sheet: '$sample_sheet'"
    echo "Value of multiqc_data: '$multiqc_data'"
    echo "Value of config_file: '$config_file'"

    # The following line(s) use the dx command-line tool to download your file
    # inputs to the local file system using variable names for the filenames. To
    # recover the original filenames, you can use the output of "dx describe
    # "$variable" --name".

    dx download "$sample_sheet" -o sample_sheet

    dx download "$multiqc_data" -o multiqc_data

    dx download "$config_file" -o config_file

    # Fill in your application code here.
    #
    # To report any recognized errors in the correct format in
    # $HOME/job_error.json and exit this script, you can use the
    # dx-jobutil-report-error utility as follows:
    #
    #   dx-jobutil-report-error "My error message"
    #
    # Note however that this entire bash script is executed with -e
    # when running in the cloud, so any line which returns a nonzero
    # exit code will prematurely exit the script; if no error was
    # reported in the job_error.json file, then the failure reason
    # will be AppInternalError with a generic error message.

    sudo -H python3 -m pip install --no-index --no-deps packages/*

    python3 full_assembly.py sample_sheet multiqc_data config_file

    # The following line(s) use the dx command-line tool to upload your file
    # outputs after you have created them on the local file system.  It assumes
    # that you have used the output field name for the filename for each output,
    # but you can change that behavior to suit your needs.  Run "dx upload -h"
    # to see more options to set metadata.

    qc_report_json=$(find . -name "*multiqc.json")

    echo File $qc_report_json created.

    qc_report_json=$(dx upload $qc_report_json --brief)

    # The following line(s) use the utility dx-jobutil-add-output to format and
    # add output variables to your job's output as appropriate for the output
    # class.  Run "dx-jobutil-add-output -h" for more information on what it
    # does.

    dx-jobutil-add-output qc_report_json "$qc_report_json" --class=file
}
