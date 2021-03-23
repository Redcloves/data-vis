import holoviews as hv
import pandas as pd
from holoviews import opts
from holoviews.plotting.links import DataLink
hv.extension('bokeh')
from bokeh.sampledata.us_states import data as boheh_states

restrictions = pd.read_csv('plots/static/restrictions.csv', skiprows=[0, 1, 2, 4, 15])
data = pd.read_csv('plots/static/data.csv', usecols=['WEEK', 'ELECT_PX', 'PTNT_ST_ABBR', 'PATIENTS'], low_memory=False, nrows=422047)
states = restrictions['State']
surgery_type = ['MASTECTOMY', 'CABG', 'CATARACT', 'CYSTOSCOPY', 'HYSTEROSCOPY', 'PROSTATECTOMY', 'CHOLECYSTECTOMY', 'HIP REPLACEMENT', 'KNEE REPLACEMENT', 'COSMETIC RECONSTRUCTION']


states_data = {}   # dictonary of data by states
state_patients = []

for state in states:
    states_data[state] =data[data['PTNT_ST_ABBR']== state]

def total_weekly_patients(state):
    time = pd.to_datetime(states_data[state]['WEEK'])
    x = states_data[state].groupby(pd.to_datetime(time, unit='D')).sum()
    return x

# def total_state_patients(state):   # correct
#     return sum(states_data[state]['PATIENTS'])

def surgery_patients(state, surgery):
    patients = states_data[state]['ELECT_PX'].values == surgery
    return sum(states_data[state][patients]['PATIENTS'])

for index, row in restrictions.iterrows():
    total = 0
    d = dict(state = row['State'], Name= row['Name'])
    for surgery in surgery_type:
        patients = surgery_patients(row['State'], surgery)
        d[surgery] = patients
        total += patients
    d['Total'] = total
    d['lons'] = boheh_states[row['State']]['lons']
    d['lats'] = boheh_states[row['State']]['lats']
    state_patients.append(d)

def state_restriction(state, res):
    r = states == state
    return float(restrictions[r][res])

def plot_states():
    map_data = [(state['Name'], state['Total'], int(state_restriction(state['state'], 'RANK RESTR')), state_restriction(state['state'], 'SCORE RESTR')) for state in state_patients]
    choropleth = hv.Polygons(state_patients, ['lons', 'lats'], ['Name', 'Total'], label='Total patients in the US')
    table = hv.Table(map_data, ['Name', 'Total', 'Ranking*', 'Score*'])

    DataLink(choropleth, table)

    d= (choropleth + table).opts(
        opts.Table(height=428),
        opts.Polygons(logz=True, width=650, height=440,  tools=['hover', 'tap'], xaxis=None, yaxis=None,
                      color_index='Total', colorbar=True, toolbar='above', line_color='white', cmap='Oranges'))
    fig = hv.render(d)
    return fig

def plot_weekly(state):
    data = total_weekly_patients(state)
    data_plot = hv.Curve(data, label='Total number of patients by week.').opts(width=650, tools=['hover'])
    for i in state_patients:
        if i['state'] == state:
            table_data = [(k.capitalize(),i[k]) for k in surgery_type]
            table_data.append(('Total', i['Total']))
            break
    table = hv.Table(table_data, ['Surgery', 'No Patients']).opts(width=380)
    d = ( data_plot + table )
    fig = hv.render(d)
    return fig

# state = 'CA'
# time = pd.to_datetime(states_data[state]['WEEK'])
# x = states_data[state].groupby(time).sum()
# pd.to_datetime(x.index.values, unit='D')

# https://www.youtube.com/watch?v=YlOVR_1q4Ak
# http://docs.bokeh.org/en/0.11.0/docs/user_guide/embed.html#userguide-embed
# http://holoviews.org/user_guide/Deploying_Bokeh_Apps.html
# print(pd.to_datetime(total_weekly_patients('CA').index.values, unit='D'))
# print(total_weekly_patients('CA').index.values)

