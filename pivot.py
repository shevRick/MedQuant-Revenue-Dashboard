import pandas as pd

class PivotBuilder:
    """Methods for building Pivot Tables."""
    
    def __init__(self):

        """init

        Parameters
        ----------
        repo : MedQuantRepository, optional
            Data source, by default MedQuantRepository()
        """
        self.df = pd.read_csv('app.csv')
        
    
    def query_df(self, query):
        
        self.fd = self.df.query(query)
        
       
    def diagnosis_pivot_table(self, columns='', category=''):

        if category == 0:

            table =  self.fd.pivot_table(index='diagnosis', values='Membership_Number', aggfunc='count')

            # Reset index
            table = table.reset_index()

            table = table.sort_values(by='Membership_Number', ascending=False)

            table = table.head(10)

            return table
            
        else:
            
            table = self.fd.pivot_table(index='diagnosis', columns=columns, values='Membership_Number', aggfunc='count', margins=True, margins_name="Total")

            table = table.drop('Total', axis=0)

            # Reset index
            table = table.reset_index()

            table = table.sort_values(by='Total', ascending=False)

            table = table.drop('Total', axis=1)

            table = table.head(10)

            return table
            
        
    def overall_pivot_table(self, index='',  columns='', category=''):

        if category == 0:

            table = self.fd.pivot_table(index=index, values='Inv_Amount', aggfunc='sum')

            return table

        elif category == 1:

            table = self.fd.pivot_table(index=index, columns="Quarter", values='Inv_Amount', aggfunc='sum')

            return table
        
        elif category == 2:

            # Define custom month order
            month_order = ['January', 'February', 'March', 'April','May','June','July','August','September','October','November','December']

            table = self.fd.pivot_table(index=index, columns="Month", values='Inv_Amount', aggfunc='sum')

            table = table.reindex(columns=month_order)

            return table
        elif category == 3:
        
            table = self.fd.pivot_table(index=index, values='AgeGroup', aggfunc='count').reset_index()
            return table
            
        elif category == 4:
            table = self.fd.pivot_table(index=index, values='Age', aggfunc='count')
            return table

        elif category == 5:
            table = self.fd.pivot_table(index=index, values='Age', aggfunc='count').reset_index()

            table["count_pct"] = (table["Age"] / table["Age"].sum()) * 100
            return table
            
        elif category == 6: #Monthly Revenue
            table = self.fd.pivot_table(index=index, columns=columns, values='Inv_Amount', aggfunc='sum')

            # Convert pivot table to DataFrame
            table = pd.DataFrame(table.to_records())
            
            return table
            
        else:
            table = self.fd.pivot_table(index=index, values='Inv_Amount', aggfunc='sum').reset_index()

            table["count_pct"] = (table["Inv_Amount"] / table["Inv_Amount"].sum()) * 100
            
            return table
            
    def KPIs(self, index='', category=''):

        if category == 0:
        
            table = self.fd.pivot_table(index=index, values='Membership_Number', aggfunc='count')

            return table
            
        elif category == 1:
        
            table = self.fd.pivot_table(index=index, values=['Inv_Amount','Membership_Number'], aggfunc={'Inv_Amount':'mean', 'Membership_Number': 'count'}).round(2)

            return table
            
        elif category == 2:
        
            table = self.fd.pivot_table(index='Membership_Number', values='Quarter', aggfunc=pd.Series.nunique)

            return table
            
        elif category == 3:
        
            table = self.fd.pivot_table(index='Membership_Number', values='Quarter', aggfunc=pd.Series.nunique)
            
            return table
       
        
            
        
    def summary_stats(self):

        sum_df = int(self.fd["Inv_Amount"].sum())
        mean_df = round(self.fd["Inv_Amount"].mean(), 2)
        count_df = len(self.fd["Inv_Amount"])
        insurance = self.fd["Scheme_Code"]
        scheme = self.fd["scheme"]
        service = self.fd["service"]
        quarter = self.fd["Quarter"]
        gender = self.fd["Gender"]
        age_group = self.fd["AgeGroup"]
        
        summary_df = {
            'Sum': sum_df,
            'Mean': mean_df,
            'Count': count_df,
            'insurance': insurance,
            'scheme': scheme,
            'service': service,
            'quarter': quarter,
            'gender': gender,
            'age_group': age_group
        }
        
        return summary_df
        
  
        

        