from action import Action
from cellCodes import CellCodes
from document import Document
from agentView import AgentView
from agent import Agent
from config import Config
from performedAction import PerformedAction
import time


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
        timeStart = time.time()
        perfActionList: list[PerformedAction] = []
        for agent in doc.agents:
            agentView = AgentView(doc, agent.x, agent.y)
            actions: list[Action] = agent.selectActions(agentView)
            assert(len(actions) > 0)
            sharedAct = Model.J(actions, agent, agentView, doc)
            assert(sharedAct is not None)
            perfActionList.append(PerformedAction(agent, sharedAct, agentView))

        doc.applyActionList(perfActionList)

        scoreAfter = Model.getScore(doc)
        reward = scoreAfter - scoreBefore

        for perfAct in perfActionList:
            perfAct.reward = reward

        for perfAct in perfActionList:
            perfAct.agent.addToMemory(perfAct.action, perfAct.agentView, perfAct.success, perfAct.reward)

        for agent in doc.agents:
            agent.L(perfActionList, reward)

        afterAgentViews = []
        for agent in doc.agents:
            afterAgentViews.append(AgentView(doc, agent.x, agent.y))
        for agent in doc.agents:
            agent.Q(perfActionList, afterAgentViews, reward)

        timeEnd = time.time()
        print("reward: ", reward, " score: ", scoreAfter, " step time: ", f'{(timeEnd - timeStart):.2f}', " step nr ", doc.step)

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
