from action import Action
from cellCodes import CellCodes
from document import Document
from agentView import AgentView
from agent import Agent
from config import Config

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

        # TODO make it a class not a tuple
        actionList: list[tuple[Agent, Action, AgentView]] = []
        for agent in doc.agents:
            agentView = AgentView(doc, agent.x, agent.y)
            actions: list[Action] = agent.selectActions(agentView)
            sharedAct = Model.J(actions, agent, agentView, doc)
            actionList.append((agent, sharedAct, agentView))

        doc.applyActionList(actionList)

        scoreAfter = Model.getScore(doc)
        reward = scoreAfter - scoreBefore
        print("reward: ", reward, " score: ", scoreAfter)

        for agent in doc.agents:
            agent.L(actionList, reward)

        for agent in doc.agents:
            agent.Q(actionList, reward)


    @staticmethod
    def J(actions: list[Action], thisAgent: Agent, agentView: AgentView, doc: Document) -> Action:
        if len(actions) == 0:
            return None
        bids: list[list[float]] = []
        for actId, action in enumerate(actions):
            bids.append([])
            for agent in doc.agents:
                if thisAgent.distanceTo(agent) <= Config.agent_coms_distance:
                    agentBid = agent.bid(action, agentView)
                    bids[actId].append(agentBid)
            bids[actId].sort(reverse=True)

        bestActID = 0
        bestActBid = bids[0][0]
        for id, bid in enumerate(bids):
            if bid[0] > bestActBid:
                bestActID = id
                bestActBid = bid[0]

        return actions[bestActID]
