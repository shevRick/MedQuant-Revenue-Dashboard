import mysql.connector
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
import functools
from datetime import datetime

class MedQuantRepository:

    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port=port
        self.username = username
        self.password = password
        self.database = database
        self.connection = self.connect()
     
    def connect(self):
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.database
        )
        return connection
        
    @functools.lru_cache(maxsize=None)
    def final_dataframe(self):
    
        df = self.convert_xml_data_to_dataframe()
        
        
        df[["Net_Amount","Inv_Amount"]] = df[["Total_Amount","Gross_Amount"]].astype(float)
        
        for index, row in df.iterrows():
            if row['Pool_Number'] == '18':
                df.at[index, 'rev_dept'] = 'Inpatient'
            else:
                df.at[index, 'rev_dept'] = 'Outpatient'
        
        df['Date_Of_Birth'] = pd.to_datetime(df['Date_Of_Birth'])
        
        # Calculate the age based on current date
        current_date = datetime.now()
        df['Age'] = (current_date - df['Date_Of_Birth']).astype('<m8[Y]')

        # Define the age groups and their ranges
        age_groups = ['<1','<20', '20-29', '30-39', '40-49', '50+']
        age_bins = [-1, 0, 19, 29, 39, 49, float('inf')]

        # Assign each row to an age group
        df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_groups)

        # Convert the 'Date' column to datetime type
        df['Claim_Date'] = pd.to_datetime(df['Claim_Date'])

        # Extract the year and quarter
        df['Year'] = df['Claim_Date'].dt.year
        df['Quarter'] = df['Claim_Date'].dt.quarter
        df['Month'] = df['Claim_Date'].dt.month_name()
        df['Week'] = df['Claim_Date'].dt.isocalendar().week
        df['Day'] = df['Claim_Date'].dt.day
        
        df['Month'] = pd.Categorical(df['Month'], categories=[
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ], ordered=True)

        
        df_groups = self.retrieve_data_from_mysql_table()
        
        df['service'] = df['Encounter_Type'].map(dict(zip(df_groups['group_name'], df_groups['parent_group_code'])))

        for index, row in df.iterrows():
            if pd.isnull(row['service']):
                if row['Encounter_Type'][:4] == 'Cons':
                    df.at[index, 'service'] = 'CONS' 
                elif row['Encounter_Type'][:4] == 'Medi':
                    df.at[index, 'service'] = 'MED'
                elif row['Encounter_Type'][:4] == 'Proc':
                    df.at[index, 'service'] = 'PRO'
                elif row['Encounter_Type'][:4] == 'Labo':
                    df.at[index, 'service'] = 'LAB'
                else:
                    df.at[index, 'service'] = 'RAD'
                    
        df_scheme = self.retrieve_scheme_from_mysql_table()
        
        df['scheme'] = df['Scheme_Plan'].map(dict(zip(df_scheme['medicalaid_plan'], df_scheme['scheme_name'])))
        
        df_diagnosis = self.retrieve_diagnosis_from_mysql_table()
        
        df['diagnosis'] = df['ICD10_Code'].map(dict(zip(df_diagnosis['code'], df_diagnosis['description'])))
        
        df['diagnosis'] = df['diagnosis'].apply(lambda x: np.random.choice(df['diagnosis'].dropna()) if pd.isnull(x) else x)
      

        return df
    
    def convert_xml_data_to_dataframe(self):
       
            cnx = self.connection

            if cnx.is_connected():
               
                cursor = cnx.cursor()

                query = f"SELECT  Data, Pool_Name FROM claims WHERE Insert_Date BETWEEN '2022-01-01' AND '2023-05-31'"
                cursor.execute(query)

                rows = cursor.fetchall()

                data = []
                for row in rows:
                    xml_data = row[0]
                    pool_no = row[1]

                    root = ET.fromstring(xml_data)

                    subelement_data = {}
                    for subelement in root.iter():
                        subelement_data[subelement.tag] = subelement.text
                        subelement_data['PoolName'] = pool_no


                    data.append(subelement_data)

                df = pd.DataFrame(data)
                
                return df


    def retrieve_data_from_mysql_table(self):
        
        cnx = self.connection

        # Create a cursor object to interact with the database
        cursor = cnx.cursor()

        # Define the query to select all rows from the table
        query = "SELECT group_name,parent_group_code FROM lookup_sbb_groups"

        # Execute the query
        cursor.execute(query)

        # Fetch all the rows returned by the query
        rows = cursor.fetchall()

        # Get the column names
        column_names = [column[0] for column in cursor.description]

        # Create a Pandas DataFrame from the fetched rows
        df = pd.DataFrame(rows, columns=column_names)

        # Close the cursor and the database connection
        cursor.close()

        return df
    
    def retrieve_scheme_from_mysql_table(self):
        # Connect to the MySQL database
        cnx = self.connection

        # Create a cursor object to interact with the database
        cursor = cnx.cursor()

        # Define the query to select all rows from the table
        query = "SELECT scheme_name,medicalaid_plan FROM scheme_list"

        # Execute the query
        cursor.execute(query)

        # Fetch all the rows returned by the query
        rows = cursor.fetchall()

        # Get the column names
        column_names = [column[0] for column in cursor.description]

        # Create a Pandas DataFrame from the fetched rows
        df = pd.DataFrame(rows, columns=column_names)

        # Close the cursor and the database connection
        cursor.close()
       

        return df

    def retrieve_diagnosis_from_mysql_table(self):
        # Connect to the MySQL database
        cnx = self.connection

        # Create a cursor object to interact with the database
        cursor = cnx.cursor()

        # Define the query to select all rows from the table
        query = "SELECT code,description FROM lookup_sbb_diagnosis"

        # Execute the query
        cursor.execute(query)

        # Fetch all the rows returned by the query
        rows = cursor.fetchall()

        # Get the column names
        column_names = [column[0] for column in cursor.description]

        # Create a Pandas DataFrame from the fetched rows
        df = pd.DataFrame(rows, columns=column_names)

        # Close the cursor and the database connection
        cursor.close()

        return df







