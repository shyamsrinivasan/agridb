/*SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'sakila'*/

/*SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'film'*/

/*SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'film'*/

/*CREATE TABLE `agrid`.`expense` (`column_name` int(11) NULL, `column_2` varchar(55) NOT NULL, 
PRIMARY KEY (`column_name`), KEY `index_name` (`column_name`), 
CONSTRAINT `constraint_name` FOREIGN KEY (`column_name`) REFERENCES `table_name` (`column_in_foreign_table`) ON DELETE CASCADE)*/

/*CREATE TABLE `testdb`.`items` (
  `itemid` INT NOT NULL,
  `name` VARCHAR(30) NULL,
  `type` VARCHAR(15) NULL DEFAULT 'undefined',
  `cost` DECIMAL(10,2) NULL DEFAULT 0.00,
  `from_date` TIMESTAMP(3) NULL DEFAULT CURRENT_TIMESTAMP,
  `item_num` INT NOT NULL AUTO_INCREMENT,
  `to_date` TIMESTAMP(3) NULL DEFAULT NULL,
  PRIMARY KEY (`itemid`, `item_num`),
  UNIQUE INDEX `item_num_UNIQUE` (`item_num` ASC) VISIBLE);*/
  
  SELECT description, type, cost, id, to_date FROM agridb.items 
  WHERE description = 'Male wage' AND to_date IS NULL
