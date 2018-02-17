from network.components import Agent


class FED(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
