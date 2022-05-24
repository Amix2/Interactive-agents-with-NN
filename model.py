from action import Action
from cellCodes import CellCodes
from document import Document
from agentView import AgentView


class Model:
    def __init__(self) -> None:
        pass

    @staticmethod
    def getScore(doc: Document) -> float:
        score = 0
        for x in range(doc.size[0]):
            for y in range(doc.size[1]):
                # scan for chairs
                if doc.getCellCode(x, y) == CellCodes.Chair:
                    for (_x, _y) in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
                        # check if chair is next to a table
                        if doc.getCellCode(_x, _y) in [CellCodes.Table_min, CellCodes.Table_max]:
                            score += 1
                            break
        return score

    @staticmethod
    def step(doc: Document) -> None:
        scoreBefore = Model.getScore(doc)

        for agent in doc.agents:
            agentView = AgentView(doc, agent.x, agent.y)
            action = agent.selectAction(agentView)
            applied = doc.applyActionToAgent(agent, action)
            print("action type: ", action.type, " success: ", applied)
            agent.addToMemory(action, applied)

        scoreAfter = Model.getScore(doc)
        reward = scoreAfter - scoreBefore
        print("reward: ", reward)

        for agent in doc.agents:
            agent.L(reward)

