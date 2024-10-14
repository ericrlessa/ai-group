# -*- coding: utf-8 -*-
"""normalize.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Yv8IRGCKnJsuCJyjafgI2hn-nBfD6Svx
"""

import pandas as pd
import numpy as np
import os

import xlrd

# Path to the Excel workbook
excel_file = r"Sample - Superstore.xls"

# Read all sheets from the Excel file
xls = pd.ExcelFile(excel_file, engine='xlrd')

# Get the sheet names
sheet_names = xls.sheet_names

# Create a dictionary to store dataframes
dfs = {}

# Read each sheet into a separate dataframe
for sheet in sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet, engine='xlrd')
    dfs[sheet] = df

# Access individual dataframes
orders_df = dfs['Orders']
returns_df = dfs['Returns']
People_df = dfs['People']

orders_df

# Replace missing values in 'Postal Code' with '0000'
orders_df['Postal Code'] = orders_df['Postal Code'].fillna('0000')

# Verify the changes

print(orders_df['Postal Code'].isna().sum(), "missing values")

#total number of rows in the dataframe
print(len(orders_df))

distinct_combinations = orders_df.groupby(['Order ID', 'Product ID']).size().reset_index().shape[0]
print(distinct_combinations)

# Group by 'Order ID' and 'Product ID', count occurrences, and filter for counts > 1
duplicates = orders_df.groupby(['Order ID', 'Product ID']).size().reset_index(name='count')
duplicates = duplicates[duplicates['count'] > 1]

# Sort by count in descending order (optional, for better readability)
duplicates = duplicates.sort_values('count', ascending=False)

print("Duplicate combinations of 'Order ID' and 'Product ID':")
print(duplicates)

# Print the total number of duplicate combinations
print(f"\nTotal number of duplicate combinations: {len(duplicates)}")

duplicates = orders_df.groupby(['Order ID', 'Product ID']).size().reset_index(name='count')
duplicates = duplicates[duplicates['count'] > 1]

# Now, merge this back with the original dataframe to get the desired columns
result = orders_df.merge(duplicates[['Order ID', 'Product ID']], on=['Order ID', 'Product ID'])

# Select only the columns we want
result = result[['Product ID', 'Order ID', 'Sales', 'Quantity', 'Discount', 'Profit']]

# Sort the result (optional, for better readability)
result = result.sort_values(['Order ID', 'Product ID'])

result

#taking sum of quantity,sales,profit and max of other columns ; also droping row_id column
orders_df = orders_df.groupby(['Order ID', 'Product ID']).agg({
    'Order Date': 'max',
    'Ship Date': 'max',
    'Ship Mode': 'max',
    'Customer ID': 'max',
    'Customer Name': 'max',
    'Segment': 'max',
    'Country/Region': 'max',
    'City': 'max',
    'State': 'max',
    'Postal Code': 'max',
    'Region': 'max',
    'Category': 'max',
    'Sub-Category': 'max',
    'Product Name': 'max',
    'Sales': 'sum',
    'Quantity': 'sum',
    'Discount': 'max',
    'Profit': 'sum'
}).reset_index()

orders_df

duplicates = orders_df.groupby(['Order ID', 'Product ID']).size().reset_index(name='count')
duplicates = duplicates[duplicates['count'] > 1]

# Now, merge this back with the original dataframe to get the desired columns
result = orders_df.merge(duplicates[['Order ID', 'Product ID']], on=['Order ID', 'Product ID'])

# Select only the columns we want
result = result[['Product ID', 'Order ID', 'Sales', 'Quantity', 'Discount', 'Profit']]

# Sort the result (optional, for better readability)
result = result.sort_values(['Order ID', 'Product ID'])

result

# NO duplicates now...!!

# Get distinct Order IDs from returns_df
returned_order_ids = set(returns_df['Order ID'])

# Create a dictionary mapping regions to regional managers
region_manager_dict = dict(zip(People_df['Region'], People_df['Regional Manager']))

# Create df_merge with all columns from orders_df
df_merge = orders_df.copy()

# Add 'Returned' column
df_merge['Returned'] = df_merge['Order ID'].isin(returned_order_ids)

# Add 'Regional Manager' column
df_merge['Regional Manager'] = df_merge['Region'].map(region_manager_dict)

df_merge

# Find products with multiple names
product_name_counts = df_merge.groupby('Product ID')['Product Name'].nunique().reset_index(name='name_count')
products_with_multiple_names = product_name_counts[product_name_counts['name_count'] > 1]

# Display the results
print(products_with_multiple_names)
print(f"Number of products with multiple names: {len(products_with_multiple_names)}")

"""The above observation implies that there are about 32 Product_ID s with 2 different Product Names, Which goes against one of our assumptions i.e. 1 to 1 relationship b/w Poduct name and Product ID

Checking for Product Names with multiple Product IDs is an important step in data validation. While ideally each product should have a unique identifier, real-world scenarios often present exceptions. Multiple Product IDs for the same Product Name can occur due to various reasons such as product variations, regional differences. This check helps identify such cases, allowing for proper data management and ensuring accurate analysis. By understanding these instances, we can make informed decisions on how to handle them in our data processing pipeline, whether it's consolidating entries, maintaining separate identifiers, or flagging them for further review. This process is crucial for maintaining data integrity and enabling precise inventory management and sales analysis.

Now, we can clearly Decline that there is nos uch 1 to 1 relationship nor it was originally ment to be b/w product_id and product name,
Therefore while creating Product entity we will create a new "PRODUCT_KEY_ID" column which will be a combination of "Product_ID" and "Product Name".....
"""

product_name_id_counts = df_merge.groupby('Product Name')['Product ID'].nunique().reset_index(name='ID_count')
products_with_multiple_ids = product_name_id_counts[product_name_id_counts['ID_count'] > 1].sort_values('ID_count', ascending=False)

print(f"Number of Product Names with multiple Product IDs: {len(products_with_multiple_ids)}")
print("\nList of Product Names with multiple Product IDs:")
print(products_with_multiple_ids)

for product_name in products_with_multiple_ids['Product Name']:
    product_ids = df_merge[df_merge['Product Name'] == product_name]['Product ID'].unique()
    print(f"\nProduct Name: {product_name}")
    print(f"Product IDs: {product_ids}")

#count of distinct order ID where returned is true
df_merge[df_merge['Returned'] == True]['Order ID'].count()

"""### Normalized form:
![image-2.png](attachment:image-2.png)

#### Converting df_merge into further normalized forms
"""

import pandas as pd

# Assuming df_merge is already loaded

# df_CUSTOMERS
df_CUSTOMERS = df_merge[['Customer ID', 'Customer Name', 'Segment']].drop_duplicates().reset_index(drop=True)

# df_ADDRESS
df_ADDRESS = df_merge[['City', 'State', 'Country/Region', 'Postal Code']].drop_duplicates().reset_index(drop=True)
df_ADDRESS['ADDRESS_ID'] = df_ADDRESS.index + 1

# df_PRODUCTS
df_PRODUCTS = df_merge[['Product ID', 'Product Name', 'Sub-Category']].drop_duplicates().reset_index(drop=True)
df_PRODUCTS['PRODUCT_KEY_ID'] = df_PRODUCTS.index + 1

# df_SubCategory
df_SubCategory = df_merge[['Sub-Category','Category']].drop_duplicates().reset_index(drop=True)
df_SubCategory['Sub_Category_ID'] = df_SubCategory.index + 1

# df_Category
df_Category = df_merge[['Category']].drop_duplicates().reset_index(drop=True)
df_Category['Category_ID'] = df_Category.index + 1

#update df_SubCategory with Category_ID
df_SubCategory = pd.merge(df_SubCategory, df_Category, on='Category')
df_SubCategory = df_SubCategory[['Sub_Category_ID','Sub-Category', 'Category_ID']]

# Update df_PRODUCTS with Sub_Category_ID
df_PRODUCTS = pd.merge(df_PRODUCTS, df_SubCategory, on='Sub-Category')
df_PRODUCTS = df_PRODUCTS[['PRODUCT_KEY_ID','Product ID', 'Product Name', 'Sub_Category_ID']]

# df_MANAGER
df_MANAGER = df_merge[['Region', 'Regional Manager']].drop_duplicates().reset_index(drop=True)
df_MANAGER['REGION_ID'] = df_MANAGER.index + 1

# df_SHIP
df_SHIP = df_merge[['Ship Date', 'Ship Mode']].drop_duplicates().reset_index(drop=True)
df_SHIP['SHIP_ID'] = df_SHIP.index + 1

# df_ORDERS
df_ORDERS = df_merge[['Order ID', 'Customer ID','Order Date','Ship Date','Ship Mode','Returned','City','State','Country/Region','Postal Code','Region']].drop_duplicates().reset_index(drop=True)
#update df_ORDERS with SHIP_ID
df_ORDERS = pd.merge(df_ORDERS, df_SHIP, on=['Ship Mode','Ship Date'])
df_ORDERS = df_ORDERS[['Order ID', 'Customer ID','Order Date','SHIP_ID','Returned','City','State','Country/Region','Postal Code','Region']]
#update df_ORDERS with Address_ID
df_ORDERS = pd.merge(df_ORDERS, df_ADDRESS, on=['City','State','Country/Region','Postal Code'])
df_ORDERS = df_ORDERS[['Order ID', 'Customer ID','Order Date','SHIP_ID','Returned','ADDRESS_ID','Region']]
#update df_ORDERS with Region_ID
df_ORDERS = pd.merge(df_ORDERS, df_MANAGER, on='Region')
df_ORDERS = df_ORDERS[['Order ID', 'Customer ID','Order Date','SHIP_ID','Returned','ADDRESS_ID','REGION_ID']]

# df_ORDER_ITEMS
df_ORDER_ITEMS = df_merge[['Order ID', 'Product ID','Product Name', 'Quantity']].drop_duplicates().reset_index(drop=True)
#Update df_ORDER_ITEMS with PRODUCT_KEY_ID
df_ORDER_ITEMS = pd.merge(df_ORDER_ITEMS, df_PRODUCTS, on=['Product ID','Product Name'])
df_ORDER_ITEMS = df_ORDER_ITEMS[['Order ID', 'PRODUCT_KEY_ID','Quantity']]

# df_Sales
df_Sales = df_merge[['Order ID', 'Product ID','Product Name', 'Sales', 'Discount', 'Profit']].drop_duplicates().reset_index(drop=True)
#Update df_Sales with PRODUCT_KEY_ID
df_Sales = pd.merge(df_Sales, df_PRODUCTS, on=['Product ID','Product Name'])
df_Sales = df_Sales[['Order ID', 'PRODUCT_KEY_ID','Sales', 'Discount', 'Profit']]

print("Length of df_CUSTOMERS:", len(df_CUSTOMERS))
print("Length of df_ADDRESS:", len(df_ADDRESS))
print("Length of df_PRODUCTS:", len(df_PRODUCTS))
print("Length of df_SubCategory:", len(df_SubCategory))
print("Length of df_Category:", len(df_Category))
print("Length of df_MANAGER:", len(df_MANAGER))
print("Length of df_SHIP:", len(df_SHIP))
print("Length of df_ORDERS:", len(df_ORDERS))
print("Length of df_ORDER_ITEMS:", len(df_ORDER_ITEMS))
print("Length of df_Sales:", len(df_Sales))

#get list of columns of each dataframe in order
print(df_CUSTOMERS.columns)
print(df_ADDRESS.columns)
print(df_PRODUCTS.columns)
print(df_SubCategory.columns)
print(df_Category.columns)
print(df_MANAGER.columns)
print(df_SHIP.columns)
print(df_ORDERS.columns)
print(df_ORDER_ITEMS.columns)
print(df_Sales.columns)

df_ORDERS

# Rearranging DataFrames using simplified assignment
df_CUSTOMERS1 = df_CUSTOMERS[['Customer ID', 'Customer Name', 'Segment']]
df_ADDRESS1 = df_ADDRESS[['ADDRESS_ID', 'City', 'State', 'Country/Region', 'Postal Code']]
df_PRODUCTS1 = df_PRODUCTS[['PRODUCT_KEY_ID','Product ID', 'Product Name', 'Sub_Category_ID']]
df_SubCategory1 = df_SubCategory[['Sub_Category_ID', 'Sub-Category', 'Category_ID']]
df_Category1 = df_Category[['Category_ID', 'Category']]
df_MANAGER1 = df_MANAGER[['REGION_ID', 'Region', 'Regional Manager']]
df_SHIP1 = df_SHIP[['SHIP_ID', 'Ship Date', 'Ship Mode']]
df_ORDERS1 = df_ORDERS[['Order ID', 'Order Date','Customer ID', 'SHIP_ID', 'Returned', 'ADDRESS_ID', 'REGION_ID']]
df_ORDER_ITEMS1 = df_ORDER_ITEMS[['Order ID', 'PRODUCT_KEY_ID','Quantity']]
df_Sales1 = df_Sales[['Order ID', 'PRODUCT_KEY_ID','Sales', 'Discount', 'Profit']]

df_ORDERS1.head()

#converting True to 1 and False to 0 in order to make MYSQL compatible
df_ORDERS1 = df_ORDERS1.copy()
df_ORDERS1['Returned'] = df_ORDERS1['Returned'].astype(int)

df_ORDERS1.head()

#distinct values with count in Returned column

print(df_ORDERS1['Returned'].value_counts())

def create_directory(directory_name):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    new_folder_path = os.path.join(current_directory, directory_name)
    if not os.path.exists(new_folder_path):
        os.mkdir(new_folder_path)

path = 'files/'
create_directory(path)

#saving each dataframe into csv files
df_CUSTOMERS1.to_csv(path + 'CUSTOMERS.csv', index=False)
df_ADDRESS1.to_csv(path + 'ADDRESS.csv', index=False)
df_PRODUCTS1.to_csv(path + 'PRODUCTS.csv', index=False)
df_SubCategory1.to_csv(path + 'SUBCATEGORY.csv', index=False)
df_Category1.to_csv(path + 'CATEGORY.csv', index=False)
df_MANAGER1.to_csv(path + 'MANAGER.csv', index=False)
df_SHIP1.to_csv(path + 'SHIP.csv', index=False)
df_ORDERS1.to_csv(path + 'ORDERS.csv', index=False)
df_ORDER_ITEMS1.to_csv(path + 'ORDER_ITEMS.csv', index=False)
df_Sales1.to_csv(path + 'SALES.csv', index=False)

"""##### Creating New DATABASE inside MYSQL - create DATABASE GBC_Superstore ;

"""

import mysql.connector
from mysql.connector import Error
import time
import os


def wait_for_mysql(host, user, password, database, retries=50, delay=10):
    """Wait for MySQL to be ready."""
    for i in range(retries):
        try:
            db = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if db.is_connected():
                print("Connected to MySQL")
                return db
        except Error as e:
            print(f"Attempt {i+1}: MySQL is not ready yet. Error: {e}")
            time.sleep(delay)
    raise Exception("MySQL is not ready after several attempts.")

# Connection details
host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']

# Wait for MySQL to be ready before proceeding
connection = wait_for_mysql(host, user, password, database)

print("Connected to MySQL") if connection.is_connected() else print("Connection failed")

cursor = connection.cursor()

# Create the tables
cursor.execute("""
    CREATE TABLE CUSTOMERS (
        Customer_ID VARCHAR(50) PRIMARY KEY,
        Customer_Name VARCHAR(100),
        Segment VARCHAR(50)
    );
""")

cursor.execute("""
    CREATE TABLE ADDRESS (
        Address_ID INT PRIMARY KEY,
        City VARCHAR(100),
        State VARCHAR(100),
        Country_Region VARCHAR(100),
        Postal_Code VARCHAR(20)
    );
""")

cursor.execute("""
    CREATE TABLE Category (
        Category_ID INT PRIMARY KEY,
        Category VARCHAR(100)
    );
""")

cursor.execute("""
    CREATE TABLE SubCategory (
        Sub_Category_ID INT PRIMARY KEY,
        Sub_Category VARCHAR(100),
        Category_ID INT,
        FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
    );
""")


cursor.execute("""
    CREATE TABLE PRODUCTS (
        Product_KEY_ID INT PRIMARY KEY,
        Product_ID VARCHAR(50),
        Product_Name VARCHAR(10000),
        Sub_Category_ID INT,
        FOREIGN KEY (Sub_Category_ID) REFERENCES SubCategory(Sub_Category_ID)
    );
""")

cursor.execute("""
    CREATE TABLE MANAGER (
        Region_ID INT PRIMARY KEY,
        Region VARCHAR(100),
        Regional_Manager VARCHAR(100)
    );
""")

cursor.execute("""
    CREATE TABLE SHIP (
        Ship_ID INT PRIMARY KEY,
        Ship_Date DATE,
        Ship_Mode VARCHAR(50)
    );
""")

cursor.execute("""
    CREATE TABLE ORDERS (
        Order_ID VARCHAR(50) PRIMARY KEY,
        Order_Date DATE,
        Customer_ID VARCHAR(50),
        Ship_ID INT,
        Returned BOOLEAN,
        Address_ID INT,
        Region_ID INT,
        FOREIGN KEY (Customer_ID) REFERENCES CUSTOMERS(Customer_ID),
        FOREIGN KEY (Ship_ID) REFERENCES SHIP(Ship_ID),
        FOREIGN KEY (Address_ID) REFERENCES ADDRESS(Address_ID),
        FOREIGN KEY (Region_ID) REFERENCES MANAGER(Region_ID)
    );
""")

cursor.execute("""
    CREATE TABLE ORDER_ITEMS (
        Order_ID VARCHAR(50),
        Product_KEY_ID INT,
        Quantity INT,
        PRIMARY KEY (Order_ID, Product_KEY_ID),
        FOREIGN KEY (Order_ID) REFERENCES ORDERS(Order_ID),
        FOREIGN KEY (Product_KEY_ID) REFERENCES PRODUCTS(Product_KEY_ID)
    );
""")

cursor.execute("""
    CREATE TABLE Sales (
        Order_ID VARCHAR(50),
        Product_KEY_ID INT,
        Sales DOUBLE,
        Discount DOUBLE,
        Profit DOUBLE,
        PRIMARY KEY (Order_ID, Product_KEY_ID),
        FOREIGN KEY (Order_ID) REFERENCES ORDERS(Order_ID),
        FOREIGN KEY (Product_KEY_ID) REFERENCES PRODUCTS(Product_KEY_ID)
    );
""")

# Commit the transaction
connection.commit()

print("Tables created successfully!")

# Close the connection
cursor.close()

"""![image.png](attachment:image.png)

Loading Data From CSV Files into MYSQL
"""

connection.close()
connection = wait_for_mysql(host, user, password, database)

cursor = connection.cursor()


# List of CSV files and their corresponding table names
csv_files = [
    "ADDRESS.csv",
    "CUSTOMERS.csv",
    "CATEGORY.csv",
    "SUBCATEGORY.csv",
    "PRODUCTS.csv",
    "MANAGER.csv",
    "SHIP.csv",
    "ORDERS.csv",
    "SALES.csv",
    "ORDER_ITEMS.csv"
]

# Loop through each file and load data into the corresponding table
for csv_file in csv_files:
    table_name = csv_file.split('.')[0].lower()  # Convert file name to lowercase table name
    csv_file_path = csv_file  # Full path to the CSV file

    # SQL command to load CSV data into the table
    query = f"""
        LOAD DATA INFILE '/var/lib/mysql-files/{csv_file_path}'
        INTO TABLE {table_name}
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        IGNORE 1 ROWS;
    """

    try:
        # Execute the SQL command
        cursor.execute(query)
        connection.commit()

        # Get the number of rows inserted
        rows_inserted = cursor.rowcount

        print(f"{rows_inserted} rows inserted in {table_name}.")

    except mysql.connector.Error as err:
        print(f"Error inserting data into {table_name}: {err}")

# Close the cursor and connection
cursor.close()
connection.close()

connection = wait_for_mysql(host, user, password, database)

"""### Confirming the data in MYSQL by Reverse Engineering

![image.png](attachment:image.png)

### Again Forming the main base table to be used for operational,KPI and Executive Reports

![image.png](attachment:image.png)
"""

outdir = 'output/'
create_directory(outdir)

queryOp = """
 select
    m.Regional_Manager, c.Segment, cat.Category,

    round(sum(sale.sales)) as 'Total Sales',
	count(distinct o.order_id) as 'Number of Orders',
	round(avg(sale.sales)) as 'Average Sales per Order',
	
	round(avg(sale.discount)) as 'Average Discount',
	
	round(sum(oi.quantity)) as 'Total Quantity',
	round(avg(oi.quantity)) as 'Average Quantity',
	
    round(SUM(CASE WHEN o.returned = 0 THEN sale.profit ELSE 0 END)) as 'Total Profit',
    round(SUM(CASE WHEN o.returned = 0 THEN sale.profit ELSE 0 END)) as 'Average Profit',
        
    round(SUM(CASE WHEN o.returned = 0 THEN sale.profit ELSE 0 END)/SUM(CASE WHEN o.returned = 0 THEN sale.sales ELSE 0 END)) as 'Gross Profit Margin',
        
    round((avg(sale.discount)*100)/avg(sale.profit)) as 'Discount-to-Profit Ratio',
        
    round(sum(o.returned)) as 'Total returns',
    round(avg(o.returned)*100) as 'Return Rate'

  from order_items as oi
	left join sales as sale on oi.Order_ID=sale.Order_ID and oi.Product_KEY_ID=sale.Product_KEY_ID
	left join orders as o on o.Order_ID=oi.Order_ID
	left join products as p on p.Product_KEY_ID=oi.Product_KEY_ID
	left join subcategory as sub on sub.Sub_Category_ID=p.Sub_Category_ID
	left join category as cat on cat.Category_ID=sub.Category_ID
	left join customers as c on o.Customer_ID=c.Customer_ID
	left join ship as s on s.Ship_ID = o.Ship_ID
	left join address as a on a.Address_ID=o.Address_ID
	left join manager as m on m.Region_ID=o.Region_ID
 where MONTH(o.order_date) = 12 AND YEAR(o.order_date) = 2021
 group by m.Regional_Manager, c.Segment, cat.Category
"""

df_base = pd.read_sql(queryOp, connection)
df_base.to_excel(outdir + 'operational.xlsx', index=False, engine='openpyxl')

queryExec = """
select ship_mode as 'Shipping Mode',
 round(sales_q4_20) as 'Sales Q4-20',
 round(sales_q4_21) as 'Sales Q4-21',
 round(((sales_q4_21 - sales_q4_20)/sales_q4_20)* 100) as 'Q4 Sales YOY',
 round(avg_ship_time_q4_21) as 'Average Shipping Time',
 round((profit_q4_21/sales_q4_21)*100) as 'Profit Margin',
 round((return_q4_21/total_orders)*100) as 'Return Rate',
 round((discount_mean*100)/profit_mean) 'Discount Profit Ratio'
 from (
 select s.ship_mode,
        SUM(CASE 
        WHEN o.order_date BETWEEN '2021-10-01' AND '2021-12-31' 
        THEN sale.sales 
        ELSE 0 
    END) AS sales_q4_21,
        SUM(CASE 
        WHEN o.order_date BETWEEN '2021-10-01' AND '2021-12-31' 
        THEN sale.profit 
        ELSE 0 
    END) AS profit_q4_21,
    SUM(CASE 
        WHEN o.order_date BETWEEN '2020-10-01' AND '2020-12-31' 
        THEN sale.sales 
        ELSE 0 
    END) AS sales_q4_20,
    SUM(CASE 
        WHEN o.order_date BETWEEN '2021-07-01' AND '2021-09-30'  
        THEN sale.sales 
        ELSE 0 
    END) AS sales_q3_21,
     avg(CASE 
        WHEN o.order_date BETWEEN '2021-10-01' AND '2021-12-31' 
        THEN DATEDIFF(s.ship_date, o.order_date)
        ELSE null 
    END) AS avg_ship_time_q4_21,
     SUM(CASE 
        WHEN o.order_date BETWEEN '2021-10-01' AND '2021-12-31' and o.returned = 1 
        THEN 1 
        ELSE 0 
    END) AS return_q4_21,
    sum(
    CASE 
        WHEN o.order_date BETWEEN '2021-10-01' AND '2021-12-31'
        THEN 1
        ELSE 0 
    END
     ) as total_orders,
     avg(
    CASE 
        WHEN o.order_date BETWEEN '2021-10-01' AND '2021-12-31'
        THEN sale.discount
        ELSE Null
    END
     ) as discount_mean,
     avg(
    CASE 
        WHEN o.order_date BETWEEN '2021-10-01' AND '2021-12-31'
        THEN sale.profit
        ELSE Null
    END
     ) as profit_mean
  from order_items as oi
	left join sales as sale on oi.Order_ID=sale.Order_ID and oi.Product_KEY_ID=sale.Product_KEY_ID
	left join orders as o on o.Order_ID=oi.Order_ID
	left join products as p on p.Product_KEY_ID=oi.Product_KEY_ID
	left join subcategory as sub on sub.Sub_Category_ID=p.Sub_Category_ID
	left join category as cat on cat.Category_ID=sub.Category_ID
	left join customers as c on o.Customer_ID=c.Customer_ID
	left join ship as s on s.Ship_ID = o.Ship_ID
	left join address as a on a.Address_ID=o.Address_ID
	left join manager as m on m.Region_ID=o.Region_ID
 group by s.ship_mode ) sales_q
 """

df_base = pd.read_sql(queryExec, connection)
df_base.to_excel(outdir + 'executive.xlsx', index=False, engine='openpyxl')

connection.close()