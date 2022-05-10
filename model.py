from action import Action
from document import Document
from agentView import AgentView


class Model:
    def __init__(self) -> None:
        pass

    def step(self, doc: Document) -> None:
        for agent in doc.agents:
            action = Action.makeRandom()
            agentView = AgentView(doc, agent.x, agent.y)
            # print(agentView.ToPrettyString())
            applied = doc.applyActionToAgent(agent, action)
            print("action type: ", action.type, " success: ", applied)
