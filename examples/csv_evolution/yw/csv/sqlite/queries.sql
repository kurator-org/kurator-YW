-- .help
-- .tables
.header on
.mode column
.nullvalue [NULL]
.width 35 20 20
.output queries_output.txt

-- log queries
-- LQ1: How many times has the variable 'num' been updated? - lq1(#count).
SELECT count(DISTINCT new_value) 
FROM record_update;


-- LQ2: At which step, the variable 'num' was updated to 7? - lq2(iteration_count).
SELECT iteration_count
FROM record_update
WHERE new_value + 0 = 7;


-- LQ3: At which steps, the updated num > 5? - lq3(iteration_count).
SELECT iteration_count
FROM record_update
WHERE new_value + 0 > 5;    -- The + 0 part will force conversion to number


-- LQ4: After how many steps until the updated num > 7  - lq4(#count).
SELECT count(DISTINCT iteration_count)
FROM record_update
WHERE new_value + 0 <= 7;


-- LQ5: How did the variable 'num' change (What is the value of 'num' before and after updates) at the 3rd iteration? - lq5(old_value, new_value).
SELECT old_value, new_value
FROM record_update
WHERE iteration_count=3;


-- LQ6: How many steps were there from num = 2 to num = 7? - lq6(#count).



-- LQ7: ... And what were the intermediate values? - lq7(new_value)


-- extract queries
-- EQ1: What source files SF were YW annotations extracted from? - eq1(SourceFiles)
SELECT source_path as SourceFiles
FROM extractfacts_extract_source;
/* answer:
SourceFiles              
----------------
../evolve_csv.py
*/

-- EQ2:  What are the names PN of all program blocks? - eq2(ProgramName)
SELECT value as ProgramName
FROM extractfacts_annotation
WHERE tag='begin';

/* answer: 
ProgramName        
----------
evolve_csv
read_num  
update_num
timestamp 
*/

-- EQ3:  What out ports are qualified with URIs? - eq3(PortName)
SELECT a1.annotation_id AS uri_id, a2.annotation_id AS out_id, a2.value AS PortName
FROM extractfacts_annotation a1, extractfacts_annotation a2, extractfacts_annotation_qualifies
WHERE a1.tag='uri' AND a2.tag='out' AND extractfacts_annotation_qualifies.qualifying_annotation_id=a1.annotation_id AND extractfacts_annotation_qualifies.primary_annotation_id=a2.annotation_id;

/* answer:
uri_id,out_id,PortName
5,4,output_csv_file
7,6,evolve_log
20,19,output_csv_file
22,21,evolve_log
*/


-- model queries
-- MQ1:  Where is the definition of block 'evolve_csv.update_num'? - mq1(ProgramName, SourceFile, StartLine, Endline)
SELECT program_name AS ProgramName, qualified_program_name AS SourceFile, begin_annotation_id AS StartLine, end_annotation_id AS Endline
FROM modelfacts_program
WHERE qualified_program_name='evolve_csv.update_num';
/* answer:
ProgramName,SourceFile,StartLine,Endline
update_num,evolve_csv.update_num,15,25
*/

-- MQ2:  What is the name and description of the top-level workflow? - mq2(WorflowName, Description)
SELECT qualified_program_name AS WorflowName, desc_value AS Description
FROM top_workflow, program_description, modelfacts_program
WHERE top_workflow.program_id=program_description.program_id AND top_workflow.program_id=modelfacts_program.program_id;


-- MQ3:  What are the names of any top-level functions? - mq3(FunctionName)
SELECT qualified_program_name AS FunctionName
FROM top_function, modelfacts_program
WHERE modelfacts_program.program_id=top_function.program_id;


-- MQ4:  What are the names of the programs comprising the top-level workflow? - mq4(ProgramName)
SELECT program_name as ProgramName
FROM top_workflow, modelfacts_has_subprogram, modelfacts_program
WHERE top_workflow.program_id=modelfacts_has_subprogram.program_id AND modelfacts_has_subprogram.subprogram_id=modelfacts_program.program_id;

-- MQ5:  What are the names and descriptions of the inputs to the top-level workflow? - mq5(InputPortName, Description)
SELECT port_name AS InputPortName, description AS Description
FROM top_workflow, port_description, modelfacts_has_in_port, modelfacts_port
WHERE top_workflow.program_id=modelfacts_has_in_port.block_id AND modelfacts_has_in_port.port_id=modelfacts_port.port_id AND modelfacts_port.port_id=port_description.port_id;

-- MQ6:  What data is output by program block evolve_csv.update_num? - mq6(DataName, Description)
SELECT data_name AS DataName, description AS Description
FROM modelfacts_program, modelfacts_has_out_port, modelfacts_port, port_description, modelfacts_data
WHERE modelfacts_program.qualified_program_name='evolve_csv.update_num' AND block_id=program_id and modelfacts_has_out_port.port_id=modelfacts_port.port_id AND modelfacts_has_out_port.port_id=port_description.port_id AND modelfacts_data.data_id=modelfacts_port.data_id AND modelfacts_has_out_port.port_id=port_description.port_id; 

-- MQ7: What program blocks provide input directly to evolve_csv.update_num? - mq7(ProgramName)
SELECT DISTINCT p2.qualified_program_name
FROM modelfacts_program AS p1, modelfacts_program AS p2, modelfacts_has_in_port, modelfacts_has_out_port, modelfacts_port AS port1, modelfacts_port AS port2
WHERE p1.qualified_program_name='evolve_csv.update_num' AND modelfacts_has_in_port.block_id=p1.program_id AND port1.data_id=port2.data_id AND port1.port_id!=port2.port_id AND port2.port_id=modelfacts_has_out_port.port_id AND p2.program_id=modelfacts_has_out_port.block_id;

-- MQ8: What programs have input ports that receive data evolve_csv[num]? - mq8(ProgramName)
SELECT DISTINCT modelfacts_program.qualified_program_name
FROM modelfacts_program, modelfacts_channel, modelfacts_port_connects_to_channel, modelfacts_has_in_port,modelfacts_data
WHERE modelfacts_data.qualified_data_name='evolve_csv[num]' AND modelfacts_channel.data_id=modelfacts_data.data_id AND modelfacts_channel.channel_id=modelfacts_port_connects_to_channel.channel_id AND modelfacts_port_connects_to_channel.port_id=modelfacts_has_in_port.port_id AND modelfacts_has_in_port.block_id=modelfacts_program.program_id;


-- MQ9: How many ports read data evolve_csv[num]? - ma9(#count)
SELECT COUNT(port_id)
FROM modelfacts_data, data_in_port
WHERE qualified_data_name='evolve_csv[num]' AND modelfacts_data.data_id=data_in_port.data_id;

