import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Qgo Finance Dashboard", page_icon=":bar_chart:", layout="wide")

# Add a logo image at the top
st.image("qgo_logo.svg", width=250)  # Adjust width as needed

# Streamlit App Setup
st.title('Finance Data Visualization')

# Define static target sales (500,000 KD per month)
TARGET_SALES = 500000

# Static Excel File
file_path = "ERP_OCT2024_Ali.xlsx"  # Static file path

# Load the data from the static Excel file
xls = pd.ExcelFile(file_path)
sheet_name = xls.sheet_names[0]  # Use the first sheet
df = pd.read_excel(xls, sheet_name=sheet_name)

st.write("This system was Developed by Qgo ")

# Sidebar filters
st.sidebar.header('Filter Options')

# Refresh button in the sidebar
if st.sidebar.button('Refresh Data'):
    st.rerun()  # Use st.rerun() to refresh the app

# Filter options based on columns
department = st.sidebar.multiselect('Select Department', df['Department'].unique(),
                                    default=df['Department'].unique())
invoice_type = st.sidebar.multiselect('Select Invoice Type', df['INVOICE_TYPE'].unique(),
                                      default=df['INVOICE_TYPE'].unique())
supplier_code = st.sidebar.multiselect('Select Supplier Code', df['SUPPLIER_CODE'].unique(),
                                       default=df['SUPPLIER_CODE'].unique())

# Apply filters to the data
filtered_df = df[(df['Department'].isin(department)) &
                 (df['INVOICE_TYPE'].isin(invoice_type)) &
                 (df['SUPPLIER_CODE'].isin(supplier_code))]

# Display target process on top
st.subheader('Department Sales vs Target')

# Group data by Department and calculate the total COMPANY_SELLING_PRICE
department_sales = filtered_df.groupby('Department')['COMPANY_SELLING_PRICE'].sum().reset_index()

# Display sales progress against target for each department using Plotly indicators
for i, row in department_sales.iterrows():
    department_name = row['Department']
    sales = row['COMPANY_SELLING_PRICE']
    progress = sales / TARGET_SALES
    progress_percent = min(progress, 1.0) * 100  # Limit to 100%

    # Create Plotly indicator for each department
    fig_indicator = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sales,
        delta={'reference': TARGET_SALES, 'position': "top"},
        gauge={
            'axis': {'range': [0, TARGET_SALES]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, TARGET_SALES * 0.75], 'color': "lightgray"},
                {'range': [TARGET_SALES * 0.75, TARGET_SALES], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': TARGET_SALES
            }
        },
        title={'text': f"Department: {department_name}"},
        number={'suffix': " KD"}
    ))

    st.plotly_chart(fig_indicator)

    # Display additional messages based on progress
    if progress_percent >= 100:
        st.success(f"{department_name} has reached or exceeded the target!")
    else:
        st.info(f"{department_name} is at {progress_percent:.2f}% of the target.")

# Group data by COST_OBJECT and calculate the total COMPANY_SELLING_PRICE
cost_object_group = filtered_df.groupby('COST_OBJECT')['COMPANY_SELLING_PRICE'].sum().reset_index()

# Calculate Profit for each row
filtered_df['Profit'] = filtered_df['COMPANY_SELLING_PRICE'] - filtered_df['COMPANY_COST_PRICE']

# Group data by COST_OBJECT and calculate total Profit
profit_group = filtered_df.groupby('COST_OBJECT')['Profit'].sum().reset_index()

# Create a single row for graphs
col1, col2 = st.columns([1, 1])  # Equal width for both columns

# 1st Graph: Bar chart with different colors and markers
with col1:
    st.subheader('Total Selling Price by Projects')
    fig1 = px.bar(cost_object_group, x='COST_OBJECT', y='COMPANY_SELLING_PRICE',
                  labels={'COST_OBJECT': 'Cost Object', 'COMPANY_SELLING_PRICE': 'Total Company Selling Price'},
                  color='COST_OBJECT',  # Different color for each cost object
                  color_discrete_sequence=px.colors.qualitative.Set2)  # Set2 color scheme
    fig1.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))  # Add marker outlines
    fig1.update_layout(hovermode="x")  # Add hover interaction
    st.plotly_chart(fig1)
st.markdown("<br><br>", unsafe_allow_html=True)

# 2nd Graph: Horizontal bar chart with a different color scale
with col2:
    st.subheader('Total Profit Price by Projects')
    fig2 = px.bar(profit_group, x='Profit', y='COST_OBJECT',  # Horizontal bar chart
                  labels={'COST_OBJECT': 'Cost Object', 'Profit': 'Total Profit'},
                  color='Profit',  # Color by profit values
                  color_continuous_scale=px.colors.sequential.Viridis)  # Sequential color scale
    fig2.update_traces(marker_line_color='black', marker_line_width=1.5)  # Add thicker marker lines
    fig2.update_layout(hovermode="y")  # Add hover interaction
    st.plotly_chart(fig2)

# New row for side-by-side scatter and pie chart
col3, col4 = st.columns(2)

# Scatter plot for Selling Price by Type
with col3:
    st.subheader('Total Selling Price by Type')
    description_sum = filtered_df.groupby('DESCRIPTION1')['COMPANY_SELLING_PRICE'].sum().reset_index()
    fig3 = px.scatter(description_sum, x='DESCRIPTION1', y='COMPANY_SELLING_PRICE',
                      labels={'DESCRIPTION1': 'Type', 'COMPANY_SELLING_PRICE': 'Total Company Selling Price'},
                      color='COMPANY_SELLING_PRICE',  # Color by selling price
                      size='COMPANY_SELLING_PRICE',  # Bubble size by selling price
                      color_continuous_scale=px.colors.diverging.Temps)  # Diverging color scale
    fig3.update_traces(marker=dict(opacity=0.7, sizemode='area'))  # Adjust marker transparency
    fig3.update_layout(hovermode="x unified")  # Unified hover for more interaction
    st.plotly_chart(fig3)

# Pie chart for Supplier's Total Selling Price
with col4:
    st.subheader('Total Selling Price by Supplier')
    supplier_sales = filtered_df.groupby('SUPPLIER_CODE')['COMPANY_SELLING_PRICE'].sum().reset_index()
    fig_pie = px.pie(supplier_sales, values='COMPANY_SELLING_PRICE', names='SUPPLIER_CODE',

                     color_discrete_sequence=px.colors.qualitative.Pastel)  # Use Pastel colors
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie)

# Optional: Auto-refresh every 15 minutes (900 seconds)
REFRESH_INTERVAL = 900  # 15 minutes in seconds
time.sleep(REFRESH_INTERVAL)
st.rerun()
