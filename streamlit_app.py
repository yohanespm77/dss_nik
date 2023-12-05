import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

# --- READ DATA ---
employ_merge = pd.read_pickle('data/employ_clean.pkl')
coord = pd.read_csv('data/coordinate.csv')

# --- ROW 1 ---
st.write('# Employee Demography Dashboard')
st.write("""Explore workforce dynamics at a glance with this Employee Demography Dashboard. 
         Track hiring trends over time, visualize employee distribution across provinces, 
         and delve into generational and gender insights within departments—all in one comprehensive view.""")

# --- ROW 2 ---
col1, col2 = st.columns(2)

## --- LINE PLOT ---

# data: line plot
df_join = pd.crosstab(index=employ_merge['join_year'],
                       columns='join_count', 
                       colnames=[None])
df_join = df_join.reset_index()

# plot: line plot
plot_join = px.line(df_join, x='join_year', y='join_count', markers=True,
                     labels = {
                         'join_year' : 'Year',
                         'join_count' : 'Employee Joining'})

col1.write('### Joining Frequency over Time')
col1.plotly_chart(plot_join, use_container_width=True)

## --- MAP PLOT ---
# data: map
prov_gender = pd.crosstab(index=employ_merge['province'],
                        columns=employ_merge['gender'], colnames=[None])
prov_gender['Total'] = prov_gender['Female'] + prov_gender['Male']
df_map = prov_gender.merge(coord, on='province')

# plot: map
plot_map = px.scatter_mapbox(data_frame=df_map, lat='latitude', lon='longitude',
                             mapbox_style='carto-positron', zoom=3,
                             size='Total',
                             hover_name='province',
                             hover_data={'Male': True,
                                         'Female': True,
                                         'latitude': False,
                                         'longitude': False})

col2.write('### Employee Count across Indonesia')
col2.plotly_chart(plot_map, use_container_width=True)

# --- ROW 3 ---
st.divider()
col3, col4 = st.columns(2)

## --- INPUT SELECT ---
input_select = col3.selectbox(
    label='Select Department',
    options=employ_merge['department_name'].unique().sort_values()
)

## --- INPUT SLIDER ---
input_slider = col4.slider(
    label='Select age range',
    min_value=employ_merge['age'].min(),
    max_value=employ_merge['age'].max(),
    value=[20,50]
)

min_slider = input_slider[0]
max_slider = input_slider[1]

# --- ROW 4 ---
col5, col6 = st.columns(2)

## --- BARPLOT ---
# data: barplot
employ_cs = employ_merge[employ_merge['department_name'] == input_select]
df_gen = pd.crosstab(index=employ_cs['generation'], columns='num_people', colnames=[None])
df_gen = df_gen.reset_index()

# plot: barplot
plot_gen = px.bar(df_gen, x='generation', y='num_people', 
                   labels = {'generation' : 'Generation',
                             'num_people' : 'Employee Count'})

col5.write(f'### Employee Count per Generation in {input_select} Dept.') # f-string
col5.plotly_chart(plot_gen, use_container_width=True)

## --- MULTIVARIATE ---
# data: multivariate
employ_age = employ_merge[employ_merge['age'].between(left=min_slider, right=max_slider)]
dept_gender = pd.crosstab(index=employ_age['department_name'],
                          columns=employ_age['gender'],
                          colnames=[None])
dept_gender_melt = dept_gender.melt(ignore_index=False, var_name='gender', value_name='num_people')
dept_gender_melt = dept_gender_melt.reset_index()

# plot: multivariate
plot_dept = px.bar(dept_gender_melt.sort_values(by='num_people'), 
                   x="num_people", y="department_name", 
                   color="gender", 
                   barmode='group',
                   labels = {'num_people' : 'Employee Count',
                             'department_name' : 'Department',
                             'gender': 'Gender'}
                             )

col6.write(f'### Gender per Department, Age {min_slider} to {max_slider}')
col6.plotly_chart(plot_dept, use_container_width=True)