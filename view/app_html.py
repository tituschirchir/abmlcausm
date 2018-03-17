import dash_core_components as dcc
import dash_html_components as html

import network.core.skeleton as ns


def get_layout(interval_t, layouts):
    return html.Div([initial_params(interval_t), get_side_bar(layouts), get_main_body()])


def get_nick_layout(interval_t):
    return html.Div([initial_params(interval_t), get_nick_main_body()])


def initial_params(interval_t):
    return html.Div([
        html.Link(href='/assets/codePen.css', rel='stylesheet'),
        html.Link(href='/assets/app.css', rel='stylesheet'),
        html.P(hidden='', id='raw_container', style={'display': 'none'}),
        dcc.Interval(id='interval-component', interval=interval_t, n_intervals=0)
    ])


def get_main_body():
    return html.Div([
        html.Div([dcc.Graph(id='live-update-graph-network')], className="six columns"),
        html.Div([dcc.Graph(id='show-bank-status')], className="six columns"),
        html.Div([dcc.Graph(id='funnel-graph')], className="six columns"),
        html.Div([dcc.Graph(id='bs-display')], className="twelve columns")
    ], className="main")


def get_nick_main_body():
    return html.Div([
        html.Label(html.Strong('No. of Nodes', title="Number of nodes")),
        dcc.Input(id="nofagents", value=100, type='number', step=100, min=100, max=5000),
        html.Div([dcc.Graph(id='stock_exchange')], className="six columns")
    ], className="_main")


def get_side_bar(layouts):
    return html.Div([
        html.H2("Bank Network"),
        html.Label(html.Strong('No. of Nodes', title="Number of nodes")),
        dcc.Input(id="nofbanks", value=25, type='number', step=1, min=1, max=25),
        html.Label(html.Strong('Style')),
        dcc.RadioItems(
            id='order-style',
            options=[{'label': i, 'value': i} for i in ['Random', 'Size']],
            value='Random'
        ),
        html.Label(html.Strong('Probability'), title="Probability for edge creation"),
        dcc.Input(id="prob", value=0.5, type='number', step=0.05, min=0, max=1),
        html.Label(html.Strong('M'), title='Number of edges to attach from a new node to existing nodes'),
        dcc.Input(id="m_val", value=3, type='number', step=1, min=0, max=25),
        html.Label(html.Strong('K-Nearest Neighbor'),
                   title='Each node is joined with its k-nearest neighbors in a ring topology.'),
        dcc.Input(id="k_val", value=4, type='number', step=1, min=0, max=25),
        html.Label(html.Strong('Network')),
        dcc.RadioItems(
            id='network-type-input',
            options=[{'label': i, 'value': i} for i in ns.all_nets],
            value=ns.barabasi_albert_graph
        ),
        html.Label(html.Strong('Layout')),
        dcc.RadioItems(
            id='network-layout-input',
            options=[{'label': k, 'value': k} for k in layouts],
            value="kamada_kawai_layout"
        ),
        html.Div([
            html.Label(html.Strong('Quarter', title="__ quarters ago")),
            dcc.Input(id="quarters", value=2, type='number', min=1, max=5),
            html.Button('Download BS', id='button', n_clicks=0),
            html.Div(id='data-downloader'),
            dcc.Input(style={'display': 'none'})
        ])
    ], className="side-bar")
