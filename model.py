from document import Document


class Model:

    def __init__(self) -> None:
        pass

    def Step(self, doc : Document) -> None:
        for agent in doc.agents:
            doc.ApplyActionToAgent(agent, None)
