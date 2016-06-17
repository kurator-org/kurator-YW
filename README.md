kurator-YW
===========

kurator-YW repo is for SPNHC16-YW demo (and others)… 

### Introduction
Here we demonstrate how the [YesWorkflow](https://github.com/yesworkflow-org) toolkit developed by the Kurator team facilitates exploration of the results of running a simple data cleaning script written in Python on a biodiversity dataset. By analyzing the YW annotations in a script, YesWorkflow can render a prospective provenance graph of the results the script will produce when executed. Using log files easily written by such scripts, as well as annotations made in comments in a script, we will highlight how these annotations enable interpreting and querying log files in terms of the structure of the script itself. 

### Prerequisites

Python 2.7.x, YesWorkflow x.x

Note: A previous version of yesworkflow (which does not support the @log markup) can be obtained from:
```
   $ wget http://opensource.ncsa.illinois.edu/bamboo/browse/KURATOR-YW-267/artifact/JOB1/executable-jar/yesworkflow-0.2-SNAPSHOT-jar-with-dependencies.jar --no-check-certificates
```

### Repository organization

Overall sturcture of the repository: 

Directory            | Description
---------------------|------------
.                    | Python scripts, input file, and output files.
./**yw**             | YesWorkflow-generated graphs and other related configuration files.
./yw/**dlv**         | Datalog facts, rules, and queries.

#### Python scripts

The script [clean_name_date_yw.py](https://github.com/kurator-org/kurator-YW/blob/master/clean_name_date_yw.py) is the Python script with the Yesworkflow markup. The script [clean_name_date.py](https://github.com/kurator-org/kurator-YW/blob/master/clean_name_date.py) is the Python script without the Yesworkflow markup. Both scripts will generate the same output files. To see raw python of a script without the YesWorkflow markup, use: 
```
  grep -v "@" clean_name_date_yw.py | grep -v "\"\"\""
```
To save raw python of a script without the YesWorkflow markup, use: 
```
  grep -v "@" clean_name_date_yw.py | grep -v "\"\"\"" > clean_name_date.py
```

#### Input and output files
The Python script [clean_name_date_yw.py](https://github.com/kurator-org/kurator-YW/blob/master/clean_name_date_yw.py): 
- takes as input a CSV file [demo_input.csv](https://github.com/kurator-org/kurator-YW/blob/master/demo_input.csv) containing occurrence records represented using Darwin Core terms,
- by comparing with refernce of local authority source file, [demo_localDB.csv](https://github.com/kurator-org/kurator-YW/blob/master/demo_localDB.csv)
- for each input record, validates the fields of scientific name firstly and the event date secondly, 
   - replaces nonstandard or incorrect values for particular fields when the meanings or intents of these input values are unambiguous,
   - and marks records with missing values  or containing incorrect or ambiguous values for which enhancements cannot be proposed, 
- and then produces 
      - one ultimate CSV file [demo_output_name_date_val.csv](https://github.com/kurator-org/kurator-YW/blob/master/demo_output_name_date_val.csv),
      - two log files ([name_val_log.txt](https://github.com/kurator-org/kurator-YW/blob/master/name_val_log.txt) and [date_val_log.txt](https://github.com/kurator-org/kurator-YW/blob/master/date_val_log.txt)), 
         - Each of the data validation steps in the script write key information about their operations to simple log files that are easily produced without depending on software packages specific to Python. 
      - and two intermediate output files [demo_output_name_val.csv](https://github.com/kurator-org/kurator-YW/blob/master/demo_output_name_val.csv) and [record_id.txt](https://github.com/kurator-org/kurator-YW/blob/master/record_id.txt).

#### YesWorkflow-generated files
More commands and details about Yesworkflow can be found from [yw-prototypes](https://github.com/yesworkflow-org/yw-prototypes).

#### Datalog (DLV)
So far, [Datalog](http://www.dlvsystem.com/html/DLV_User_Manual.html) is used as the database system to manage the resource dependencies in Yesworkflow. It is also the query language used in this demo. 

##### Install DLV 
   The instructions for downloading DLV can be follow this [website](http://www.dlvsystem.com/dlv/). 

##### DLV Basics
   DLV user mannual can be found [here](http://www.dlvsystem.com/html/DLV_User_Manual.html).

