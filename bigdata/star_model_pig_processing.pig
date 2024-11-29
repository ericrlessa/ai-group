-- Load the data
invoice_data = LOAD '/user/ssis/data/invoice.csv' USING PigStorage(',')
               AS (InvoiceNo:chararray, StockCode:chararray, Quantity:int, 
                   InvoiceDate:chararray, CustomerID:int);

filtered_data = FILTER invoice_data BY InvoiceDate IS NOT NULL;


-- Convert InvoiceDate to a datetime format
invoice_data_parsed = FOREACH filtered_data GENERATE
    InvoiceNo AS InvoiceNo,
    ToDate(InvoiceDate, 'dd/MM/yyyy HH:mm') AS InvoiceDatetime,
    Quantity AS Quantity,
    StockCode AS StockCode,
    CustomerID AS CustomerID;

-- Add a generated TimeId
time_data_with_id = FOREACH invoice_data_parsed GENERATE
    CONCAT(InvoiceNo, ToString(InvoiceDatetime)) AS TimeId, -- Sequential IDs
    ToString(InvoiceDatetime, 'dd/MM/yyyy') AS Date,
    GetYear(InvoiceDatetime) AS Year,
    (CASE WHEN GetMonth(InvoiceDatetime) IN (1, 2, 3) THEN 1 
          WHEN GetMonth(InvoiceDatetime) IN (4, 5, 6) THEN 2 
          WHEN GetMonth(InvoiceDatetime) IN (7, 8, 9) THEN 3 
          ELSE 4 END) AS Quarter,
    GetMonth(InvoiceDatetime) AS Month,
    (CASE GetMonth(InvoiceDatetime) 
          WHEN 1 THEN 'January' 
          WHEN 2 THEN 'February'
          WHEN 3 THEN 'March'
          WHEN 4 THEN 'April'
          WHEN 5 THEN 'May'
          WHEN 6 THEN 'June'
          WHEN 7 THEN 'July'
          WHEN 8 THEN 'August'
          WHEN 9 THEN 'September'
          WHEN 10 THEN 'October'
          WHEN 11 THEN 'November'
          ELSE 'December' END) AS MonthName,
    GetDay(InvoiceDatetime) AS Day,
    GetWeek(InvoiceDatetime) AS Week;

-- Remove duplicates to ensure unique time dimensions
unique_time_data = DISTINCT time_data_with_id;

-- Store the time data
STORE unique_time_data INTO '/user/ssis/data/time' USING PigStorage(',');

-- Link invoice data to generated TimeId
linked_invoice_data = JOIN invoice_data_parsed BY CONCAT(InvoiceNo, ToString(InvoiceDatetime)), unique_time_data BY TimeId USING 'hash';

linked_invoice_final = FOREACH linked_invoice_data GENERATE
    invoice_data_parsed::InvoiceNo AS InvoiceNo,
    invoice_data_parsed::Quantity AS Quantity,
    invoice_data_parsed::StockCode AS StockCode,
    invoice_data_parsed::CustomerID AS CustomerID,
    unique_time_data::TimeId AS TimeId;

-- Store the linked invoice data
STORE linked_invoice_final INTO '/user/ssis/data/invoice_processed' USING PigStorage(',');
