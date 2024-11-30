# SQL Server and Hadoop Integration Project in SSIS pipeline

This repository contains instructions, scripts, and commands for setting up SQL Server and Hadoop (HDFS) integration. It includes SQL Server table creation scripts and HDFS setup commands for user directories.

This made through SSIS environment.

# SSIS Pipeline

The file Pipeline.dstx has the SSIS pipeline:

- copy the csvs files to HDFS
- extract from HDFS the csv files
- transform the data
- load in SQL Server the data transformed

## 📋 SQL Server Script

The following SQL script creates the `customer`, `TimeTable`, `invoice`, and `product` tables in your SQL Server database.

```sql

CREATE TABLE [dbo].[customer](
	[customer_id] [bigint] PRIMARY KEY,
	[country] [varchar](100) NULL
 )

CREATE TABLE [dbo].[TimeTable](
	[TimeId] [varchar](100) PRIMARY KEY,
	[Date] [varchar](100) NOT NULL,
	[Year] int NOT NULL,
	[Quarter] int NOT NULL,
	[Month] int NOT NULL,
	[MonthName] [varchar](100) NOT NULL,
	[Day] int NOT NULL,
	[Week] [varchar](100) NOT NULL
)

CREATE TABLE [dbo].[product](
	[stock_code] [varchar](50) COLLATE SQL_Latin1_General_CP1_CS_AS PRIMARY KEY,
	[description] [varchar](50) NULL,
	[unitPrice] [decimal](15, 5) NULL
)


CREATE TABLE [dbo].[invoice](
    ID INT IDENTITY(1,1) PRIMARY KEY, 
	[invoice_id] [varchar](50) NULL,
	[quantity] [int] NULL,
	[stock_Code] [varchar](50) COLLATE SQL_Latin1_General_CP1_CS_AS NULL ,
	[customer_id] [bigint] NULL,
	[time_id] [varchar](100) NULL,
	FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
	FOREIGN KEY (time_id) REFERENCES TimeTable(TimeId)
)





```

## HDFS commands

```bash

# Create a user directory in HDFS for SSIS user
hdfs dfs -mkdir -p /user/ssis/data

# Set ownership of this directory to the user you want to use for SSIS
hdfs dfs -chown ssis:ssis /user/ssis/data

# Grant Permissions to the User
hdfs dfs -chmod 755 /user/ssis/data

# Add user
useradd ssis

```