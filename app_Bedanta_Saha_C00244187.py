from flask import Flask, render_template, send_file

import pandas as pd

from sqlalchemy import create_engine

import altair as alt

app = Flask(__name__)

@app.route("/")
def default():
    return render_template("home_Bedanta_Saha_C00244187.html")

def get_data():
    engine = create_engine("mysql+pymysql://salutemuser:salutempasswd@localhost/salutemDB")    
    scraped_data = pd.read_sql_query("select * from scraped", engine)
    therapyareas_data = pd.read_sql_query("select * from therapyareas", engine)
    date_range=scraped_data.copy()
    for index,row in date_range.iterrows():
        if row['rr_start'] is None:
            _start=row['earliest']
            date_range.loc[index,'rr_start']=_start
            _end=row['latest']
            date_range.loc[index,'rr_end']=_end
            _start_str=str(_start)
            _end_str=str(_end)
            date_range.loc[index,'rr_dates']= _start_str +", " + _end_str
            date_range.loc[index,'rr_outcome']='Unknown'
    date_range['rr_range']=date_range['rr_end']-date_range['rr_start']
    for index,row in date_range.iterrows():
        date_range.loc[index,'rr_range']=row['rr_range'].days
    for index,row in date_range.iterrows():
        if row['rr_range']<0:
            _end=row['rr_start']
            _start=row['rr_end']
            date_range.loc[index,'rr_start']=_start
            date_range.loc[index,'rr_end']=_end
    date_range['rr_range']=date_range['rr_end']-date_range['rr_start']
    for index,row in date_range.iterrows():
        date_range.loc[index,'rr_range']=row['rr_range'].days
    for index, row in date_range.iterrows() :
        if row['ema_url']== '':
            date_range.drop(index,inplace=True)
    for index,row in date_range.iterrows():
        if row['company']=='':
            date_range.loc[index,'company']='Unknown'
    return date_range


@app.route('/Vis1')
def display_Vis1():
    date_range = get_data()
    for index,row in date_range.iterrows():
        date_range.loc[index,'rr_end_year']=int(row['rr_end'].year)
    end_year_range = date_range.groupby(['rr_end_year','orphan'])['rr_range'].mean().reset_index(name='mean_range')
    Vis1_1=alt.Chart(end_year_range,title="Yearly average Rapid Review time for Orphan and Non-Orphan Drugs").mark_line().encode(
    alt.X('rr_end_year', axis=alt.Axis(title='Rapid Review Ending Year')),
    alt.Y('mean_range', axis=alt.Axis(title='Average Rapid Review time taken')),
    color='orphan:N'
    )
    end_year_count=date_range.groupby(['rr_end_year','orphan']).size().reset_index(name='count')
    Vis1_2=alt.Chart(end_year_count,title="Yearly Reviewed drugs count for Orphan and Non-Orphan Drugs").mark_line().encode(
    alt.X('rr_end_year', axis=alt.Axis(title='Rapid Review Ending Year')),
    alt.Y('count', axis=alt.Axis(title='Number of reviewed drugs')),
    color='orphan:N'
    )
    Vis1=Vis1_1|Vis1_2
    Vis1.save('Vis1.html')
    return send_file('Vis1.html')

@app.route('/Vis2')
def display_Vis2():
    date_range = get_data()
    company_count_ncpe=date_range.groupby(['ncpe_year','company']).size().reset_index(name='count')
    for index,row in date_range.iterrows():
        date_range.loc[index,'eu_market']=int(row['eu_market'].year)
    company_count_eu=date_range.groupby(['eu_market','company']).size().reset_index(name='count')
    Vis2_1=alt.Chart(company_count_ncpe,title="NCPE Year wise number of drug released by each company").mark_bar().encode(
    alt.X('company', axis=alt.Axis(title='Company Name')),
    alt.Y('ncpe_year:N', axis=alt.Axis(title='NCPE Year')),
    color='count:N'
    )
    Vis2_2=alt.Chart(company_count_eu,title="Eu market year wise number of drug released by each company").mark_bar().encode(
    alt.X('company', axis=alt.Axis(title='Company Name')),
    alt.Y('eu_market:N', axis=alt.Axis(title='Eu Market Year')),
    color='count:N'
    )
    Vis2= Vis2_1 & Vis2_2
    Vis2.save('Vis2.html')
    return send_file('Vis2.html')

@app.route('/Vis3')
def display_Vis3():
    date_range = get_data()
    rr_status_rr_range=date_range.groupby(['rr_status','orphan'])['rr_range'].mean().reset_index(name='mean_range')
    Vis3=alt.Chart(rr_status_rr_range,title='Rapid Review Status wise average Rapid Review timetaken for orphan and non-orphan drugs').mark_bar().encode(
    alt.X('rr_status:N', 
          axis=alt.Axis(title='Rapid Review Status',labelAngle=-45),
         ),
    alt.Y('mean_range',
          axis=alt.Axis(title='Average Rapid Review Days Taken'),
         ),
    color="orphan:N"
    ).properties(
    width=700,
    height=300,
    )
    Vis3.save('Vis3.html')
    return send_file('Vis3.html')

@app.route('/Vis4')
def display_Vis4():
    date_range = get_data()
    drug_count_ncpe=date_range.groupby('ncpe_year').size().reset_index(name='count')
    for index,row in date_range.iterrows():
        date_range.loc[index,'eu_market']=int(row['eu_market'].year)
    drug_count_eu=date_range.groupby('eu_market').size().reset_index(name='count')
    Vis4_1=alt.Chart(drug_count_ncpe,title='NCPE Year wise and Eu Market year wise total number of drugs released').mark_line().encode(
    alt.X('ncpe_year:N',
          axis=alt.Axis(title=' The Red line and the blue line represent the drugs released in Eu market and NCPE respectively')),
    alt.Y('count',
          axis=alt.Axis(title='Number of drug reseased'))     
    )
    Vis4_2=alt.Chart(drug_count_eu).mark_line(color='red').encode(
    x='eu_market:N',
    y='count'
    )
    Vis4=(Vis4_1+Vis4_2)
    Vis4.save('Vis4.html')
    return send_file('Vis4.html')

@app.route('/Vis5')
def display_Vis5():
    date_range = get_data()
    for index,row in date_range.iterrows():
        date_range.loc[index,'eu_ncpe_year_gap']=int(row['ncpe_year']-row['eu_market'].year)
    eu_ncpe_gap_orphan= date_range[date_range['orphan']==1].groupby('company')['eu_ncpe_year_gap'].mean().reset_index(name='mean_gap')
    eu_ncpe_gap_non_orphan= date_range[date_range['orphan']!=1].groupby('company')['eu_ncpe_year_gap'].mean().reset_index(name='mean_gap')
    Vis5_1=alt.Chart(eu_ncpe_gap_orphan,title="EU to IE time for Orphan Drugs").mark_bar().encode(
    alt.Y('company:N', 
          axis=alt.Axis(title='Drugs Company'),
         ),
    alt.X('mean_gap', 
          axis=alt.Axis(title='Average year gap between a drug released in Eu market and NCPE'),
         )
    ).properties(width=200,
    height=800)
    Vis5_2=alt.Chart(eu_ncpe_gap_non_orphan,title="EU to IE time for Non-Orphan Drugs").mark_bar().encode(
    alt.Y('company:N', 
          axis=alt.Axis(title='Drugs Company'),
         ),
    alt.X('mean_gap', 
          axis=alt.Axis(title='Average time between a drug released in Eu market and NCPE'),
         )
    ).properties(width=200,
    height=800)
    Vis5=(Vis5_1 | Vis5_2)
    Vis5.save('Vis5.html')
    return send_file('Vis5.html')
app.run(debug=True)
    