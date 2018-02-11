import datetime
import colorlover as cl
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.graph_objs import *

import helpers.data_downloader as dd
import helpers.data_scraper as ds
from data.meta_data import network_layouts, layouts, kawai, network_types
from data.meta_data import tickers
from models.financial_model import FinancialModel

app = dash.Dash()
app.title = "Agent-Based Modeling"
interval_t = 1 * 500
initiated = False
app.layout = html.Div([
    html.P(
        hidden='',
        id='raw_container',
        style={'display': 'none'}
    ),
    dcc.Interval(id='interval-component', interval=interval_t, n_intervals=0),
    html.Div([
        html.Div([
            dcc.Checklist(
                id='stock-ticker-input',
                options=[{'label': i, 'value': j} for i, j in tickers.items()],
                values=[j for i, j in tickers.items()])
        ], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='network-type-input',
                options=[{'label': i, 'value': i} for i in network_types],
                value='Barabasi',
                multi=False
            )
        ], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([
            dcc.RadioItems(
                id='network-layout-input',
                options=[{'label': k, 'value': k} for k in layouts],
                value=kawai,
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '33%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
    html.Div([
        html.Div([
            dcc.Graph(id='live-update-graph')
        ], style={'width': '25%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='live-update-graph-network')
        ], style={'width': '25%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='live-update-graph-scatter')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    html.Hr()
])


# Cache raw data
@app.callback(Output('raw_container', 'hidden'),
              [Input('stock-ticker-input', 'values'),
               Input('network-type-input', 'value')])
def cache_raw_data(tickers, network_type):
    global model, data2, end, colors_c, stocks, initiated
    model, data2, end, colors_c, stocks = initialize(tickers, network_type)
    print('Loaded raw data')
    initiated = True
    return 'loaded'


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph-scatter', 'figure'),
              [Input('raw_container', 'hidden'),
               Input('interval-component', 'n_intervals')])
def update_graph_live(hidden, i):
    graphs = []
    layout = []
    if initiated:
        all_agents = model.all_agents.sort_index(axis=1)
        graphs = []
        ic = 0
        for fx in data2.index:
            graphs.append(go.Scatter(
                x=all_agents.index,
                y=all_agents[fx],
                mode='lines',
                name=fx,
                marker=dict(
                    color=colors_c[ic],
                    line=dict(
                        width=2,
                        color=colors_c[ic]
                    ))
            ))
            ic += 1
        layout = dict(xaxis=dict(title='Date'), yaxis=dict(title='Cash in Hand'), )
    fig = dict(data=graphs, layout=layout)
    return fig


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('raw_container', 'hidden')])
def update_graph_live(n, hidden):
    fig = []
    if initiated:
        banks = model.schedule.agents
        banks = sorted(banks, key=lambda bank: bank.ticker, reverse=False)
        labels = [x.ticker for x in banks]
        values = [x.cash_A for x in banks]
        layout = dict(xaxis=dict(title='Date'),
                      yaxis=dict(title='Cash in Hand'),
                      showlegend=False)

        trace = go.Pie(labels=labels, values=values, hole=.25, pull=.005, sort=False, textinfo='percent+label',
                       marker=dict(colors=colors_c))

        fig = dict(data=[trace], layout=layout)

    return fig


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph-network', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('raw_container', 'hidden'),
               Input('network-layout-input', 'value')])
def update_graph_live(n, hidden, network_layout):
    fig = Figure()
    if initiated:
        model.step()
        model_graph = model.graph
        banks = list(nx.get_node_attributes(model_graph, 'bank').values())
        equities = [x.equity for x in banks]
        equities = equities / sum(equities)
        mx_eq = max(equities)
        equities = equities * 50 / mx_eq + 25
        pos = network_layouts[network_layout](model_graph)
        node_colors = []
        for x in banks:
            if x.state == 'Infected':
                node_colors.append('rgb(244, 194, 66)')
            elif x.state == 'Dead':
                node_colors.append('rgb(237, 14, 14)')
            else:
                node_colors.append('rgb(14, 209, 53)')
        edge_trace = Scatter(x=[], y=[], line=Line(width=2.5, color='#888'), hoverinfo='none', mode='lines')
        node_trace = Scatter(x=[], y=[], text=stocks, mode='markers+text+value', hoverinfo='text', marker=Marker(
            color=node_colors,
            size=equities,
            line=dict(width=2)))

        for st in stocks:
            x0, y0 = pos[st]
            node_trace['x'].append(x0)
            node_trace['y'].append(y0)
            neighbors = list(model_graph.edges._adjdict[st].keys())
            for nei in neighbors:
                x1, y1 = pos[nei]
                edge_trace['x'] += [x0, x1, None]
                edge_trace['y'] += [y0, y1, None]

        fig = Figure(data=Data([edge_trace, node_trace]),
                     layout=Layout(
                         titlefont=dict(size=16),
                         showlegend=False,
                         title='Residual shock: {};.<br> Dead: {} <br> Bad Debt: {}'
                             .format(model.shock, model.dead, model.total_bad_debt()),
                         hovermode='closest',
                         margin=dict(b=20, l=5, r=5, t=40),
                         xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                         yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))
    return fig


def initialize(stocks, network_type):
    dt = 1 / 252.0
    end = datetime.date.today()
    stocks.sort(reverse=False)
    set_c = 'Set3' if len(stocks) > 9 else 'Set1'
    colors_c = cl.scales[str(len(stocks))]['qual'][set_c]
    start = datetime.datetime(2016, 1, 1)
    data2 = ds.scrape_balance_sheet_data(qt=2, stock_list=stocks)
    stock_data = dd.download_data(start, end, stocks)
    model = FinancialModel(data2, stock_data, dt=dt, network_type=network_type)
    return model, data2, end, colors_c, stocks


if __name__ == '__main__':
    app.run_server(debug=True, port=3434)
