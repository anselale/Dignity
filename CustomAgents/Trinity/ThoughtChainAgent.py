from CustomAgents.Trinity.ChatAgent import ChatAgent


class ThoughtChainAgent(ChatAgent):

    def parse_result(self):
        self.logger.log(f"{self.agent_name} Results:\n{self.result}", 'debug', 'Trinity')
        result = str(self.result)
        try:
            self.result = {'result': result}
        except Exception as e:
            self.logger.parsing_error(result, e)

