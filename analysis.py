import pandas as pd
import sqlite3
import os

# Folder containing monthly files
folder_path = "data/monthly_sales"

# Empty list to store dataframes
all_data = []

# Loop through all CSV files
for file in os.listdir(folder_path):

    if file.endswith(".csv"):

        file_path = os.path.join(folder_path, file)

        df = pd.read_csv(file_path)

        all_data.append(df)

# Combine all dataframes
df = pd.concat(all_data, ignore_index=True)

# Remove missing rows
df = df.dropna()

# Remove repeated header rows
df = df[df["Product"] != "Product"]

# Convert columns to numeric
df["Quantity Ordered"] = pd.to_numeric(df["Quantity Ordered"])
df["Price Each"] = pd.to_numeric(df["Price Each"])

# Convert order date to datetime
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    format="%m/%d/%y %H:%M"
)

# Create month column
df["Month"] = df["Order Date"].dt.month_name()
df["Month_Number"] = df["Order Date"].dt.month

# Rename columns
df.columns = df.columns.str.replace(" ", "_")

# Create SQL database
conn = sqlite3.connect("sales.db")

# Send dataframe to SQL
df.to_sql("sales", conn, if_exists="replace", index=False)

# SQL query
query = """
SELECT Month,
       Month_Number,
       SUM(Quantity_Ordered * Price_Each) AS Revenue
FROM sales
GROUP BY Month, Month_Number
ORDER BY Month_Number;
"""

# Run query
result = pd.read_sql_query(query, conn)

# Show results
print(result)

# Revenue bar chart
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))

plt.bar(result["Month"], result["Revenue"])

plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.title("Monthly Revenue")

plt.tight_layout()
plt.savefig("monthly_revenue.png")
plt.show()