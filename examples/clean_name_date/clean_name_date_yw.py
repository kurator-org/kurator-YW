import sys
import csv
import time
from datetime import datetime
import re
import uuid

#######################################################################

"""
@begin clean_name_and_date_workflow
@in input1_data @uri file:demo_input.csv @as original_dataset
@param local_authority_source @uri file:demo_localDB.csv
@out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
@out output2_data  @uri file:demo_output_name_date_val.csv @as data_with_cleaned_names_and_dates
@out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
"""

"""
@begin clean_scientific_name @desc Clean scientificName field
@param local_authority_source @uri file:demo_localDB.csv
@in input1_data @uri file:demo_input.csv @as original_dataset
@out output1_data  @uri file:demo_output_name_val.csv @as data_with_cleaned_names
@out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
@out record_id_data @uri file:record_id.txt
"""

def clean_scientific_name():  
    
    input1_data_file_name='demo_input.csv'
    local_authority_source_file_name='demo_localDB.csv'
    output1_data_file_name='demo_output_name_val.csv'
    name_val_log_file_name='name_val_log.txt'
    record_id_file_name = 'record_id.txt'
    
    accepted_record_count = 0
    rejected_record_count = 0 
    log_record_count = 0
    output1_record_count = 0
    match_result = None
    final_result = None

    # create log file 
    """
    @begin initialize_run @desc Create the run log file
    @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
        @log {timestamp} Reading input records from {input1_data_file_name}
    """
    name_val_log = open(name_val_log_file_name,'w')    
    name_val_log.write(timestamp("Reading input records from '{0}'\n".format(input1_data_file_name))) 
    
    """
    @end initialize_run
    """
    
    """
    @begin read_scientific_name @desc Read scientificName from local authority source
    @param local_authority_source @uri file:demo_localDB.csv
    @call fieldmatch
    @out local_authority_source_scientificName_lst @as local_authority_source_scientificName_list
    """
    # create CSV reader for local_authority_source records
    local_authority_source = csv.DictReader(open('demo_localDB.csv', 'r'),
                                delimiter=',')
    # fieldnames/keys of original input data (dictionary)
    local_authority_source_fieldnames = local_authority_source.fieldnames
    
    # find corresponding column position for specified header
    scientificName_pos = fieldmatch(local_authority_source_fieldnames,'name')[1]
    authorship_pos = fieldmatch(local_authority_source_fieldnames,'author')[1]
    eventDate_pos = fieldmatch(local_authority_source_fieldnames,'date')[1]
    locality_pos = fieldmatch(local_authority_source_fieldnames,'locality')[1]
    state_pos = fieldmatch(local_authority_source_fieldnames,'state')[1]
    geography_pos = fieldmatch(local_authority_source_fieldnames,'geography')[1]
       
    # iterate over local_authority_source data records
    local_authority_source_record_num = 0
    
    # find values of specific fields
    local_authority_source_scientificName_lst = []
    local_authority_source_authorship_lst = []
    
    for local_authority_source_record in local_authority_source:
        local_authority_source_record_num += 1 
        local_authority_source_scientificName = local_authority_source_record[scientificName_pos]
        local_authority_source_scientificName_lst.append(local_authority_source_scientificName)
        local_authority_source_authorship = local_authority_source_record[authorship_pos]
        local_authority_source_authorship_lst.append(local_authority_source_authorship)
    """
    @end read_scientific_name
    """
    
    """
    @begin read_data_records @desc Read original dataset
    @in input1_data @uri file:demo_input.csv @as original_dataset
    @out original_scientificName @as scientificName
    @out original_authorship @as authorship
    @out RecordID 
    @out original_others @as other_fields
    @out record_id_data @uri file:record_id.txt
    @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
      @log {timestamp} Reading input record {RecordID}
    """
    # create CSV reader for input records
    input1_data = csv.DictReader(open('demo_input.csv', 'r'),
                                delimiter=',')

    # iterate over input data records
    record_num = 0
    RecordID_lst = []
    
    # open file for storing output data if not already open
    output1_data = csv.DictWriter(open('demo_output_name_val.csv', 'w'), 
                                      input1_data.fieldnames, 
                                      delimiter=',')
    output1_data.writeheader()
    record_id_data = open(record_id_file_name,'w')    
       
    for original1_record in input1_data:
        RecordID = str(uuid.uuid4().fields[-1])[:8]
        RecordID_lst.append(RecordID)
        record_id_data.write(RecordID + '\n')
        output1_record = original1_record
        record_num += 1
        print

        # extract values of fields to be validated
        # original_catalogNumber = original1_record['id']
        original_scientificName = original1_record['scientificName']
        original_authorship = original1_record['scientificNameAuthorship']
        name_val_log.write('\n')
        name_val_log.write(timestamp("Reading input record '{0}'\n".format(RecordID)))
        """
        @end read_data_records
        """
 
        """
        @begin check_if_name_is_nonempty @desc Check if scientificName value is present
        @in original_scientificName @as scientificName
        @out original_scientificName @as empty_scientificName
        @out original_scientificName @as nonEmpty_scientificName
        @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
                          @log {timestamp} Checking if {field_name} value is Empty - {check_result}
         """
        check_type = 'external check'
        source_used = 'local_authority_source'
        match_method = 'EXACT'
        field_name = 'scientificName'
        field_name_value = original_scientificName
        # reject the currect record if no value
        if len(original_scientificName) < 1:
            check_result = 'YES'
            match_result = None
        else:
            check_result = 'NO'
            match_result = 'FAILED'
        name_val_log.write(timestamp("Checking if scientificName value is Empty - '{0}'\n".format(check_result)))
        """
        @end check_if_name_is_nonempty
        """
        
        """
        @begin log_name_is_empty @desc Log records of empty scientific name with final status as unable to validate
        @param RecordID 
        @in original_scientificName @as empty_scientificName
        @out final_result @as record_final_status
        @out rejected_record_count @as unable-to-validate_record_count
        @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
            @log {timestamp} {final_result} the record {RecordID}
        """
        if check_result == 'YES':
            final_result = 'UNABLE-to-validate'
            name_val_log.write(timestamp("UNABLE-to-validate the record '{0}'\n".format(RecordID)))
            rejected_record_count += 1
            
            # write output record to output file
            output1_data.writerow(output1_record)
            output1_record_count += 1
            # skip to processing of next record in input file
            continue
            """
            @end log_name_is_empty
            """
        else:
            final_result = None
        
        """   
        @begin find_name_match 
            @desc Find if the scientificName matches any record in the local authority source using exact and fuzzy match
        @in original_scientificName @as nonEmpty_scientificName
        @param local_authority_source_scientificName_lst @as local_authority_source_scientificName_list
        @call exactmatch
        @call fieldmatch
        @out matching_local_authority_source_record @as matching_record
        @out match_result
        @out final_result @as record_final_status
        @out matching_method
        @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
            @log {timestamp} Trying {check_type} {source_used} {match_method} match for validating {field_name}: {field_name_value}
            @log {timestamp} {match_method} match was {match_result}, compliant with {source_used}: {compliant_result}.
        """
        name_val_log.write(timestamp("Trying external_check local_authority_source EXACT match for validating scientificName: '{0}'\n".format(original_scientificName))) 
        matching_method = None
        # first try exact match of the scientific name against local_authority_source
        matching_local_authority_source_record = exactmatch(local_authority_source_scientificName_lst, original_scientificName)[1]
        match_result = exactmatch(local_authority_source_scientificName_lst, original_scientificName)[0]
        if match_result == "SUCCESSFUL":
            name_val_log.write(timestamp("EXACT match was SUCCESSFUL, compliant with local_authority_source: SUCCESSFUL\n"))
            matching_method = match_method
            final_result = "ACCEPTED"

        # otherwise try a fuzzy match
        else:
            match_method = "FUZZY"
            name_val_log.write(timestamp("EXACT match was FAILED, compliant with local_authority_source: FAILED\n"))
            name_val_log.write(timestamp("Trying external_check local_authority_source FUZZY match for validating scientificName: '{0}'\n".format(original_scientificName)))
            matching_local_authority_source_record = fieldmatch(local_authority_source_scientificName_lst, original_scientificName)[1]
            match_result = fieldmatch(local_authority_source_scientificName_lst, original_scientificName)[0]
            if match_result == "SUCCESSFUL":
                name_val_log.write(timestamp("FUZZY match was SUCCESSFUL, compliant with local_authority_source: SUCCESSFUL\n"))
                matching_method = match_method
                final_result = "ACCEPTED"
            else:
                name_val_log.write(timestamp("FUZZY match was FAILED, compliant with local_authority_source: FAILED\n"))   
                final_result= "UNABLE-to-validate"
        """
        @end find_name_match
        """

    #########################################################
        # reject the currect record if not matched successfully against local_authority_source
        """
        @begin log_match_not_found @desc Log record where no match is found in authority source final status as unable to validate
        @param RecordID
        @in final_result @as record_final_status
        @in match_result
        @out rejected_record_count @as unable-to-validate_record_count
        @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
            @log {timestamp} {final_result} the record {RecordID}
        """
        if final_result == "UNABLE-to-validate":
            name_val_log.write(timestamp("UNABLE-to-validate the record '{0}'\n".format(RecordID)))
            rejected_record_count += 1
            
            # write output record to output file
            output1_data.writerow(output1_record)
            output1_record_count += 1
            
            # skip to processing of next record in input file
            continue
            """
            @end log_match_not_found
            """
  
     #############################################################
        """
        @begin update_scientific_name @desc Update scientificName if fuzzy match is found
        @in matching_method
        @in match_result
        @in matching_local_authority_source_record @as matching_record
        @out updated_scientificName
        """
        updated_scientificName = None
        
        # get scientific name from local_authority_source record if the taxon name match was fuzzy
        if matching_method == 'FUZZY':
            updated_scientificName = matching_local_authority_source_record
        """
        @end update_scientific_name
        """

    #####################################################################
        """
        @begin update_authorship @desc Update authorship if fuzzy match is found
        @in original_authorship @as authorship
        @in matching_method
        @in matching_local_authority_source_record @as matching_record
        @out updated_authorship
        """
        updated_authorship = None
        
        # get the scientific name authorship from the local_authority_source record if different from input record
        local_authority_source_name_authorship = local_authority_source_authorship_lst[local_authority_source_scientificName_lst.index(matching_local_authority_source_record)]
        if local_authority_source_name_authorship != original_authorship:
            updated_authorship = local_authority_source_name_authorship

        """
        @end update_authorship
        """

    #####################################################################
        # compose_output1_record
        """
        @begin log_updated_record @desc Log records updating from old value to new value
        @in updated_scientificName
        @in updated_authorship
        @in original_authorship @as authorship
        @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
            @log {timestamp} UPDATING record {Record}: {field_name} from {original_value} to {updated_value}
        """
        if updated_scientificName is not None:
            field_name = "scientificName"
            original_value = original_scientificName
            updated_value = updated_scientificName
            name_val_log.write(timestamp("UPDATING record '{0}': scientificName from '{1}' to '{2}'\n".format(
                     RecordID, original_value, updated_value)))
            output1_record['scientificName'] = updated_scientificName
            
        if updated_authorship is not None:
            field_name = "scientificNameAuthorship"
            original_value = original_authorship
            updated_value = updated_authorship
            name_val_log.write(timestamp("UPDATING record '{0}': scientificNameAuthorship from '{1}' to '{2}'\n".format(
                RecordID, original_value, updated_value)))
            output1_record['scientificNameAuthorship'] = updated_authorship
        """
        @end log_updated_record
        """
    #####################################################################
        """
        @begin log_accepted_record @desc Log record final status as accepted
        @param RecordID
        @in final_result @as record_final_status
        @out accepted_record_count
        @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
            @log {timestamp} {final_result} the record {RecordID}
        """
        name_val_log.write(timestamp("ACCEPTED the record '{0}'\n".format(RecordID)))
        accepted_record_count += 1
        """
        @end log_accepted_record
        """
        
        # write output record to output file
        """
        @begin write_data_into_file @desc Write data into a new file
        @in original_others @as other_fields
        @in original_scientificName @as scientificName
        @in original_authorship @as authorship
        @in updated_scientificName
        @in updated_authorship
        @out output1_data  @uri file:demo_output_name_val.csv @as data_with_cleaned_names
        """
        output1_data.writerow(output1_record)
        output1_record_count += 1
        """
        @end write_output1_data
        """

    """
    @begin log_summary @desc Summarize on all the records
    @in accepted_record_count
    @in rejected_record_count @as unable-to-validate_record_count
    @out name_val_log @uri file:name_val_log.txt @as name_cleaning_log
        @log {timestamp} Wrote {accepted_record_count} ACCEPTED records to {output1_data_file_name}
        @log {timestamp} Wrote {rejected_record_count} UNABLE-to-validate records to {output1_data_file_name}
    """   
    print
    name_val_log.write("\n")
    name_val_log.write(timestamp("Wrote {0} ACCEPTED records to {1}\n".format(accepted_record_count, output1_data_file_name)))
    name_val_log.write(timestamp("Wrote {0} UNABLE-to-validate records to {1}\n".format(rejected_record_count, output1_data_file_name)))
    """
    @end log_summary
    """
    
"""
@end clean_scientific_name
"""

"""
@begin clean_event_date @desc Clean eventDate field
@in output1_data  @uri file:demo_output_name_val.csv @as data_with_cleaned_names
@param record_id_data @uri file:record_id.txt
@out output2_data  @uri file:demo_output_name_date_val.csv @as data_with_cleaned_names_and_dates
@out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
"""
def clean_event_date():
    
    input2_data_file_name='demo_output_name_val.csv'
    record_id_file_name = "record_id.txt"
    output2_data_file_name='demo_output_name_date_val.csv'
    date_val_log_file_name='date_val_log.txt'
    
    accepted2_record_count = 0
    rejected2_record_count = 0
    log2_record_count = 0
    output2_record_count = 0
    match_result = None
    final_result = None
    # create log file
    """
    @begin initialize_run @desc Create the run log file
    @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
        @log {timestamp} Reading input records from {input2_data_file_name}
    """
    date_val_log = open(date_val_log_file_name,'w')    
    date_val_log.write(timestamp("Reading input records from '{0}'\n".format(input2_data_file_name)))
    
    """
    @end initialize_run
    """
        
    """
    @begin read_data_records @desc Read data with cleaned names
    @in input2_data  @uri file:demo_output_name_val.csv @as data_with_cleaned_names
    @in record_id_data @uri file:record_id.txt
    @out original2_eventDate @as eventDate
    @out RecordID 
    @out original2_others @as other_fields
    @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
                      @log {timestamp} Reading input record {RecordID}
    """
    input2_data = csv.DictReader(open('demo_output_name_val.csv', 'r'),
                                delimiter=',')
    # iterate over input data records
    record2_num = 0
    RecordID_lst = []
    record_id_data = open(record_id_file_name, 'r') 
    for line in record_id_data:
        line = line.rstrip('\n')
        RecordID_lst.append(line)
    
    # open file for storing output data if not already open
    output2_data = csv.DictWriter(open('demo_output_name_date_val.csv', 'w'), 
                                      input2_data.fieldnames, 
                                      delimiter=',')
    output2_data.writeheader()
    
    for original2_record, ReID in zip(input2_data, RecordID_lst):
        RecordID = ReID
        output2_record = original2_record
        record2_num += 1
        print

        # extract values of fields to be validated
        original2_eventDate = original2_record['eventDate']

        date_val_log.write('\n')
        date_val_log.write(timestamp("Reading input record '{0}'\n".format(RecordID)))        
        """
        @end read_input2_data_records
        """
        
        """
        @begin check_if_date_is_nonempty @desc Check if eventDate value is present
        @in original2_eventDate @as eventDate
        @out original2_eventDate @as empty_eventDate
        @out original2_eventDate @as nonEmpty_eventDate
        @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
                       @log {timestamp} Checking if {field_name} value is Empty: {check_result}       
        """
        check_type = 'self_check'
        source_used = 'ISO_date_format-(YYYY-MM-DD)'
        match_method = 'EXACT'
        field_name = 'eventDate'
        field_name_value = original2_eventDate
        # reject the currect record if no value
        if len(original2_eventDate) < 1:
            check_result = 'YES'
            match_result = None
        else: 
            check_result = 'NO'
            match_result = 'FAILED'
        date_val_log.write(timestamp("Checking if eventDate value is Empty: '{0}'\n".format(check_result)))
        """
        @end check_if_date_is_nonempty 
        """
        
        """
        @begin log_date_is_empty @desc Log records of empty event date with final status as unable to validate
        @param RecordID 
        @in original2_eventDate @as empty_eventDate
        @out rejected2_record_count @as unable-to-validate_record_count
        @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
            @log {timestamp} {final_result} the record {RecordID}
        """
        
        if check_result == 'YES':
            final_result = 'UNABLE-to-validate'
            date_val_log.write(timestamp("UNABLE-to-validate the record '{0}'\n".format(RecordID)))
            rejected2_record_count += 1
            
            # write output record to output file
            output2_data.writerow(output2_record)
            output2_record_count += 1
            # skip to processing of next record in input file
            continue
            """
            @end log_date_is_empty
            """
        else:
            final_result = 'ACCEPTED'
                    
        """
        @begin check_ISO_date_compliant 
            @desc Check if the eventDate is compliant with ISO date format (YYYY-MM-DD)
        @in original2_eventDate @as nonEmpty_eventDate
        @out original2_eventDate @as compliant_eventDate
        @out original2_eventDate @as nonCompliant_eventDate
        @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
                       @log {timestamp} Trying {check_type} {source_used} {match_method} match for validating {field_name}: {field_name_value}            
                       @log {timestamp} {match_method} match was {match_result}, compliant with {source_used}: {match_result}.
        """                
        date_val_log.write(timestamp("Trying self_check ISO_date_format-(YYYY-MM-DD) EXACT match for validating eventDate: '{0}'\n".format(original2_eventDate)))
        # date format: xxxx-xx-xx
        if re.match(r'^(\d{4}\-)+(\d{1,2}\-)+(\d{1,2})$',original2_eventDate):
            match_result = 'SUCESSFUL'
            compliant_eventDate = original2_eventDate
            date_val_log.write(timestamp("EXACT match was SUCESSFUL, compliant with ISO_date_format-(YYYY-MM-DD): SUCCESSFUL\n"))
        # date format: xxxx-xx-xx/xxxx-xx-xx
        elif re.match(r'^(\d{4}\-)+(\d{1,2}\-)+(\d{1,2}\/)+(\d{4}\-)+(\d{1,2}\-)+(\d{1,2})$',original2_eventDate):
            match_result = 'SUCESSFUL'
            compliant_eventDate = original2_eventDate
            date_val_log.write(timestamp("EXACT match was SUCESSFUL, compliant with ISO_date_format-(YYYY-MM-DD): SUCCESSFUL\n"))
        else: 
            match_result = 'FAILED'
            nonCompliant_eventDate = original2_eventDate
            date_val_log.write(timestamp("EXACT match was FAILED, compliant with ISO_date_format-(YYYY-MM-DD): FAILED\n"))
        """
        @end check_ISO_date_compliant
        """
            
        """
        @begin update_event_date @desc Update eventDate by date format conversion
        @in original2_eventDate @as nonCompliant_eventDate
        @out updated2_eventDate @as updated_eventDate
        @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
                          @log {timestamp} UPDATING record {Record}: {field_name} from {original_value} to {updated_value} 
        """
        updated2_eventDate = None
        # date format: xx/xx/xx
        if match_result == "FAILED":
            if re.match(r'^(\d{1,2}\/)+(\d{1,2}\/)+(\d{4})$',original2_eventDate):
                dateparts_slash = original2_eventDate.split('/')
                par0 = dateparts_slash[0]
                par1 = dateparts_slash[1]  
                par2 = dateparts_slash[2]
                par_mon = par0.zfill(2)
                par_day = par1.zfill(2)
                par_yr = par2
                updated2_eventDate = par_yr + '-' + par_mon + '-' + par_day
                field_name = "eventDate"
                original_value = original2_eventDate
                updated_value = updated2_eventDate
                date_val_log.write(timestamp("UPDATING record '{0}': eventDate from '{1}' to '{2}'\n".format(RecordID, original2_eventDate, updated2_eventDate)))
                output2_record['eventDate'] = updated2_eventDate
            elif re.match(r'^(\d{1,2}\/)+(\d{1,2}\/)+(\d{2})$',original2_eventDate):
                dateparts_slash = original2_eventDate.split('/')
                par0 = dateparts_slash[0]
                par1 = dateparts_slash[1]  
                par2 = dateparts_slash[2]
                par_mon = par0.zfill(2)
                par_day = par1.zfill(2)
                par_yr = par2
                prefix_yr = '19'
                fix_yr = prefix_yr + par2
                updated2_eventDate = fix_yr + '-' + par_mon + '-' + par_day
                field_name = "eventDate"
                original_value = original2_eventDate
                updated_value = updated2_eventDate
                date_val_log.write(timestamp("UPDATING record '{0}': eventDate from '{1}' to '{2}'\n".format(RecordID, original2_eventDate, updated2_eventDate)))
                output2_record['eventDate'] = updated2_eventDate
                
        """
        @end update_event_date       
        """
                
        """
        @begin log_accepted_record @desc Log record final status as accepted
        @param RecordID
        @in updated2_eventDate @as updated_eventDate
        @in original2_eventDate @as compliant_eventDate
        @out accepted2_record_count @as accepted_record_count
        @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
            @log {timestamp} {final_result} the record {RecordID}
        """
        date_val_log.write(timestamp("ACCEPTED the record '{0}'\n".format(RecordID)))    
        accepted2_record_count += 1  
        """
        @end log_accepted_record
        """            
        
        # write output record to output file
        """
        @begin write_data_into_file @desc Write data into a new file
        @in original2_others @as other_fields
        @in updated2_eventDate @as updated_eventDate
        @in original2_eventDate @as eventDate
        @out output2_data  @uri file:demo_output_name_date_val.csv @as data_with_cleaned_names_and_dates
        """
        output2_data.writerow(output2_record)
        output2_record_count += 1
        """
        @end write_output2_data
        """
        
    """
    @begin log_summary @desc Summarize on all the records
    @in accepted2_record_count @as accepted_record_count
    @in rejected2_record_count @as unable-to-validate_record_count
    @out date_val_log @uri file:date_val_log.txt @as date_cleaning_log
                   @log {timestamp} Wrote {accepted2_record_count} accepted records to {output2_data_file_name}
                   @log {timestamp} Wrote {rejected2_record_count} UNABLE-to-validate records to {rejected2_data_file_name}
    """
    print
    date_val_log.write("\n")
    date_val_log.write(timestamp("Wrote {0} accepted records to {1}\n".format(accepted2_record_count, output2_data_file_name)))
    date_val_log.write(timestamp("Wrote {0} UNABLE-to-validate records to {1}\n".format(rejected2_record_count, output2_data_file_name)))
    """
    @end log_summary
    """

"""
@end clean_event_date               
"""

"""
@end clean_name_and_date_workflow
"""

"""    
@begin exactmatch
@param lst
@param label_str
@return key
@return None            
"""
def exactmatch(lst, label_str):
    match_result = "FAILED"
    matching_record = None
    for key in lst:
        if key.lower() == label_str.lower():
            match_result = 'SUCCESSFUL'
            matching_record = key
            break
    return [match_result,matching_record]
"""
@end exactmatch
"""

"""
@begin fuzzymatch
@param str1
@param str2
@return [match_result, str1[x_longest - longest: x_longest], x_longest - longest]            
"""
def fuzzymatch(str1, str2):
    match_result = "FAILED"
    len1 = len(str1)
    len2 = len(str2)
    str1 = str1.lower()
    str2 = str2.lower()
        
    counter = [[0] * (1 + len2) for k in range(1 + len1)]
    longest = 0
    x_longest = 0
    for i in range(1, 1 + len(str1)):
        for j in range(1, 1 + len(str2)):
            if str1[i - 1] == str2[j - 1]:
                counter[i][j] = counter[i - 1][j - 1] + 1
                if counter[i][j] > longest:
                    longest = counter[i][j]
                    x_longest = i
            else:
                counter[i][j] = 0
    
    if longest > min(len(str1),len(str2))/2:
        match_result = 'SUCCESSFUL'
    
    return [match_result, str1[x_longest - longest: x_longest], x_longest - longest]
    
"""
@end fuzzymatch
"""
 
"""
@begin fieldmatch
@param lst
@param str2
@call fuzzymatch
@return match_str            
 """
def fieldmatch(lst, str2):
    matching_str = None
    for str in lst: 
        match_result = fuzzymatch(str, str2)[0]
        if match_result == 'SUCCESSFUL':
            matching_str = str
            break
    return [match_result,matching_str]
"""
@end fieldmatch
"""   
    

"""
@begin timestamp
@param message
@return timestamp_message
"""            
def timestamp(message):
    current_time = time.time()
    timestamp = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d-%H:%M:%S')
    print "{0}  {1}".format(timestamp, message)
    timestamp_message = (timestamp, message)
    return '  '.join(timestamp_message)
"""
@end timestamp
"""

if __name__ == '__main__':
    """ Demo of clean_name_and_date_workflow script """
    clean_scientific_name()
    clean_event_date()
