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
SELECT qualified_program_name AS WorflowName, description AS Description
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

-- MQ10: How many data are read by more than one port in workflow evolve_csv? - mq10(#count)
CREATE TABLE data_in_port_count AS
    SELECT data_id, count(port_id) AS port_ct
    from data_in_port
    GROUP BY data_id;
CREATE TABLE data_in_workflow_read_by_multiple_ports AS
    SELECT data_in_workflow.data_id, subprogram_id, program_id, port_ct
    FROM data_in_workflow, data_in_port_count
    WHERE port_ct>1 AND data_in_workflow.data_id=data_in_port_count.data_id;
SELECT COUNT(data_id) AS DataCount
    FROM modelfacts_program, data_in_workflow_read_by_multiple_ports
    WHERE program_name='evolve_csv' AND data_in_workflow_read_by_multiple_ports.program_id=modelfacts_program.program_id;

-- MQ11: What program blocks are immediately downstream of read_num? - mq11(DownstreamProgramName)
SELECT p1.program_name AS DownstreamProgramName
FROM program_immediately_downstream, modelfacts_program AS p1, modelfacts_program AS p2
WHERE p2.program_name='read_num' AND p1.program_id=program_immediately_downstream.program1_id;

-- MQ12: What program blocks are immediately upstream of update_num? - mq12(UpstreamProgramName)
SELECT p2.program_name AS UpstreamProgramName
FROM program_immediately_upstream, modelfacts_program AS p1, modelfacts_program AS p2
WHERE p1.program_name='update_num' AND p2.program_id=program_immediately_upstream.program1_id;

-- MQ13: What program blocks are upstream of update_num? - mq13(UpstreamProgramName)
SELECT DISTINCT pro2.program_name AS UpstreamProgramName
FROM program_upstream, modelfacts_program AS pro1, modelfacts_program AS pro2
WHERE pro1.program_name='update_num' AND pro2.program_id=program_upstream.p2;

-- MQ14: What program blocks are anywhere downstream of initialize_run? - mq14(DownstreamProgramName)
SELECT DISTINCT pro1.program_name AS DownstreamProgramName
FROM program_downstream, modelfacts_program AS pro1, modelfacts_program AS pro2
WHERE pro2.program_name='initialize_run' AND pro1.program_id=program_downstream.p1;

-- MQ15: What data is immediately downstream of num? - mq15(DownstreamDataName)
SELECT DISTINCT dt1.data_name AS DownstreamDataName
FROM modelfacts_data AS dt1, modelfacts_data AS dt2, data_immediately_downstream
WHERE dt2.data_name='num' AND dt2.data_id=data_immediately_downstream.d2 AND dt1.data_id=data_immediately_downstream.d1;

-- MQ16: What data is immediately upstream of num? - mq16(UpstreamDataName)
SELECT DISTINCT dt2.data_name AS UpstreamDateName
FROM modelfacts_data AS dt1, modelfacts_data AS dt2, data_immediately_upstream
WHERE dt1.data_name='num' AND dt1.data_id=data_immediately_upstream.d1 AND dt2.data_id=data_immediately_upstream.d2;

-- MQ17: What data is downstream of num? - mq17(DownstreamDataName)
SELECT DISTINCT dt1.data_name
FROM modelfacts_data AS dt1, modelfacts_data AS dt2, data_downstream
WHERE dt2.data_name='num' AND dt1.data_id=data_downstream.dd1 AND dt2.data_id=data_downstream.dd2;

-- MQ18: What data is upstream of num? - mq18(UpstreamDataName)
SELECT DISTINCT dt2.data_name
FROM modelfacts_data AS dt1, modelfacts_data AS dt2, data_upstream
WHERE dt1.data_name='num' AND dt2.data_id=data_upstream.dd2 AND dt1.data_id=data_upstream.dd1;





