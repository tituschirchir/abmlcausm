from networkx.drawing import layout

tickers = {"Goldman Sachs": 'GS',
           "Bank of America": 'BAC',
           'Morgan Stanley': 'MS',
           'JP Morgan': 'JPM',
           "Wells Fargo": "WFC",
           'Citigroup': 'C',
           'U.S. Bancorp': "USB",
           'Apple Inc': "AAPL",
           'Advanced Microdevices': "AMD",
           'Amazon': "AMZN",
           'American Investment Group': "AIG",
           'Johnson and Johnson': "JNJ",
           'PNC Financial Services Group Inc': 'PNC'}

kawai = "Kamada Kawai"
layouts = ['Circular', kawai, 'Random', 'Rescale', "Shell", "Spring", "Spectral", "Fruchterman Reingold"]
network_types = ['Erdos', 'Barabasi']
network_layouts = {layouts[0]: layout.circular_layout,
                   kawai: layout.kamada_kawai_layout,
                   layouts[2]: layout.random_layout,
                   layouts[3]: layout.rescale_layout,
                   layouts[4]: layout.shell_layout,
                   layouts[5]: layout.spring_layout,
                   layouts[6]: layout.spectral_layout,
                   layouts[7]: layout.fruchterman_reingold_layout}
