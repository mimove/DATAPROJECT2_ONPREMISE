-- Creation of product table
CREATE TABLE IF NOT EXISTS panelData (
  Panel_id varchar(250) NOT NULL,
  power_panel DECIMAL(20,3) NOT NULL,
  current_status INT NOT NULL,
  time_data TIMESTAMP
);
