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

    def bid(self, action: Action, agentView: AgentView) -> float:
        # TODO implement
        return random.random()

    def L(self, performedActionList: list[PerformedAction], reward: float) -> None:
        # Options for teaching:
        # 1. Based on this step's action for this agent
        # 2. Based on this step's action for all the agents (in range) (this agent's Q models)
        # 3. Based on history actions for this agent
        # 4. Based on history actions for all the agents (in range) (this agent's Q models)
        option = 2
        if option == 2:
            # lets assume performedActionList contains following actions (in order) a2, a2, a3 and views v1, v2, v3
            # trainBatchX ] [v1, v2, v3...]
            # trainBatchY will be:
            # [ [d(v1)[a1], d(v1)[a2] + a(r-Q(v1,a2)), d(v1)[a3]...],   // fixing value for a2
            #   [d(v2)[a1], d(v2)[a2] + a(r-Q(v2,a2)), d(v2)[a3]...],   // fixing value for a2
            #   [d(v3)[a1], d(v3)[a2], d(v3)[a3] + a(r-Q(v3,a3))...]]   // fixing value for a3
            viewsActions: list[tuple[AgentView, Action]] = []
            views: list[AgentView] = []
            for perfAct in performedActionList:
                if self.distanceTo(perfAct.agent) < Config.agent_coms_distance:
                    viewsActions.append((perfAct.agentView, perfAct.action))
                    views.append(perfAct.agentView)
            Qvalues = self.calculateQ(viewsActions)
            deltaValues = self.calculateDelta(views)
            trainBatchX = []
            trainBatchY = []
            i = 0
            for perfAct in performedActionList:
                if self.distanceTo(perfAct.agent) < Config.agent_coms_distance:
                    trainBatchX.append(np.array(perfAct.agentView.toList()))
                    Y = deltaValues[i]

                    actID = Action.getAll().index(perfAct.action)
                    Y[actID] = Y[actID] + Config.q_learn_a * (perfAct.reward - Qvalues[i][0])
                    trainBatchY.append(np.array(Y))
                    i = i+1

            self.deltaModel.fit(np.array(trainBatchX), np.array(trainBatchY), verbose=0)
        else:
            raise NotImplementedError

    def Q(self, actionList: list[PerformedAction], reward: float) -> None:
        # TODO: implement
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
        model.add(Dense(10, activation='relu'
                        , input_dim=Config.agent_view_zone_size*Config.agent_view_zone_size))
        model.add(Dense(10, activation='relu'))
        model.add(Dense(5, activation='relu'))
        model.add(Dense(len(Action.getAll())))

        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def calculateDelta(self, agentViews: Union[AgentView, list[AgentView]]):
        if not isinstance(agentViews, list):
            agentViews = [agentViews]
        inputs = [av.toList() for av in agentViews]
        deltaPredictions = self.deltaModel.predict(inputs)
        return deltaPredictions

    @staticmethod
    def createQNN() -> keras.Model:
        model = Sequential()
        # agent view + action -> action value [float] [-1,1]
        model.add(Dense(10, activation='relu'
                        , input_dim=Config.agent_view_zone_size*Config.agent_view_zone_size+1))
        model.add(Dense(10, activation='relu'))
        model.add(Dense(5, activation='relu'))
        model.add(Dense(1))

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
        deltaPredictions = self.QModel.predict(inputs)
        return deltaPredictions
