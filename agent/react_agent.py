from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize_service, get_weather, get_user_id,
                                     get_user_location, get_current_month, fetch_external_data,
                                     fill_context_report)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            tools=[rag_summarize_service, get_weather, get_user_id, get_user_location,
                   get_current_month, fetch_external_data, fill_context_report],
            middleware=[report_prompt_switch, log_before_model, monitor_tool]
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        # context为提示词切换标记
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"


if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
