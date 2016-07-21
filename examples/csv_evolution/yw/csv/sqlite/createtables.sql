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

-- FACT: modelfacts_log_template(log_template_id, port_id, entry_template, log_annotation_id).
.import ../modelfacts_log_template.csv modelfacts_log_template

-- FACT: modelfacts_log_template_variable(log_variable_id, variable_name, log_template_id).
CREATE TABLE modelfacts_log_template_variable (
    log_variable_id     TEXT     NOT NULL    PRIMARY KEY,
    variable_name       TEXT     NOT NULL,
    log_template_id     TEXT     NOT NULL    REFERENCES modelfacts_log_template(log_template_id)
);
.import ../modelfacts_log_template_variable.csv modelfacts_log_template_variable

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
        AND v1.entry_template=v2.entry_template AND v2.entry_template=v3.entry_template
        AND v1.variable_name='iteration_count' 
        AND v2.variable_name='num_old'
        AND v3.variable_name='num_new' 
        AND v1.log_entry_id=v2.log_entry_id AND v2.log_entry_id=v3.log_entry_id;


-- .tables
.header on
.mode column
