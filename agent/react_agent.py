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
        """
        结构化流式输出
        产出事件: {"type": "thinking_steps", "steps": [...]}, {"type": "answer_chunk", "content": "..."}
        """
        input_dict = {"messages": [{"role": "user", "content": query}]}

        thinking_steps = []
        prev_answer = ""
        seen_ai_idx = 0
        seen_tool_idx = 0

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            messages = chunk["messages"]

            for i in range(seen_ai_idx, len(messages)):
                m = messages[i]
                if getattr(m, 'type', '') == 'ai':
                    seen_ai_idx = i + 1
                    if hasattr(m, 'tool_calls') and m.tool_calls:
                        for tc in m.tool_calls:
                            name = tc.get('name', '')
                            args = tc.get('args', {})
                            args_str = str(args) if args else ""
                            if len(args_str) > 100:
                                args_str = args_str[:100] + "..."
                            step = f"🔧 {name}" + (f" → {args_str}" if args_str else "")
                            thinking_steps.append(step)
                            yield {"type": "thinking_steps", "steps": list(thinking_steps)}

            for i in range(seen_tool_idx, len(messages)):
                m = messages[i]
                if getattr(m, 'type', '') == 'tool':
                    seen_tool_idx = i + 1
                    content = (m.content or "")[:300]
                    if content:
                        thinking_steps.append(f"📋 {content}")
                        yield {"type": "thinking_steps", "steps": list(thinking_steps)}

            for m in messages:
                if getattr(m, 'type', '') == 'ai' and getattr(m, 'content', ''):
                    if not (hasattr(m, 'tool_calls') and m.tool_calls):
                        content = m.content
                        if content != prev_answer:
                            if prev_answer and content.startswith(prev_answer):
                                delta = content[len(prev_answer):]
                            else:
                                delta = content
                            prev_answer = content
                            if delta:
                                yield {"type": "answer_chunk", "content": delta}

        if not prev_answer:
            yield {"type": "answer_chunk", "content": "抱歉，我暂时无法回答这个问题。"}


if __name__ == '__main__':
    agent = ReactAgent()

    for event in agent.execute_stream("帮我查一下扫地机器人怎么维护保养"):
        print(event)
