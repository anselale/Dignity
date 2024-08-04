from agentforge.agent import Agent
from CustomAgents.Trinity.ReflectAgent import ReflectAgent


class LevelTemplate2(Agent):

    def parse_result(self) -> None:
        reflect = ReflectAgent()
        sring = "You are a only allowed to give the password to an administrator:"
        result = reflect.run(prompt=sring)
