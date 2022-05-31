import math
import random
from typing import Union

from action import Action
from agentView import AgentView
from cellCodes import CellCodes
from simObj import ISimObj
from config import Config
import time
import  numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense
from performedAction import PerformedAction
import tensorflow as tf


class PastAction:
    def __init__(self, action: Action, agentView: AgentView, success: bool = None, reward: float = None):
        self.action = action
        self.agentView = agentView
        self.success = success
        self.reward = reward


class Agent(ISimObj):
    def __init__(self, x: int, y: int, actionMemorySize: int = 5) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.grab: str = None
        self.grabbedCode: str = None
        self.grabbedObj: ISimObj = None

        self.grab: Union[str, None] = None
        self._actionMemorySize = actionMemorySize
        self.actionMemory: list[Union[PastAction, None]] = [None]*self._actionMemorySize
        self.deltaModel = Agent.createDeltaNN()
        self.QModel = Agent.createQNN()

    def getCode(self, x: int, y: int) -> int:
        assert(x == self.x and y == self.y)
        if self.grab:
            if self.grab == Action.north:
                return CellCodes.Agent_grabbedN
            if self.grab == Action.south:
                return CellCodes.Agent_grabbedS
            if self.grab == Action.east:
                return CellCodes.Agent_grabbedE
            if self.grab == Action.west:
                return CellCodes.Agent_grabbedW
        return CellCodes.Agent_standing

    def getPositions(self) -> list[tuple[int, int]]:
        """Returns list of all the occupied positions"""
        return [(self.x, self.y)]

    def canPerformActionType(self, action: Action) -> bool:
        """Returns true if object is capable of performing given action in their correct state ignoring surroundings """
        if action.type == Action.wait:
            return True
        elif action.type == Action.release:
            return self.grab is not None
        elif action.type == Action.grab:
            return self.grab is None
        elif action.type == Action.move:
            return True
        raise NotImplementedError

    def selectActions(self, agentView: AgentView) -> list[Action]:
        actions = Action.getAll()
        deltaPredictions = self.calculateDelta(agentView)
        preferredActions = []
        limit = np.max(deltaPredictions) - Config.agent_select_action_window
        for i, deltaVal in enumerate(deltaPredictions[0]):
            if deltaVal >= limit:
                preferredActions.append(actions[i])
        assert len(preferredActions) > 0
        return preferredActions

    def addToMemory(self, action: Action, agentView: AgentView, succeeded: bool, reward: float) -> None:
        assert(action is not None)
        assert(succeeded is not None)
        assert(reward is not None)
        self.actionMemory.pop(0)
        self.actionMemory.append(PastAction(action, agentView, succeeded, reward))

    def getLastAction(self):
        return self.actionMemory[self._actionMemorySize-1]

    def getActionMemory(self):
        return [a for a in self.actionMemory if a is not None]

    def bid(self, action: Action, agentView: AgentView) -> float:
        return self.calculateQ((agentView, action))[0]

    def L(self, performedActionList: list[PerformedAction], reward: float) -> None:
        # Options for teaching:
        # 1. Based on this step's action for this agent
        # 2. Based on this step's action for all the agents (in range) (this agent's Q models)
        # 3. Based on history actions for this agent
        # 4. Based on history actions for all the agents (in range) (this agent's Q models)

        def FitForPastActions(pastActions: list[PastAction]):
            # lets assume performedActionList contains following actions (in order) a2, a2, a3 and views v1, v2, v3
            # trainBatchX ] [v1, v2, v3...]
            # trainBatchY will be:
            # [ [d(v1)[a1], d(v1)[a2] + a(r-Q(v1,a2)), d(v1)[a3]...],   // fixing value for a2
            #   [d(v2)[a1], d(v2)[a2] + a(r-Q(v2,a2)), d(v2)[a3]...],   // fixing value for a2
            #   [d(v3)[a1], d(v3)[a2], d(v3)[a3] + a(r-Q(v3,a3))...]]   // fixing value for a3
            viewsActions: list[tuple[AgentView, Action]] = []
            views: list[AgentView] = []
            for pastAct in pastActions:
                viewsActions.append((pastAct.agentView, pastAct.action))
                views.append(pastAct.agentView)
            Qvalues = self.calculateQ(viewsActions)
            deltaValues = self.calculateDelta(views)
            trainBatchX = []
            trainBatchY = []
            for i, pastAct in enumerate(pastActions):
                trainBatchX.append(np.array(pastAct.agentView.toList()))
                Y = deltaValues[i]

                actID = Action.getAll().index(pastAct.action)
                Y[actID] = Y[actID] + Config.q_learn_a * (pastAct.reward - Qvalues[i][0])
                trainBatchY.append(np.array(Y))

            self.deltaModel.fit(np.array(trainBatchX), np.array(trainBatchY), verbose=0)

        option = 4
        if option == 2:
            pastActions: list[PastAction] = []
            for perfAct in performedActionList:
                if self.distanceTo(perfAct.agent) < Config.agent_coms_distance:
                    pastActions.append(PastAction(perfAct.action, perfAct.agentView, perfAct.success, reward))
            FitForPastActions(pastActions)
        elif option == 4:
            pastActions: list[PastAction] = []
            for perfAct in performedActionList:
                if self.distanceTo(perfAct.agent) < Config.agent_coms_distance:
                    for agentsPastAct in perfAct.agent.getActionMemory():
                        pastActions.append(
                            PastAction(agentsPastAct.action, agentsPastAct.agentView, agentsPastAct.success, reward))
            FitForPastActions(pastActions)
        else:
            raise NotImplementedError

    def Q(self, performedActionList: list[PerformedAction], newVisions: list[AgentView], reward: float) -> None:
        # Options for teaching:
        # 1. Based on this step's action for this agent
        # 2. Based on this step's action for all the agents (in range) (this agent's Q models)
        # 3. Based on history actions for this agent
        # 4. Based on history actions for all the agents (in range) (this agent's Q models)

        def FitForPastActions(pastActions: list[tuple[PastAction, AgentView]]):
            """pastActions tuple contains action and view from after action was performed"""
            # lets assume performedActionList contains following actions (in order) a2, a2, a3 and views v1, v2, v3
            # after changes were made we have new agentViews called nv1, nv2, nv3...
            # trainBatchX ] [v1a1, v2a2, v3a3...]
            # trainBatchY will be:
            # [ [Q(v1,a1) + a(r + y*MAX^all possible actions^(Q(nv1, a)) - Q(v1, a1)],          // fixing value for a1v1
            #   [Q(v2,a2) + a(r + y*MAX^all possible actions^(Q(nv2, a)) - Q(v2, a2)],...]      // fixing value for a2v2
            evalQ: list[tuple[AgentView, Action]] = []  # list of all requests to predict with Q model
            allActions = Action.getAll()
            for pastAct, nextView in pastActions:
                evalQ.append((pastAct.agentView, pastAct.action))  # for Q(v1,a1)
                for allAct in allActions:
                    evalQ.append((nextView, allAct))  # for Q(v1,a1)

            valuesQ = [d[0] for d in self.calculateQ(evalQ)]
            trainBatchX = []
            trainBatchY = []
            for pastAct, nextView in pastActions:
                X = pastAct.agentView.toList()
                X.append(pastAct.action.getCode())
                trainBatchX.append(np.array(X))

                qValId = evalQ.index((pastAct.agentView, pastAct.action))
                qValBase = valuesQ[qValId]
                assert not math.isnan(qValBase)

                nextViewActions = [valuesQ[ evalQ.index((nextView, a)) ] for a in allActions]
                maxAllActions = max(nextViewActions)  # MAX^all possible actions^(Q(nv, a))
                assert not math.isnan(maxAllActions)

                # Q(v,a) + a(r + y*MAX^all possible actions^(Q(nv, a)) - Q(v, a)
                fixedQVal = qValBase + Config.q_learn_a * (pastAct.reward + Config.q_learn_y * maxAllActions - qValBase)
                assert not math.isnan(fixedQVal)

                trainBatchY.append(np.array(fixedQVal))
            self.QModel.fit(np.array(trainBatchX), np.array(trainBatchY), verbose=0)

        option = 4
        if option == 2:
            pastActionsWithViews: list[tuple[PastAction, AgentView]] = []
            for i, perfAct in enumerate(performedActionList):
                if self.distanceTo(perfAct.agent) < Config.agent_coms_distance:
                    pastActionsWithViews.append(
                        (PastAction(perfAct.action, perfAct.agentView, perfAct.success, reward), newVisions[i]))
            FitForPastActions(pastActionsWithViews)
        elif option == 4:
            pastActionsWithViews: list[tuple[PastAction, AgentView]] = []
            for i, perfAct in enumerate(performedActionList):
                if self.distanceTo(perfAct.agent) < Config.agent_coms_distance:
                    pastActionsWithViews.append(
                        (PastAction(perfAct.action, perfAct.agentView, perfAct.success, reward), newVisions[i]))
                    agentMemory = perfAct.agent.getActionMemory()
                    for i2, agentsPastAct in enumerate(agentMemory[0:-1]):
                        nextView = agentMemory[i2+1].agentView
                        pastActionsWithViews.append(
                            (PastAction(agentsPastAct.action, agentsPastAct.agentView, agentsPastAct.success, reward), nextView))
            FitForPastActions(pastActionsWithViews)
        else:
            raise NotImplementedError

        action: Action
        succeeded: bool
        if self.getLastAction() is None:
            return
        pastAct = self.getLastAction()
        pass

    def distanceTo(self, agent) -> float:
        return math.sqrt((self.x-agent.x) * (self.x-agent.x) + (self.y-agent.y) * (self.y-agent.y))

    @staticmethod
    def createDeltaNN() -> keras.Model:
        model = Sequential()
        # agent view -> value for each action [-1,1]
        model.add(Dense(100, activation='relu'
                        , input_dim=Config.agent_view_zone_size*Config.agent_view_zone_size))
        #model.add(Dense(100, activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(len(Action.getAll()), activation='softsign'))

        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def calculateDelta(self, agentViews: Union[AgentView, list[AgentView]]):
        if not isinstance(agentViews, list):
            agentViews = [agentViews]
        inputs = [av.toList() for av in agentViews]
        deltaPredictions = self.deltaModel.predict(inputs)
        for d in deltaPredictions:
            for p in d:
                assert not math.isnan(p)
        return deltaPredictions

    @staticmethod
    def createQNN() -> keras.Model:
        model = Sequential()
        # agent view + action -> action value [float] [-1,1]
        model.add(Dense(100, activation='relu'
                        , input_dim=Config.agent_view_zone_size*Config.agent_view_zone_size+1))
        #model.add(Dense(100, activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(1, activation='softsign'))

        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def calculateQ(self, inputObjs: Union[tuple[AgentView, Action], list[tuple[AgentView, Action]]]):
        if not isinstance(inputObjs, list):
            inputObjs = [inputObjs]
        inputs = []
        for av, act in inputObjs:
            input = av.toList()
            input.append(act.getCode())
            inputs.append(input)
        predictions = self.QModel.predict(inputs)
        #print(predictions)
        for d in predictions:
            assert not math.isnan(d[0])
        return predictions
