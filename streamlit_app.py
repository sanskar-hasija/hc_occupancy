import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os 
import glob

def process_pickup(pickup):
    pickup['report_date']=pd.to_datetime(pickup['report_date'])
    pickup['stay_date']=pd.to_datetime(pickup['stay_date'])

    rooms_df = pickup[['report_date','stay_date','dynamic_rooms','total_rooms','dynamic_room_revenue','total_room_revenue']]
    return rooms_df


old_bookings = pd.read_parquet('data/processed_bookings_old.parquet')
groups = ['direct', 'indirect' ,'ota', 'general']



bookings = pd.read_parquet('data/processed_bookings.parquet')

min_report_date = "2023-01-01"

old_bookings = old_bookings.query(f'report_date >= "{min_report_date}" & stay_date >= "{min_report_date}"')
bookings = bookings.query(f'report_date >= "{min_report_date}" & stay_date >= "{min_report_date}"')
plot_data = old_bookings.copy()

max_report_date = plot_data.report_date.max()
new_max_report_date = max_report_date + pd.DateOffset(months=4)
zmin = plot_data.cumulative_total_bookings.min()
zmax = plot_data.cumulative_total_bookings.max()

max_bookings = st.slider(
        'Select Max Occupancy for Color Range',
        min_value=1,
        max_value=int(zmax),
        value = 50
    )
zmax = max_bookings
zmin = 0
zero_position = abs(zmin) / (zmax - zmin)

custom_colorscale = [
    [0, 'white'],           
    [1, 'red']            
]


plot_data_total_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_total_bookings')  
plot_data_individual_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_individual_bookings')
plot_data_dynamic_group_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_dynamic_group_bookings')
plot_data_static_individual_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_static_individual_bookings')
plot_data_direct_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_direct_bookings')
plot_data_indirect_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_indirect_bookings')
plot_data_ota_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_ota_bookings')
plot_data_direct_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_direct_bookings')
plot_data_indirect_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_indirect_bookings')
plot_data_ota_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_ota_bookings')
plot_data_other_type_bookings = plot_data.pivot(index = 'report_date', columns = 'stay_date', values = 'cumulative_other_type_bookings')

plot_data2 = bookings.copy()
groups = ['RMA', 'RMB', 'RMC', 'RMD', 'RME', 'RMF', 'RMG', 'RMH', 'RMI', 'RMJ', 'RMK', 'RML', 'RMQ', 'RMT', 'RMZ', 'others']
plot_data_group_dfs = { group: pd.DataFrame() for group in groups}
for group in groups:
    plot_data_group = plot_data2.pivot(index = 'report_date', columns = 'stay_date', values = f'cumulative_{group}_bookings')  
    plot_data_group_dfs[group] = plot_data_group


trace_individual = go.Heatmap(
    z=plot_data_individual_bookings,
    x=plot_data_individual_bookings.columns,
    y=plot_data_individual_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_dynamic_group = go.Heatmap(
    z=plot_data_dynamic_group_bookings,
    x=plot_data_dynamic_group_bookings.columns,
    y=plot_data_dynamic_group_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_static_group = go.Heatmap(
    z=plot_data_static_individual_bookings,
    x=plot_data_static_individual_bookings.columns,
    y=plot_data_static_individual_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_total = go.Heatmap(
    z=plot_data_total_bookings,
    x=plot_data_total_bookings.columns,
    y=plot_data_total_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= True
)

fig = go.Figure(data=[trace_individual, trace_dynamic_group, trace_static_group, trace_total])



buttons = [
    dict(
        label="Individual",
        method="update",
        args=[{"visible": [True, False, False, False]}],
    ),
    dict(
        label="Dynamic Group",
        method="update",
        args=[{"visible": [False, True, False, False]}],
    ),
    dict(
        label="Static Individual",
        method="update",
        args=[{"visible": [False, False, True, False]}],
    ),
    dict(
        label="Total Bookings",
        method="update",
        args=[{"visible": [False, False, False, True]}],
    ),
]


fig.update_layout(
    title=f'Occupancy Analysis Segment - 1: Report Date Range: {min_report_date} - {max_report_date.date()}',
    title_x=0.15,
    updatemenus=[{
        'type': 'buttons',
        'direction': 'right',
        'x': 0.65,
        'y': 1.15,
        'showactive': True,
        'active': 0,
        'buttons': buttons
    }
    ]
)
fig.update_xaxes(title_text="Stay Date")
fig.update_yaxes(title_text="Report Date")

st.write("Occupancy Analysis Segment 1:  Individual vs Static Indivdual vs Dynamic Groups ")
# Show figure
st.plotly_chart(fig)



trace_direct = go.Heatmap(
    z=plot_data_direct_bookings,
    x=plot_data_direct_bookings.columns,
    y=plot_data_direct_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='Direct Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= True
)

trace_indirect = go.Heatmap(
    z=plot_data_indirect_bookings,
    x=plot_data_indirect_bookings.columns,
    y=plot_data_indirect_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='Indirect Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)

trace_ota = go.Heatmap(
    z=plot_data_ota_bookings,
    x=plot_data_ota_bookings.columns,
    y=plot_data_ota_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='OTA Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_other_type = go.Heatmap(
    z=plot_data_other_type_bookings,
    x=plot_data_other_type_bookings.columns,
    y=plot_data_other_type_bookings.index,
    colorscale=custom_colorscale,
    colorbar=dict(title='Other Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)


fig = go.Figure(data=[trace_direct, trace_indirect, trace_ota, trace_other_type, trace_total])



buttons = [
    
    dict(
        label="Direct",
        method="update",
        args=[{"visible": [True, False, False, False, False]}],
    ),
    dict(
        label="Indirect",
        method="update",
        args=[{"visible": [False, True, False, False, False]}],
    ),
    dict(
        label="OTA",
        method="update",
        args=[{"visible": [False, False, True, False, False]}],
    ),
    dict(
        label="Other",
        method="update",
        args=[{"visible": [False, False, False, True, False]}],
    ),
    dict(
        label="Total Bookings",
        method="update",
        args=[{"visible": [False, False, False, False,True]}],
    )
]

fig.update_layout(
    title=f'Occupancy Analysis Segment 2: Report Date Range: {min_report_date} - {max_report_date.date()}',
    title_x=0.15,
    updatemenus=[{
        'type': 'buttons',
        'direction': 'right',
        'x': 0.65,
        'y': 1.15,
        'showactive': True,
        'active': 0,
        'buttons': buttons
    }
    ]
)
fig.update_xaxes(title_text="Stay Date")
fig.update_yaxes(title_text="Report Date")

st.write("Occupancy Analysis on Segment 2: Direct vs Indirect vs OTA vs Others ")
# Show figure
st.plotly_chart(fig)




traces = []
for group in groups:
    trace = go.Heatmap(
        z=plot_data_group_dfs[group],
        x=plot_data_group_dfs[group].columns,
        y=plot_data_group_dfs[group].index,
        colorscale=custom_colorscale,
        zmin=zmin,
        zmax=zmax,
        name=group,
        colorbar=dict(title='Bookings'),
        visible=False
    )
    traces.append(trace)
trace_total.name = "total"
traces.append(trace_total)
fig = go.Figure(data=traces)
buttons = []
for group in groups:
    button = dict(
        label=f'{group}',
        method="update",
        args=[{"visible": [group == trace.name for trace in traces]}, {"title": f"{group} Bookings)"}],
    )
    buttons.append(button)
button_total = dict(
    label='Total Bookings',
    method="update",
    args=[{"visible": ['total' == trace.name for trace in traces]}, {"title": "Total Revenue" }],
)
buttons.append(button_total)


fig.update_layout(
    title=f'Occupancy Analysis on Segment 3: Group Codes',
    title_x=0.15,
    updatemenus=[{
        'type': 'dropdown',
        'x': 0.85,
        'y': 1.1,
        'buttons': buttons
    },
    ]
)
fig.update_xaxes(title_text="Stay Date")
fig.update_yaxes(title_text="Report Date")

st.write("Occupancy Analysis on Segment 3: Group Codes ")
# Show figure
st.plotly_chart(fig)
