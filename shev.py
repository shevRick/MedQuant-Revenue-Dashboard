
import streamlit as st
import plotly.express as px

from pivot import PivotBuilder
pivot_build = PivotBuilder()


def dashboard(df_options):

	if not df_options: 

		default = {

			'rev_dept': ['Outpatient','Inpatient']
		}

		query = ' & '.join([f"{key} == {repr(value)}" for key, value in default.items()])
		
		return query
	
	else: 
	
		query = ' & '.join([f"{key} == {repr(value)}" for key, value in df_options.items()])
		
		return query


query = dashboard(df_options = {})

pivot_build.query_df(query)

stats = pivot_build.summary_stats()

st.set_page_config(page_title="Income Dashboard", page_icon=":bar_chart:", layout="wide")

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")

df_options = {}
df_columns = []
 
department = st.sidebar.multiselect(
    "Department:",
    options=['Outpatient','Inpatient'],
    default=None
    
) 

if department:

    df_options['rev_dept'] = department
    
    query = dashboard(df_options)
    
    pivot_build.query_df(query)

    stats = pivot_build.summary_stats()


 
insurance = st.sidebar.multiselect(
    "Insurance:",
    options=stats["insurance"].sort_values().unique(),
    default=None
    
) 


if insurance:
    
    df_options['Scheme_Code'] = insurance
    
    query = dashboard(df_options)
    
    pivot_build.query_df(query)

    stats = pivot_build.summary_stats()


 
scheme = st.sidebar.multiselect(
    "Scheme:",
    options=stats["scheme"].sort_values().unique(),
    default=None
)

if scheme:
    
    df_options['scheme'] = scheme
    
    query = dashboard(df_options)
    
    pivot_build.query_df(query)

    stats = pivot_build.summary_stats()

   
 
service = st.sidebar.multiselect(
    "Service:",
    options=stats["service"].sort_values().unique(),
    default=None
)
    
if service:

    df_options['service'] = service
    
    query = dashboard(df_options)
    
    pivot_build.query_df(query)

    stats = pivot_build.summary_stats()



 
quarter = st.sidebar.multiselect(
    "Yearly Quarters:",
    options=stats["quarter"].sort_values().unique(),
    default=None
    
)
if quarter:

    df_options['Quarter'] = quarter
    
    query = dashboard(df_options)
    
    pivot_build.query_df(query)

    stats = pivot_build.summary_stats()



  
gender = st.sidebar.multiselect(
    "Gender:",
    options=stats["gender"].unique(),
    default=None
    
)
if gender:

    df_options['Gender'] = gender
    
    query = dashboard(df_options)
    
    pivot_build.query_df(query)

    stats = pivot_build.summary_stats()


age_group = st.sidebar.multiselect(
    "Age Group:",
    options=stats["age_group"].sort_values().unique(),
    default=None
    
)
if age_group: 

    df_options['AgeGroup'] = age_group
    
    query = dashboard(df_options)
    
    pivot_build.query_df(query)

    stats = pivot_build.summary_stats()

 


# ---- MAINPAGE ----
st.title(":bar_chart: Overview:")
st.markdown("##")


total_income = stats['Sum']
average_per_patient = stats['Mean']
no_of_patients = stats['Count']

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Revenue:")
    st.subheader(f"KSHS. {total_income:,}")
with middle_column:
    st.subheader("Total Patients Visits:")
    st.subheader(f"{no_of_patients}")
with right_column:
    st.subheader("Average Per Patient:")
    st.subheader(f"KSHS. {average_per_patient}")
    
st.markdown("""---""")

# INCOME BY INSURANCE [BAR CHART]
df_columns.append('Year')


Monthly = pivot_build.overall_pivot_table(index="Month", columns=df_columns, category=6)

month_order = ['January', 'February', 'March', 'April','May','June','July','August','September','October','November','December']

month_mapping = {month: i for i, month in enumerate(month_order, start=1)}

# Apply the month mapping to the pivot table
Monthly['Month'] = Monthly['Month'].replace(month_mapping)

# Sort the pivot table by the 'Month' column in ascending order
Monthly = Monthly.sort_values('Month')

# Reset the index
Monthly = Monthly.reset_index(drop=True)

# Update the month names in the pivot table
Monthly['Month'] = [month_order[month - 1] for month in Monthly['Month']]

print(Monthly)

# Create line chart
fig_monthly = px.line(Monthly, x="Month", y=Monthly.columns[1:], title='Monthly Revenue Trend',template="plotly_white",labels= {'variable': 'Monthly'}, markers=True)

# Update x-axis tick labels to display month names
fig_monthly.update_layout(
   
    plot_bgcolor="rgba(0,0,0,0)"
)

quarterly = pivot_build.overall_pivot_table(index="Quarter", columns=df_columns, category=6)

# Create line chart
fig_quarterly = px.line(quarterly, x="Quarter", y=quarterly.columns[1:], title='Quarterly Revenue Trend',template="plotly_white",labels= {'variable': 'Quarterly'}, markers=True)

# Update x-axis tick labels to display month names
fig_quarterly.update_layout(
     
    plot_bgcolor="rgba(0,0,0,0)"
)

weekly = pivot_build.overall_pivot_table(index="Week", columns=df_columns, category=6)

# Create line chart
fig_weekly = px.line(weekly, x="Week", y=weekly.columns[1:], title='Weekly Revenue Trend',template="plotly_white",labels= {'variable': 'weekly'}, markers=True)

# Update x-axis tick labels to display month names
fig_weekly.update_layout(
   
    plot_bgcolor="rgba(0,0,0,0)"
)



left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_quarterly, use_container_width=True)
middle_column.plotly_chart(fig_monthly, use_container_width=True)
right_column.plotly_chart(fig_weekly, use_container_width=True)

st.markdown("""---""")

diagnosis = pivot_build.diagnosis_pivot_table(columns='', category=0)

fig_diag = px.bar(
    diagnosis,
    
    x='Membership_Number',
    y='diagnosis',
    orientation="h",
    title="<b>Top 10 Diagnosis</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group'
)
fig_diag.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Amount',
    yaxis_title= 'Insurance'
     
)

diag_g = pivot_build.diagnosis_pivot_table(columns='Gender', category='')

fig_diag_g = px.bar(
    diag_g,
    
    x=diag_g.columns[1:],
    y='diagnosis',
    orientation="h",
    title="<b>Diagnosis by Gender</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Gender'}
)
fig_diag_g.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Amount',
    yaxis_title= 'Insurance'
     
)

diag_ag = pivot_build.diagnosis_pivot_table(columns='AgeGroup', category='')

fig_diag_ag = px.bar(
    diag_ag,
    
    x=diag_ag.columns[1:],
    y='diagnosis',
    orientation="h",
    title="<b>Diagnosis by Age Group</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Age Group'}
)
fig_diag_ag.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Amount',
    yaxis_title= 'Insurance'
     
)

left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_diag, use_container_width=True)
middle_column.plotly_chart(fig_diag_g, use_container_width=True)
right_column.plotly_chart(fig_diag_ag, use_container_width=True)

st.title(":bar_chart: Patient Demographic:")
st.markdown("""---""")

age_hist = pivot_build.overall_pivot_table(index="Age",category=3)

fig_hist = px.histogram(age_hist, x='Age', nbins=10,template="plotly_white",barmode='group')

# Update the layout
fig_hist.update_layout(
    xaxis_title='Age',
    yaxis_title='Frequency',
    title='Age Distribution Histogram'
)

page_group = pivot_build.overall_pivot_table(index="AgeGroup",category=4)

fig_age_group = px.bar(
    page_group,
    
    
    orientation="h",
    title="<b>Patient Age Group</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Age'}
)
fig_age_group.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title= 'Visits',
    yaxis_title= 'Age Group'
     
)

p_pie = pivot_build.overall_pivot_table(index="Gender",category=5)

fig_p_pie = px.pie(p_pie, values='count_pct', names='Gender',template="plotly_white")

fig_p_pie.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    title= 'Gender Distribution'
     
)

left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_hist, use_container_width=True)
middle_column.plotly_chart(fig_age_group, use_container_width=True)
right_column.plotly_chart(fig_p_pie, use_container_width=True)

st.title(":bar_chart: Revenue Breakdown:")
st.markdown("""---""")

rev_dept = pivot_build.overall_pivot_table(index='rev_dept', category=0)

fig_rev_dept = px.bar(
    rev_dept, 
    orientation="h",
    title="<b>Revenue Departments</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Revenue'}
)
fig_rev_dept.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Amount',
    yaxis_title= 'Department'
     
)

service = pivot_build.overall_pivot_table(index='service', category=0)

fig_service = px.bar(
    service,  
    orientation="h",
    title="<b>Revenue Per Service</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Age'}
)
fig_service.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Amount',
    yaxis_title= 'Service'
     
)

rev_pie = pivot_build.overall_pivot_table(index='rev_dept', category='')


fig_rev_pie = px.pie(rev_pie, values='count_pct', names='rev_dept',template="plotly_white")

fig_rev_pie.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    title= 'Revenue Distribution'
     
)
left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_rev_dept, use_container_width=True)
middle_column.plotly_chart(fig_service, use_container_width=True)
right_column.plotly_chart(fig_rev_pie, use_container_width=True)


st.title(":bar_chart: KPIs:")
st.markdown("""---""")

p_visits = pivot_build.KPIs(index='rev_dept', category=0)

fig_p_visits = px.bar(
    p_visits,
    
    
    orientation="h",
    title="<b>Patient Visits Per Department:</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Age'}
)
fig_p_visits.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Visits',
    yaxis_title= 'Department',
    showlegend=False
     
)


p_serv_visits = pivot_build.KPIs(index='service', category=0)

fig_p_serv_visits = px.bar(
    p_serv_visits,
    
    
    orientation="h",
    title="<b>Patient Per Service</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Age'}
)
fig_p_serv_visits.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Visits',
    yaxis_title= 'Services',
    showlegend=False
     
)

avg_visits = pivot_build.KPIs(index='service', category=1)


fig_avg_visits = px.bar(
    avg_visits,
    
    
    orientation="h",
    title="<b>Average Revenue per Visit:</b>",
    text_auto=True,
    template="plotly_white",
    barmode='group',
    labels= {'variable': 'Age'}
)
fig_avg_visits.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    xaxis_title= 'Mean Revenue',
    yaxis_title= 'Services',
    showlegend=False
     
)

left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_p_visits, use_container_width=True)
middle_column.plotly_chart(fig_p_serv_visits, use_container_width=True)
right_column.plotly_chart(fig_avg_visits, use_container_width=True)

st.markdown("""---""")

retention = pivot_build.KPIs(index='Membership_Number', category=2)

retention_rate = ((retention[retention > 1].count() / retention.count()) * 100).round(2)

# Create a bar chart using Plotly Express
fig_retention = px.bar(x=['Retention Rate'], y=[retention_rate.item()], labels={'x': 'Metrics', 'y': 'Retention Rate (%)'},
             title='Patient Retention Rate',template="plotly_white",text_auto=True)
             

repeat_visit = pivot_build.KPIs(index='Membership_Number', category=3)

repeat_visits = (repeat_visit[repeat_visit > 1].count())

# Create a bar chart using Plotly Express
fig_repeat = px.bar(x=['Repeat Visits'], y=[repeat_visits], labels={'x': 'Metrics', 'y': 'Number of Patients'},
             title='Repeat Visits',template="plotly_white",text_auto=True,)
fig_repeat.update_yaxes(title_text='Number of Patients')
fig_repeat.update_layout(showlegend=False)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_retention, use_container_width=True)
right_column.plotly_chart(fig_repeat, use_container_width=True)



st.title(":bar_chart: Forecasting:")
st.markdown("""---""")
