import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

from helpers.agent_fisher import get_agents

df = pd.read_excel(
    "https://github.com/chris1610/pbpython/blob/master/data/salesfunnel.xlsx?raw=True"
)
mgr_options = df["Manager"].unique()

app = dash.Dash()

app.layout = html.Div([
    html.H2("Sales Funnel Report"),
    html.Div(
        [
            dcc.Dropdown(
                id="Manager",
                options=[{
                    'label': i,
                    'value': i
                } for i in mgr_options],
                value='All Managers'),
        ],
        style={'width': '25%', 'display': 'inline-block'}),
    dcc.Graph(id='funnel-graph'),
])


@app.callback(
    dash.dependencies.Output('funnel-graph', 'figure'))
def update_graph():
    agents = get_agents(-1)
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
    app.run_server(debug=True)
