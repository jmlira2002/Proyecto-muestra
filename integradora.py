import streamlit as st
import pandas as pd
import numpy as np
import plotly as px
import plotly.express as px2
from PIL import Image
import base64
import plotly.figure_factory as ff

st.set_page_config(
    page_title="Police Incident Report 2018 - 2020 San Francisco",
    page_icon="👮‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def logo_to_base64(image):
    import base64
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

######Cargar logo y encabezado de tablero################
logo_path = "Police.png"
logo = Image.open("Police.png")
title = "Police Incident Reports from 2018 to 2020 in San Francisco"
st.markdown(
    """
    <div style="display: flex; align-items: center; background-color: #202c81; padding: 1rem; border-radius: 8px;">
        <img src="data:image/png;base64,{}" alt="Logo" style="width: 70px; height: 70px; margin-right: 40px;">
        <h1 style="color: white;"> {}</h1>
    </div>
    """.format(logo_to_base64(logo), title),
    unsafe_allow_html=True,
)

df1 = pd.read_csv("Police1.csv")
df2 = pd.read_csv("Police2.csv")
df3 = pd.read_csv("Police3.csv")
df4 = pd.read_csv("Police4.csv")
df5 = pd.read_csv("Police5.csv")
df6 = pd.read_csv("Police6.csv")

df = df_final = pd.concat([df1, df2, df3, df4, df5, df6], ignore_index=True)

df['Incident Date'] = pd.to_datetime(df['Incident Date'])
df['Incident Datetime'] = pd.to_datetime(df['Incident Datetime'])
st.markdown('The data shown below belongs to incident reports in the city of San Francisco, from the year 2018 to 2020, with details from each case such as date, day of the week, police district, neighborhood in which it happened, type of incident in category and subcategory, exact location and resolution.')
mapa = pd.DataFrame()
mapa['Date'] = df['Incident Date']
mapa['Date'] = pd.to_datetime(mapa['Date'])
mapa['Day'] = df['Incident Day of Week']
mapa['Police District'] = df['Police District']
mapa['Neighborhood'] = df['Analysis Neighborhood']
mapa['Incident Category'] = df['Incident Category']
mapa['Incident Subcategory'] = df['Incident Subcategory']
mapa['Resolution'] = df['Resolution']
mapa['lat'] = df['Latitude']
mapa['lon'] = df['Longitude']
mapa['Year'] = df['Incident Date'].dt.year.astype(str)
mapa['Month'] = df['Incident Date'].dt.strftime('%B')
mapa['Hour'] = df['Incident Datetime'].dt.hour
mapa = mapa.dropna()

subset_data2 = mapa
police_district_input = st.sidebar.multiselect(
'Police District',
mapa.groupby('Police District').count().reset_index()['Police District'].tolist(), default={'Bayview', 'Central', 'Park'})
if len(police_district_input) > 0:
    subset_data2 = mapa[mapa['Police District'].isin(police_district_input)]
    
subset_data1 =subset_data2
neighborhood_input = st.sidebar.multiselect(
'Neighborhood',
subset_data2.groupby('Neighborhood').count().reset_index()['Neighborhood'].tolist(), default=['Chinatown', 'Tenderloin', 'Seacliff', 'Excelsior'])
if len(neighborhood_input) > 0:
    subset_data1 = subset_data2[subset_data2['Neighborhood'].isin(neighborhood_input)]

subset_data3 = subset_data1
incident_input = st.sidebar.multiselect(
'Incident Category',
subset_data1.groupby('Incident Category').count().reset_index()['Incident Category'].tolist(), default=['Assault', 'Burglary', 'Fraud', 'Homicide'])

if len(incident_input) > 0:
    subset_data3 = subset_data1[subset_data1['Incident Category'].isin(incident_input)]

start_date = pd.to_datetime(st.sidebar.date_input("Start Date", subset_data3.Date.min()))
end_date = pd.to_datetime(st.sidebar.date_input("End Date", subset_data3.Date.max()))

if start_date and end_date:
    subset_data = subset_data3[(subset_data3['Date'] >= start_date) & (subset_data3['Date'] <= end_date)]
    
subset_data


st.markdown('It is important to mention that any police district can answer to any incident, the neighborhood in which it happened is not related to the police district.')
st.markdown('Crime locations in San Francisco')
st.map(subset_data)
st.markdown('Crimes ocurred per day of the week')
st.bar_chart(subset_data['Day'].value_counts())
st.markdown('Crimes ocurred per date')
st.line_chart(subset_data['Date'].value_counts())
st.markdown('Type of crimes commited')
st.bar_chart(subset_data['Incident Category']. value_counts())

agree =st.button('Click to see Incident subcategories')
if agree:
    st.markdown('Subtype of crimes commited')
    st.bar_chart(subset_data['Incident Category'].value_counts())


st.markdown('Resolution status')
fig1 = px2.pie(subset_data, names='Resolution', title='Resolutions Distribution')
fig1.update_layout(width = 1200)
st.plotly_chart(fig1)

subset_data3 = subset_data.copy()
year_tend = st.multiselect('Year',subset_data3['Year'].unique().tolist(), default='2018')
if len(year_tend) > 0:
    subset_data3 = subset_data[subset_data['Year'].isin(year_tend)]
month_tend = st.multiselect('Month',subset_data3['Month'].unique().tolist(), default=('January', 'February', 'March'))
if len(month_tend) > 0:
    subset_data3 = subset_data3[subset_data3['Month'].isin(month_tend)]


Tendencia = subset_data3.groupby(['Year', 'Month', 'Incident Category'])['Incident Category'].count().reset_index(name='Crimes')
figTend = px2.line(Tendencia, x="Month", y="Crimes", color='Incident Category', line_group='Year')
figTend.update_layout(title_text='Crimes Trends in San Francisco by Category and Date', width = 1200)
st.plotly_chart(figTend)

subset_data4 = subset_data.copy()
hour_bar = st.multiselect('Hour',subset_data3['Hour'].sort_values().unique().tolist())
if len(hour_bar) > 0:
    subset_data4 = subset_data[subset_data['Hour'].isin(hour_bar)]

hourly_crime_counts = subset_data.groupby('Hour').size().reset_index(name='Total Crimes')
figbar = px2.bar(hourly_crime_counts, x='Hour', y='Total Crimes', title='Crimes Occurred by Hour')
figbar.update_layout(width=800)

grouped_data = subset_data4.groupby(['Incident Category', 'Incident Subcategory']).size().reset_index(name='Total Crimes')
grouped_data['Percentage'] = grouped_data['Total Crimes'] / grouped_data['Total Crimes'].sum() * 100

figcrimes = px2.sunburst(grouped_data, path=['Incident Category', 'Incident Subcategory'], values='Total crimes')

#figcrimes = px2.sunburst(grouped_data, path=['Incident Category', 'Incident Subcategory'], values='Total Crimes', color='Percentage', color_continuous_scale='ice',title='Crimes by Category and Subcategory')
#figcrimes.update_traces(hovertemplate='<b>%{label}</b><br>Total Crimes: %{value}<br>Percentage: %{color:.2f}%')
#figcrimes.update_layout(width = 400)

col= st.columns([800,400])
with col[0]:
 st.plotly_chart(figbar)
with col[1]:
 st.plotly_chart(figcrimes)
st.write('#### ← I recommend that you visit your neighborhood')
