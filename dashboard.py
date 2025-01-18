import streamlit as st
import plotly.express as px 
import pandas as pd
import os
import io
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!",page_icon=":bar_chart:",layout="wide")
                   
st.title(" :bar_chart: Sample Supers=store EDA")

fl = st.file_uploader(":file_folder: upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
else:
    os.chdir(r"C:\Users\DELL\Desktop\db project")
    df = pd.read_excel("Superstore.xls")
    
    
col1, col2 = st.columns((2))
df["order Date"] = pd.to_datetime(df["Order Date"])

#getting main max date
startDate = pd.to_datetime(df["order Date"]).min()
endDate = pd.to_datetime(df["order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))
    
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy() 

st.sidebar.header("choose your filter: ")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())  
#create for reason
if not region:
    df2 = df.copy()
else:
    df2 =df[df["Region"].isin(region)]
    
    #create for state
State = st.sidebar.multiselect("pick the state", df2["State"].unique())
if not State:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(State)]
    
    #create for city
City = st.sidebar.multiselect("pick the city", df3["City"].unique())  

#filter the data based on region,state and city
if not region and not State and not City:
    filtered_df = df
elif not State and not City:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not City:
    filtered_df = df[df["State"].isin(State)]
elif State and City:
    filtered_df = df3[df["State"].isin(State) & df3["City"].isin(City)]
elif region and City:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(City)]
elif region and State:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(City)]
elif City:
    filtered_df = df3[df3["City"].isin(City)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(State) & df3["City"].isin(City)]
    # Debug column names and data
print(filtered_df.columns)  # Ensure 'category' exists
print(filtered_df.head())  # Check the data

# Group by the correct column name
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    # Assuming filtered_df is already defined and contains the necessary columns
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")

# Create the linechart DataFrame by grouping and summing Sales
linechart = pd.DataFrame(
    filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()
).reset_index()

# Plotting the line chart using Plotly
import plotly.express as px

fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)


if "linechart" not in locals() or linechart.empty:
    st.error("Error: `linechart` is not defined or empty. Please verify the data.")
else:
    cl1, cl2 = st.columns((2))
    
    # Category View Data
    with st.expander("Category_ViewData"):
        st.write(category_df)
        category_csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=category_csv, file_name="Category.csv", mime="text/csv")

    # Region View Data
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region)
        region_csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=region_csv, file_name="Region.csv", mime="text/csv")
    
    # TimeSeries Excel File Download
    with st.expander("View Data of TimeSeries:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))

        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            linechart.to_excel(writer, index=False, sheet_name="TimeSeries")
        
        st.download_button(
            label="Download Data as Excel",
            data=excel_buffer.getvalue(),
            file_name="TimeSeries.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        # Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)
# Correct indentation
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))