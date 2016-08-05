import csv
import time
from datetime import datetime

"""
@begin evolve_csv @desc Workflow for simple experiments of CSV version evolution when writing into one csv file multiple times. 
@in input_csv_file @desc input CSV file before any updates
    @uri file:original_data.csv
@out output_csv_file @desc output CSV file
    @uri file:updated_data.csv
@out evolve_log @desc log file for evolving CSV file
    @uri file:evolve_log.txt
"""

def evolve_csv():
    input_data_file_name='original_data.csv'
    output_data_file_name='updated_data.csv'
    log_file_name='evolve_log.txt'
    
    iteration_count = 0
    evolve_log = open(log_file_name,'w')
    
    for i in range (1, 10):
        """
        @begin read_num @desc Read number from input file into variable 'num'
        @in input_csv_file @uri file:original_data.csv
        @out num_old @as num
            @desc number before updating
        """
        if i == 1:
            with open(input_data_file_name, 'r') as infile:
                in_data = csv.reader(infile)
                for line in in_data:
                    # print line
                    num_old = int(line[0])
        else:
            with open(output_data_file_name, 'r') as infile:
                in_data = csv.reader(infile)
                for line in in_data:
                    # print line
                    num_old = int(line[0])
        """
        @end read_num
        """
        
        """
        @begin update_num @desc Update variable 'num' by num += 1
        @in num_old @as num
        @out output_csv_file @uri file:updated_data.csv
            @desc output CSV file
        @out evolve_log @uri file:evolve_log.txt
            @desc log file for evolving CSV file
            @log {timestamp} The {iteration_count}th update: num is {num_old}, now is {num_new}.
            @log Total iteration times: {iteration_count}.
        """
        num_new = num_old + 1
        iteration_count += 1                 
        evolve_log.write(timestamp("The {0}th update: num is {1}, now is {2}.\n".format(iteration_count, num_old, num_new)))
        with open(output_data_file_name, 'w') as outfile:
            out_data = csv.writer(outfile, delimiter=' ')
            out_data.writerow([num_new])
    evolve_log.write(timestamp("Total iteration times: {0}.\n".format(iteration_count)))
    evolve_log.close()
    """
    @end update_num
    """
    
"""
@end evolve_csv
"""
    
"""
@begin timestamp
@param message @desc the input of the defined function 
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
    evolve_csv()    