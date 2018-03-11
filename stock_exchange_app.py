import dash
import plotly.graph_objs as go
from dash.dependencies import Output, Input

from abm_market.model import MarketModel
from view.app_html import get_nick_layout

app = dash.Dash(__name__, static_folder='assets')
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.title = "Stock Exchange"
interval_t = 1 * 1000

app.layout = get_nick_layout(interval_t)


# Cache raw data
@app.callback(Output('raw_container', 'hidden'), [Input('nofagents', 'value')])
def initialize_model(n_agents=100):
    global model
    model = MarketModel(n_agents)
    print('Model Initialized')
    return 'loaded'


@app.callback(Output('stock_exchange', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph_live(i):
    model.step()
    layout = dict(xaxis=dict(title='Step'), yaxis=dict(title='Price'), height=500)
    return dict(data=[go.Scatter(
        x=list(model.stock.price_hist.keys()),
        y=list(model.stock.price_hist.values()),
        name="Stock Price",
        mode='dots',
        marker=dict(color="green", line=dict(width=2, color="blue"))
    )], layout=layout)


if __name__ == '__main__':
    initialize_model()
    app.run_server(debug=True, port=5050)
