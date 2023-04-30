!pip install dash
!pip install jupyter_dash

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

wage_gap_text = "The gender wage gap is the proposition that men on average make more money than women in similar roles. The US Department of Labor (DOL) states that women are paid 83.7% of what men are paid. The gap is even larger black and hispanic women. The causes are vast, but the DOL suggests that one main cause is that women are generally undervalued. Source: https://blog.dol.gov/2023/03/14/5-fast-facts-the-gender-wage-gap"

gss_text = "The General Social Survey (GSS) data is survey data collected from US adults since 1972. It contains various demographic information, as well as questions which aim to get an undetstanding of how the general US popularion feels. The data used in this dashboard focues on data such as socioeconomic index and salary of men and women, to evaluate the gender wage gap identified above. Source: http://www.gss.norc.org/About-The-GSS"

gender_means = gss_clean[['income', 'job_prestige', 'socioeconomic_index', 'education', 'sex']].groupby('sex')
gender_means = gender_means.mean().round(2).reset_index()

gender_means = gender_means.rename({'sex':'Gender',
                                   'income':'Avg. Income',
                                   'job_prestige':'Avg. Occupational Prestige',
                                   'socioeconomic_index':'Avg. Socioeconomic Index',
                                   'education':'Avg. Years of Education'}, axis=1)

table = ff.create_table(gender_means)
table.show()

grouped_data = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index(name='count')

bar_fig = px.bar(grouped_data, x='male_breadwinner', y='count',
                 color='sex',
                 barmode='group',
                 text='count',
                 labels={'male_breadwinner': 'Response to Male Breadwinner', 'count': 'Number of Responses', 'sex': 'Gender'})

bar_fig.show()

scatter_fig = px.scatter(gss_clean, x='job_prestige', y='income',
                         color='sex',
                         trendline='ols',
                         hover_data=['education', 'socioeconomic_index'],
                         labels={'sex': 'Gender', 'job_prestige': 'Occupational Prestige', 'income': 'Income',
                                 'education':'Education', 'socioeconomic_index': 'Socioeconomic Index'})

scatter_fig.show()

#income
income_box = px.box(gss_clean, x='sex', y='income', color='sex')

income_box.update_layout(
    xaxis_title='',
    yaxis_title='Income',
    showlegend=False
)

income_box.show()

#job_prestige
job_prestige_box = px.box(gss_clean, x='sex', y='job_prestige', color='sex')

job_prestige_box.update_layout(
    xaxis_title='',
    yaxis_title='Occupational Prestige',
    showlegend=False
)

job_prestige_box.show()

income_prestige = gss_clean[['income', 'sex', 'job_prestige']]

income_prestige['prestige_category'] = pd.cut(income_prestige['job_prestige'], bins=6,
                                              labels=['Very Low', 'Low', 'Moderately Low', 'Moderately High', 'High', 'Very High'])

income_prestige = income_prestige.dropna()

facet_grid = px.box(income_prestige, x='sex', y='income', color='sex',
                    facet_col='prestige_category', facet_col_wrap=2,
                    color_discrete_map={'male': 'blue', 'female': 'red'},
                    labels={'income': 'Income', 'sex': 'Gender', 'prestige_category': 'Occupational Prestige Category'})

facet_grid.show()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H2("Gender Wage Gap"),
        dcc.Markdown(children = wage_gap_text),
        dcc.Markdown(children = gss_text),
     
        html.H3("Income, Prestige, Socioeconomic Index, and Years of Education per Gender Table"),
        dcc.Graph(figure=table),
     
        html.H3("Male Breadwinner Agreement"),
        dcc.Graph(figure=bar_fig),

        html.H3("Occupational Prestige and Income per Gender Scatterplot"),
        dcc.Graph(figure=scatter_fig),

        html.Div([
            
            html.H3("Income per Gender"),
            
            dcc.Graph(figure=income_box)
            ], style = {'width':'48%', 'float':'left'}),
        
            html.Div([
            
            html.H3("Occupational Prestige per Gender"),
            
            dcc.Graph(figure=job_prestige_box)
            
        ], style = {'width':'48%', 'float':'right'}),
     
        html.H3("Occupational Prestige Levels per Gender and Income"),
        dcc.Graph(figure=facet_grid)
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
