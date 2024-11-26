# SQL Server and Hadoop Integration Project

This repository contains instructions, scripts, and commands for setting up SQL Server and Hadoop (HDFS) integration. It includes SQL Server table creation scripts and HDFS setup commands for user directories.

## 📋 SQL Server Script

The following SQL script creates the `customer`, `invoice`, and `product` tables in your SQL Server database.

```sql

CREATE TABLE [dbo].[customer](
	[customer_id] [bigint] NULL,
	[country] [varchar](100) NULL
)

CREATE TABLE [dbo].[invoice](
	[invoice_id] [varchar](50) NULL,
	[invoice_date] [datetime] NULL,
	[quantity] [int] NULL,
	[stock_Code] [varchar](50) NULL,
	[customer_id] [bigint] NULL
)

CREATE TABLE [dbo].[product](
	[stock_code] [varchar](50) NULL,
	[description] [varchar](50) NULL,
	[unitPrice] [decimal](15, 5) NULL
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