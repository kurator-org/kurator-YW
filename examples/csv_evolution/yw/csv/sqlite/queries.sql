-- .help
-- .tables
.header on
.mode column
.width 35 20 20
.output queries_output.txt

-- queries
-- LQ1: How many times has the variable 'num' been updated? - lq1(#count).
SELECT count(DISTINCT new_value) 
FROM record_update;


-- LQ2: At which step, the variable 'num' was updated to 7? - lq2(iteration_count).
SELECT iteration_count
FROM record_update
WHERE new_value + 0 = 7;


-- LQ3: At which steps, the updated num > 5? - lq3(iteration_count)
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

