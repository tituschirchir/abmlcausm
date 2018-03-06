import datetime
import random

import colorlover as cl
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.graph_objs import *

import network.core.skeleton as ns
from helpers.agent_fisher import get_agents
from network.fin.fin_model import FinNetwork

layouts = ['fruchterman_reingold_layout', 'kamada_kawai_layout', 'circular_layout', 'spring_layout']
app = dash.Dash()
app.title = "Agent-Based Modeling"
interval_t = 1 * 1000
app.css.append_css({"external_url": "./mycss.css"})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
app.layout = html.Div([
    html.P(
        hidden='',
        id='raw_container',
        style={'display': 'none'}
    ),
    html.Div([
        html.Div([
            html.Div([
                html.Label('Number of Banks'),
                dcc.Input(id="nofbanks", value='10', type='text'),
                html.Label('Probability'),
                dcc.Input(id="prob", value='0.5', type='text'),
                html.Label('M'),
                dcc.Input(id="m_val", value='3', type='text'),
                html.Label('K'),
                dcc.Input(id="k_val", value='4', type='text'),
                dcc.Interval(id='interval-component', interval=interval_t, n_intervals=0)
            ], className='col'),
            html.Div([
                dcc.Dropdown(
                    id='network-type-input',
                    options=[{'label': i, 'value': i} for i in ns.all_nets],
                    value=ns.barabasi_albert_graph,
                    multi=False
                )
            ], className='col'),
            html.Div([
                dcc.RadioItems(
                    id='network-layout-input',
                    options=[{'label': k, 'value': k} for k in layouts],
                    value="kamada_kawai_layout"
                )
            ], className='col')
        ], className='col'),
        html.Div([

            html.Div([
                html.Div([dcc.Graph(id='live-update-graph-network')],
                         style={'width': '50%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(id='funnel-graph')], style={'width': '50%', 'display': 'inline-block'})
            ], style={'width': '80%', 'display': 'inline-block'})
        ], className='col')
    ], className='row')
])


def build_graph(model_):
    import networkx as nx
    model_graph = nx.Graph()
    for node in model_.schedule.agents:
        model_graph.add_node(node)
        for edge in node.edges:
            model_graph.add_edge(edge.node_from, edge.node_to)
    return model_graph


# Cache raw data
@app.callback(Output('raw_container', 'hidden'),
              [Input('network-type-input', 'value'),
               Input('nofbanks', 'value'),
               Input('prob', 'value'),
               Input('m_val', 'value'),
               Input('k_val', 'value')])
def cache_raw_data(net_type, N=10, p=0.5, m=2, k=3):
    global model, data2, end, colors_c, stocks, initiated, agents
    agents = get_agents(int(N))
    model = FinNetwork("Net 1", agents, net_type=net_type, p=float(p), m=int(m), k=int(k))
    stocks = [x.name for x in agents]
    colors_ = (cl.to_rgb(cl.interp(cl.scales['6']['qual']['Set1'], len(stocks) * 20)))
    colors_c = np.asarray(colors_)[np.arange(0, len(stocks) * 20, 20)]
    end = datetime.date.today()
    print('Loaded raw data')
    return 'loaded'


@app.callback(Output('live-update-graph-network', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('network-layout-input', 'value')])
def update_graph_live(n, net_layout):
    if random.random() > 0.9:
        model.apply_shock(random.randint(0, 1))
    model.step()
    banks = model.schedule.agents
    model_graph = build_graph(model)
    txt = [x.name for x in banks]
    equities = [x.capital for x in banks]
    equities = np.asarray(equities) / sum(equities)
    mx_eq = max(equities)
    equities = equities * 50 / mx_eq + 20

    pos = getattr(nx, net_layout)(model_graph)
    orange, red, green = 'rgb(244, 194, 66)', 'rgb(237, 14, 14)', 'rgb(14, 209, 53)'
    node_colors = [(red if x.defaults else (orange if x.affected else green)) for x in banks]
    edge_trace = Scatter(x=[], y=[], line=Line(width=2.5, color='#888'), hoverinfo='none', mode='lines')
    node_trace = Scatter(x=[], y=[], text=txt, mode='markers+text+value', hoverinfo='text', marker=Marker(
        color=node_colors,
        size=equities,
        line=dict(width=2)))

    for st in banks:
        x0, y0 = pos[st]
        node_trace['x'].append(x0)
        node_trace['y'].append(y0)
        neighbors = list(model_graph.edges._adjdict[st].keys())
        for nei in neighbors:
            x1, y1 = pos[nei]
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]

    return Figure(data=Data([edge_trace, node_trace]),
                  layout=Layout(
                      titlefont=dict(size=16),
                      showlegend=False,
                      title='Teta ak moita',
                      hovermode='closest',
                      margin=dict(b=20, l=5, r=5, t=40),
                      xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))


@app.callback(
    dash.dependencies.Output('funnel-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_graph(n):
    x = [x.name for x in agents]
    trace1 = go.Bar(x=x, y=[x.interbankAssets * 1000000 for x in agents], name='Loan Assets')
    trace2 = go.Bar(x=x, y=[x.externalAssets * 1000000 for x in agents], name='External Assets')
    trace3 = go.Bar(x=x, y=[x.customer_deposits * 1000000 for x in agents], name='Deposits')
    trace4 = go.Bar(x=x, y=[x.interbank_borrowing * 1000000 for x in agents], name='Loan Liabilities')
    trace5 = go.Bar(x=x, y=[x.capital * 1000000 for x in agents], name='Capital')

    return {
        'data': [trace1, trace2, trace3, trace4, trace5],
        'layout': go.Layout(title='Balance Sheets for the banks', barmode='stack')
    }


if __name__ == '__main__':
    cache_raw_data(ns.barabasi_albert_graph)
    app.run_server(debug=True, port=3434)
