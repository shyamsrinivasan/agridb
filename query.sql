/*SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'sakila'*/

/*SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'film'*/

/*SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'film'*/

CREATE TABLE `agrid`.`expense` (`column_name` int(11) NULL, `column_2` varchar(55) NOT NULL, 
PRIMARY KEY (`column_name`), KEY `column_name` (`index_name`), 
CONSTRAINT `constraint_name` FOREIGN KEY (`column_name`) REFERENCES `table_name` (`column_in_foreign_table`) ON DELETE CASCADE)
