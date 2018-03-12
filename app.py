import datetime
from copy import deepcopy

import colorlover as cl
import dash
import networkx as nx
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.graph_objs import *

import network.core.skeleton as ns
from helpers.agent_fisher import get_agents
from helpers.data_downloader import download_balance_sheet
from network.fin.fin_model import FinNetwork
from view.app_html import get_layout

n_clicks_2 = 0
default_tick = 'JPM,BRK.b,BAC,WFC,C,GS,USB,MS,PNC,AXP,BLK,CB,SCHW,BK,CME,AIG,MET,SPGI,COF,PRU,BBT,ICE,MMC,STT,TRV,AON,' \
               'AFL,PGR,STI,ALL,MTB,DFS,MCO,TROW,SYF,FITB,KEY,AMP,NTRS,RF,CFG,WLTW,HIG,CMA,HBAN,LNC,PFG,ETFC,XL,L,IVZ,' \
               'CBOE,BEN,AJG,RJF,CINF,UNM,ZION,AMG,RE,NDAQ,TMK,LUK,PBCT,BHF,AIZ,NAVI'
margin = dict(b=40, l=40, r=0, t=10)
layouts = ['fruchterman_reingold_layout', 'kamada_kawai_layout', 'circular_layout', 'spring_layout']
app = dash.Dash(__name__, static_folder='assets')
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.title = "Agent-Based Modeling"
interval_t = 1 * 1000
fresh_agents = get_agents(100)
app.layout = get_layout(interval_t, layouts)


def build_graph(model_):
    import networkx as nx
    model_graph = nx.Graph()
    for node in model_.schedule.agents:
        model_graph.add_node(node)
        for edge in node.edges:
            model_graph.add_edge(edge.node_from, edge.node_to)
    return model_graph


@app.callback(Output('data-downloader', 'children'),
              [Input('button', 'n_clicks'), Input('quarters', 'value')])
def download_data(n_clicks, quarters):
    tickers = default_tick.replace(' ', '').split(',')
    global n_clicks_2
    if n_clicks_2 == n_clicks:
        return
    n_clicks_2 = n_clicks
    download_balance_sheet(tickers=tickers, f_loc='data/bs_ms.csv', prev_quarter=quarters)


# Cache raw data
@app.callback(Output('raw_container', 'hidden'),
              [Input('network-type-input', 'value'), Input('nofbanks', 'value'), Input('prob', 'value'),
               Input('m_val', 'value'), Input('k_val', 'value')])
def cache_raw_data(net_type, N=29, p=0.5, m=3, k=3):
    global model, data2, end, colors_c, stocks, initiated, agents
    if m >= N:
        N = m + 1
    agents = fresh_agents if N >= len(fresh_agents) else fresh_agents[0:N]
    agents = [deepcopy(x) for x in agents]
    model = FinNetwork("Net 1", agents, net_type=net_type, p=p, m=m, k=k)
    stocks = [x.name for x in agents]
    colors_ = (cl.to_rgb(cl.interp(cl.scales['6']['qual']['Set1'], len(stocks) * 20)))
    colors_c = np.asarray(colors_)[np.arange(0, len(stocks) * 20, 20)]
    end = datetime.date.today()
    print('Loaded raw data')
    return 'loaded'


interval_element = Input('interval-component', 'n_intervals')


@app.callback(Output('live-update-graph-network', 'figure'), [interval_element, Input('network-layout-input', 'value')])
def update_graph_live(n, net_layout):
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
                      hovermode='closest',
                      margin=margin,
                      height=600,
                      xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))


@app.callback(Output('funnel-graph', 'figure'), [interval_element])
def update_graph(n):
    x = [x.name for x in agents]
    trace1 = go.Bar(x=x, y=[x.interbankAssets * 1000000 for x in agents], name='Loan Assets')
    trace2 = go.Bar(x=x, y=[x.externalAssets * 1000000 for x in agents], name='External Assets')
    trace3 = go.Bar(x=x, y=[x.customer_deposits * 1000000 for x in agents], name='Deposits')
    trace4 = go.Bar(x=x, y=[x.interbank_borrowing * 1000000 for x in agents], name='Loan Liabilities')
    trace5 = go.Bar(x=x, y=[x.capital * 1000000 for x in agents], name='Capital')

    return {
        'data': [trace1, trace2, trace3, trace4, trace5],
        'layout': go.Layout(barmode='stack', height=250, margin=margin)
    }


@app.callback(Output('show-bank-status', 'figure'), [interval_element])
def update_graph_live(i):
    graphs = []
    ic = 0
    for x in agents:
        graphs.append(go.Scatter(
            x=np.arange(len(x.price_history)),
            y=x.price_history,
            name=x.name,
            mode='dots',
            marker=dict(
                color=colors_c[ic],
                line=dict(
                    width=2,
                    color=colors_c[ic]
                ))
        ))
        ic += 1
    layout = dict(xaxis=dict(title='Step'), yaxis=dict(title='Relative Value'), margin=margin, height=300)
    return dict(data=graphs, layout=layout)


if __name__ == '__main__':
    cache_raw_data(ns.barabasi_albert_graph)
    app.run_server(debug=True, port=3434)
