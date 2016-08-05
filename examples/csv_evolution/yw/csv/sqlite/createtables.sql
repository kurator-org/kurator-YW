-- .help
.mode csv


-- table facts import from csv
-- tables to be used for reference
-- FACT: extractfacts_extract_source(source_id, source_path)
.import ../extractfacts_extract_source.csv extractfacts_extract_source

-- FACT: reconfacts_resource(resource_id, resource_uri)
.import ../reconfacts_resource.csv reconfacts_resource

-- table to use references
-- FACT: extractfacts_annotation(annotation_id, source_id, line_number, tag, keyword, value)
.import ../extractfacts_annotation.csv extractfacts_annotation

-- FACT: extractfacts_annotation_qualifies(qualifying_annotation_id, primary_annotation_id)
.import ../extractfacts_annotation_qualifies.csv extractfacts_annotation_qualifies

-- FACT: modelfacts_program(program_id, program_name, qualified_program_name, begin_annotation_id, end_annotation_id)
-- program = block= green computational step = YW annotation @begin
.import ../modelfacts_program.csv modelfacts_program

-- FACT: modelfacts_workflow(program_id)
-- workflow in YW is the toppest level workflow (i.e., "def evolve_csv():") in the current script
.import ../modelfacts_workflow.csv modelfacts_workflow

-- FACT: modelfacts_has_subprogram(program_id, subprogram_id)
.import ../modelfacts_has_subprogram.csv modelfacts_has_subprogram

-- FACT: modelfacts_function(program_id)
-- function = function in .py = any funcion beginning with "def FunctionName:" in the Python script rather than the main function (i.e., "def evolve_csv():") in the current script. 
.import ../modelfacts_function.csv modelfacts_function

-- FACT: modelfacts_log_template(log_template_id, port_id, entry_template, log_annotation_id).
.import ../modelfacts_log_template.csv modelfacts_log_template

-- FACT: modelfacts_log_template_variable(log_variable_id, variable_name, log_template_id).
CREATE TABLE modelfacts_log_template_variable (
    log_variable_id     TEXT     NOT NULL    PRIMARY KEY,
    variable_name       TEXT     NOT NULL,
    log_template_id     TEXT     NOT NULL    REFERENCES modelfacts_log_template(log_template_id)
);
.import ../modelfacts_log_template_variable.csv modelfacts_log_template_variable

-- FACT: modelfacts_port(port_id, port_type, port_name, qualified_port_name, port_annotation_id, data_id)
.import ../modelfacts_port.csv modelfacts_port

-- FACT: modelfacts_has_in_port(block_id, port_id)
.import ../modelfacts_has_in_port.csv modelfacts_has_in_port

-- FACT: modelfacts_has_out_port(block_id, port_id)
.import ../modelfacts_has_out_port.csv modelfacts_has_out_port

-- FACT: modelfacts_data(data_id, data_name, qualified_data_name)
.import ../modelfacts_data.csv modelfacts_data

-- FACT: modelfacts_channel(channel_id, data_id)
.import ../modelfacts_channel.csv modelfacts_channel

-- FACT: modelfacts_port_connects_to_channel(port_id, channel_id)
.import ../modelfacts_port_connects_to_channel.csv modelfacts_port_connects_to_channel



-- FACT: reconfacts_log_variable_value(resource_id, log_entry_id, log_variable_id, log_variable_value).
CREATE TABLE reconfacts_log_variable_value (
    resource_id         INTEGER     NOT NULL       REFERENCES reconfacts_resource(resource_id),
    log_entry_id        INTEGER     NOT NULL       REFERENCES modelfacts_log_template(log_template_id),       
    log_variable_id     INTEGER     NOT NULL,
    log_variable_value  TEXT        NOT NULL,
    PRIMARY KEY (log_entry_id, log_variable_id)
);
.import ../reconfacts_log_variable_value.csv reconfacts_log_variable_value






-- table rules created for queries
-- RULE: annotation_qualifies_full(qualifying_annotation_id, primary_annotation_id, source_id, line_number, keyword, value)
CREATE TABLE annotation_qualifies_full AS
    SELECT qualifying_annotation_id, primary_annotation_id,source_id, line_number, keyword, value
    FROM extractfacts_annotation_qualifies LEFT OUTER JOIN extractfacts_annotation ON qualifying_annotation_id=annotation_id;

-- RULE: program_description(program_id, description)
CREATE TABLE program_description AS
    SELECT program_id, value as description
    FROM modelfacts_program LEFT OUTER JOIN annotation_qualifies_full
    ON begin_annotation_id=primary_annotation_id AND keyword='@desc';

-- RULE: port_description(port_id, description)
CREATE TABLE port_description AS
    SELECT port_id, value as description
    FROM modelfacts_port LEFT OUTER JOIN annotation_qualifies_full
    ON port_annotation_id=primary_annotation_id AND keyword='@desc';


-- RULE: subprogram(program_id)
CREATE TABLE subprogram AS
    SELECT subprogram_id AS program_id
    FROM modelfacts_has_subprogram;


-- RULE: top_workflow(program_id)
-- top_workflow is the workflow/computation_step that is not contained by another bworkflow/program/computational step.
CREATE TABLE top_workflow AS
    SELECT program_id FROM modelfacts_workflow
    EXCEPT
    SELECT program_id FROM subprogram;

-- RULE: top_function(program_id)
-- top_function is the function that is the function that is called by the main workflow/function.
CREATE TABLE top_function AS
    SELECT program_id FROM modelfacts_function
    EXCEPT
    SELECT program_id FROM subprogram;

-- RULE: port_data(port_id, data_id, data_name, qualified_data_name)
-- Port P reads or writes data D with name N and qualified name QN.
CREATE TABLE port_data AS
    SELECT modelfacts_port_connects_to_channel.port_id, modelfacts_data.data_id, data_name, qualified_data_name
    FROM modelfacts_port_connects_to_channel, modelfacts_channel, modelfacts_data
    WHERE modelfacts_channel.channel_id=modelfacts_port_connects_to_channel.channel_id AND modelfacts_channel.data_id=modelfacts_data.data_id;


-- RULE: data_in_port(port_id, data_id)
-- Port P is an input for data D.
CREATE TABLE data_in_port AS
    SELECT modelfacts_port_connects_to_channel.port_id, modelfacts_channel.data_id
    FROM modelfacts_port_connects_to_channel, modelfacts_channel, modelfacts_has_in_port
    WHERE modelfacts_channel.channel_id=modelfacts_port_connects_to_channel.channel_id AND modelfacts_port_connects_to_channel.port_id=modelfacts_has_in_port.port_id;

-- RULE:  data_in_workflow(data_id, subprogram_id, port_id)
-- data in (sub)workflow read by ports
CREATE TABLE data_in_workflow AS
    SELECT data_in_port.data_id, subprogram_id, program_id, modelfacts_has_in_port.port_id
    FROM modelfacts_has_subprogram, modelfacts_has_in_port, modelfacts_port_connects_to_channel, modelfacts_channel, data_in_port
    WHERE modelfacts_has_subprogram.subprogram_id=modelfacts_has_in_port.block_id AND modelfacts_has_in_port.port_id=modelfacts_port_connects_to_channel.port_id AND modelfacts_port_connects_to_channel.channel_id=modelfacts_channel.channel_id AND modelfacts_channel.data_id=data_in_port.data_id;

-- RULE: program_immediately_downstream(program1_id, program2_id)
-- Program P1 is immediately downstream of Program P2.
CREATE TABLE program_immediately_downstream AS
    SELECT modelfacts_has_in_port.block_id AS program1_id, modelfacts_has_out_port.block_id AS program2_id
    FROM modelfacts_has_in_port, modelfacts_has_out_port, modelfacts_port_connects_to_channel AS pcc1, modelfacts_port_connects_to_channel AS pcc2
    WHERE modelfacts_has_in_port.port_id=pcc1.port_id AND pcc1.channel_id=pcc2.channel_id AND pcc1.port_id!=pcc2.port_id and pcc2.port_id=modelfacts_has_out_port.port_id;

-- RULE  program_immediately_upstream(program2_id, program1_id)
-- Program P2 is immediately upstream of Program P1.
CREATE TABLE program_immediately_upstream as select program2_id, program1_id
    FROM program_immediately_downstream;

-- RULE: program_downstream(p1, p2)
-- Program P1 is downstream of Program P2.
CREATE TABLE program_downstream AS
    WITH RECURSIVE program_downstream(p1,p2) AS (SELECT program1_id AS p1, program2_id AS p2 FROM program_immediately_downstream UNION SELECT program_downstream.p1, program_immediately_downstream.program2_id FROM program_downstream, program_immediately_downstream WHERE program_downstream.p2=program_immediately_downstream.program1_id)
    SELECT * FROM program_downstream;


-- RULE: program_upstream(p2, p1)
-- Program P2 is upstream of Program P1.
CREATE TABLE program_upstream AS
    SELECT p2, p1
    FROM program_downstream;


-- RULE: data_immediately_downstream(d1, d2)
-- Data D1 is immediately downstream of data D2.
CREATE TABLE data_immediately_downstream AS
    SELECT c1.data_id as d1, c2.data_id as d2
    FROM modelfacts_channel AS c1, modelfacts_channel AS c2, modelfacts_port_connects_to_channel AS pcc1, modelfacts_port_connects_to_channel AS pcc2, modelfacts_has_out_port, modelfacts_has_in_port
    WHERE c1.channel_id=pcc1.channel_id AND c2.channel_id=pcc2.channel_id AND pcc1.port_id=modelfacts_has_out_port.port_id AND pcc2.port_id=modelfacts_has_in_port.port_id AND modelfacts_has_in_port.block_id=modelfacts_has_out_port.block_id;


-- RULE: data_immediately_upstream(d2, d1)
-- Data D1 is immediately upstream of data D2.
CREATE TABLE data_immediately_upstream AS
    SELECT d2, d1
    FROM data_immediately_downstream;


-- RULE: data_downstream(dd1, dd2)
-- Data DD1 is downstream of data DD2.
CREATE TABLE data_downstream AS
    WITH RECURSIVE data_downstream(dd1,dd2) AS (select d1 as dd1, d2 as dd2 from data_immediately_downstream UNION SELECT data_downstream.dd1, data_immediately_downstream.d2 FROM data_downstream, data_immediately_downstream WHERE data_downstream.dd2=data_immediately_downstream.d1) SELECT * FROM data_downstream;


-- RULE: data_upstream(dd2, dd1)
-- Data DD2 is upstream of Data DD1
CREATE TABLE data_upstream AS
    SELECT dd2, dd1
    FROM data_downstream;



-- RULE: log_template_variable_name(log_template_id, port_id, entry_template, log_variable_id, variable_name, log_annotation_id)
CREATE TABLE log_template_variable_name AS
    SELECT DISTINCT modelfacts_log_template.log_template_id, port_id, entry_template, log_variable_id, variable_name, log_annotation_id
    FROM modelfacts_log_template JOIN modelfacts_log_template_variable
    ON modelfacts_log_template.log_template_id = modelfacts_log_template_variable.log_template_id;

-- RULE: log_template_variable_name_value(resource_id, log_template_id, entry_template, log_entry_id, log_variable_id, variable_name, log_variable_value). 
CREATE TABLE log_template_variable_name_value AS
    SELECT DISTINCT resource_id, log_template_id, entry_template, log_entry_id, reconfacts_log_variable_value.log_variable_id, variable_name, log_variable_value
    FROM log_template_variable_name JOIN reconfacts_log_variable_value
    ON log_template_variable_name.log_variable_id = reconfacts_log_variable_value.log_variable_id;

-- RULE: log_record_result(resource_id, final_result,iteration_count)
CREATE TABLE log_record_result AS
    SELECT DISTINCT l1.log_variable_value as final_result, l1.resource_id as resource_id, l2.log_variable_value as iteration_count
    FROM log_template_variable_name_value l1, log_template_variable_name_value l2 
    WHERE l1.entry_template='{timestamp} The {iteration_count}th update: num is {num_old}, now is {num_new}.' 
        AND l1.log_template_id=l2.log_template_id 
        AND l1.variable_name='num_new' 
        AND l2.variable_name='iteration_count'
        AND l1.log_entry_id = l2.log_entry_id;

-- RULE: log_entry_resource(resource_id, log_entry_id)
CREATE TABLE log_entry_resource AS
    SELECT DISTINCT resource_id, log_entry_id
    FROM reconfacts_log_variable_value;

-- RULE: record_update(iteration_count, old_value, new_value)
CREATE TABLE record_update AS
    SELECT v1.log_variable_value as iteration_count, v2.log_variable_value as old_value, v3.log_variable_value as new_value 
    FROM log_template_variable_name_value v1, log_template_variable_name_value v2, log_template_variable_name_value v3 
    WHERE v1.entry_template='{timestamp} The {iteration_count}th update: num is {num_old}, now is {num_new}.' 
        AND v1.entry_template=v2.entry_template AND v2.entry_template=v3.entry_template        AND v1.variable_name='iteration_count' 
        AND v2.variable_name='num_old'
        AND v3.variable_name='num_new' 
        AND v1.log_entry_id=v2.log_entry_id AND v2.log_entry_id=v3.log_entry_id;


-- .tables
.header on
.mode column
