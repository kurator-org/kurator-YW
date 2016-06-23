import sys
import csv
import time
from datetime import datetime
import re
import uuid

#######################################################################



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
    name_val_log = open(name_val_log_file_name,'w')    
    name_val_log.write(timestamp("Reading input records from '{0}'\n".format(input1_data_file_name))) 
    
    
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
        
        if check_result == 'YES':
            final_result = 'UNABLE-to-validate'
            name_val_log.write(timestamp("UNABLE-to-validate the record '{0}'\n".format(RecordID)))
            rejected_record_count += 1
            
            # write output record to output file
            output1_data.writerow(output1_record)
            output1_record_count += 1
            # skip to processing of next record in input file
            continue
        else:
            final_result = None
        
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

    #########################################################
        # reject the currect record if not matched successfully against local_authority_source
        if final_result == "UNABLE-to-validate":
            name_val_log.write(timestamp("UNABLE-to-validate the record '{0}'\n".format(RecordID)))
            rejected_record_count += 1
            
            # write output record to output file
            output1_data.writerow(output1_record)
            output1_record_count += 1
            
            # skip to processing of next record in input file
            continue
  
     #############################################################
        updated_scientificName = None
        
        # get scientific name from local_authority_source record if the taxon name match was fuzzy
        if matching_method == 'FUZZY':
            updated_scientificName = matching_local_authority_source_record

    #####################################################################
        updated_authorship = None
        
        # get the scientific name authorship from the local_authority_source record if different from input record
        local_authority_source_name_authorship = local_authority_source_authorship_lst[local_authority_source_scientificName_lst.index(matching_local_authority_source_record)]
        if local_authority_source_name_authorship != original_authorship:
            updated_authorship = local_authority_source_name_authorship


    #####################################################################
        # compose_output1_record
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
    #####################################################################
        name_val_log.write(timestamp("ACCEPTED the record '{0}'\n".format(RecordID)))
        accepted_record_count += 1
        
        # write output record to output file
        output1_data.writerow(output1_record)
        output1_record_count += 1

    print
    name_val_log.write("\n")
    name_val_log.write(timestamp("Wrote {0} ACCEPTED records to {1}\n".format(accepted_record_count, output1_data_file_name)))
    name_val_log.write(timestamp("Wrote {0} UNABLE-to-validate records to {1}\n".format(rejected_record_count, output1_data_file_name)))
    

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
    date_val_log = open(date_val_log_file_name,'w')    
    date_val_log.write(timestamp("Reading input records from '{0}'\n".format(input2_data_file_name)))
    
        
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
        
        
        if check_result == 'YES':
            final_result = 'UNABLE-to-validate'
            date_val_log.write(timestamp("UNABLE-to-validate the record '{0}'\n".format(RecordID)))
            rejected2_record_count += 1
            
            # write output record to output file
            output2_data.writerow(output2_record)
            output2_record_count += 1
            # skip to processing of next record in input file
            continue
        else:
            final_result = 'ACCEPTED'
                    
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
                
                
        date_val_log.write(timestamp("ACCEPTED the record '{0}'\n".format(RecordID)))    
        accepted2_record_count += 1  
        
        # write output record to output file
        output2_data.writerow(output2_record)
        output2_record_count += 1
        
    print
    date_val_log.write("\n")
    date_val_log.write(timestamp("Wrote {0} accepted records to {1}\n".format(accepted2_record_count, output2_data_file_name)))
    date_val_log.write(timestamp("Wrote {0} UNABLE-to-validate records to {1}\n".format(rejected2_record_count, output2_data_file_name)))



def exactmatch(lst, label_str):
    match_result = "FAILED"
    matching_record = None
    for key in lst:
        if key.lower() == label_str.lower():
            match_result = 'SUCCESSFUL'
            matching_record = key
            break
    return [match_result,matching_record]

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
    
 
def fieldmatch(lst, str2):
    matching_str = None
    for str in lst: 
        match_result = fuzzymatch(str, str2)[0]
        if match_result == 'SUCCESSFUL':
            matching_str = str
            break
    return [match_result,matching_str]
    

def timestamp(message):
    current_time = time.time()
    timestamp = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d-%H:%M:%S')
    print "{0}  {1}".format(timestamp, message)
    timestamp_message = (timestamp, message)
    return '  '.join(timestamp_message)

if __name__ == '__main__':
    clean_scientific_name()
    clean_event_date()
