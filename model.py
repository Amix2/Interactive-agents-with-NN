from action import Action
from document import Document
from agentView import AgentView

class Model:

    def __init__(self) -> None:
        pass

    def Step(self, doc : Document) -> None:
        for agent in doc.agents:
            action = Action.MakeRandom()
            agentView = AgentView(doc, agent.x, agent.y)
            doc.ApplyActionToAgent(agent, action)
