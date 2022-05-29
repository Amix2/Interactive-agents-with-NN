# following lines are a workaround for avoiding circular deps with typing-related imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from action import Action
    from agent import Agent
    from agentView import AgentView


class PerformedAction:
    def __init__(self, agent: Agent, action: Action, agentView: AgentView, success: bool = None, reward: float = None):
        self.agent = agent
        self.action = action
        self.agentView = agentView
        self.success = success
        self.reward = reward
