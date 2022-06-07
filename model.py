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
    def getScore(doc: Document) -> int:
        def taxiDist(x1, y1, x2, y2):
            return abs(x1-x2) + abs(y1-y2)
        score = 0
        docSizeSum = doc.size[0]+doc.size[1]
        for x in range(doc.size[0]):
            for y in range(doc.size[1]):
                # scan for chairs
                if doc.getCellCode(x, y) == CellCodes.Chair:
                    closestTableDist = 100000000
                    for _x in range(0, doc.size[0]):
                        for _y in range(0, doc.size[1]):
                            if doc.getCellCode(_x, _y) in [CellCodes.Table_min, CellCodes.Table_max]:
                                closestTableDist = min(closestTableDist, taxiDist(x, y, _x, _y))
                    # closestTableDist = taxi distance to closest table, smaller -> bigger reward but always in [0,1]

                    isNextToTable = False
                    for (_x, _y) in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
                        # check if chair is next to a table
                        if doc.getCellCode(_x, _y) in [CellCodes.Table_min, CellCodes.Table_max]:
                            isNextToTable = True
                            break
                    if isNextToTable:
                        score += 1
                    else:
                        if len(doc.getCell(x, y).grabbed_by) > 0:
                            closestTableDist -= 0.5  # bonus for holding chair which is not directly next to table
                    distScore = (docSizeSum - closestTableDist) / docSizeSum  # normalize to [0,1]
                    assert 0 <= distScore <= 1
                    score += distScore
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
        print("reward: ", f'{reward:.2f}', " score: ", f'{scoreAfter:.2f}', " step time: ", f'{(timeEnd - timeStart):.2f}', " step nr ", doc.step)

    @staticmethod
    def randomStep(doc: Document) -> None:
        scoreBefore = Model.getScore(doc)
        timeStart = time.time()
        perfActionList: list[PerformedAction] = []
        for agent in doc.agents:
            agentView = AgentView(doc, agent.x, agent.y)
            sharedAct = Action.makeRandom()
            assert (sharedAct is not None)
            perfActionList.append(PerformedAction(agent, sharedAct, agentView))

        doc.applyActionList(perfActionList)

        scoreAfter = Model.getScore(doc)
        reward = scoreAfter - scoreBefore

        for perfAct in perfActionList:
            perfAct.reward = reward

        timeEnd = time.time()
        print("Random Step reward: ", f'{reward:.2f}', " score: ", f'{scoreAfter:.2f}', " step time: ", f'{(timeEnd - timeStart):.2f}', " step nr ",
              doc.step)

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
