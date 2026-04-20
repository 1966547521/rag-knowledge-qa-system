from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from file_history_store import get_history


def print_prompt(prompt):
    print("=" * 20)
    print(prompt.to_string())
    print("=" * 20)

    return prompt


class RagService(object):
    def __init__(self):

        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主，"
                           "简洁和专业的回答用户问题。参考资料:{context}。"),
                ("system", "并且我提供用户的对话历史记录，如下："),
                MessagesPlaceholder("history"),
                ("user", "请回答用户提问：{input}")
            ]
        )

        self.chat_model = ChatTongyi(model=config.chat_model_name)

        self.chain = self.__get_chain()

    def __get_chain(self):
        """获取最终链"""
        retriever = self.vector_service.get_retriever()

        # 将接受的列表中的各个字符串提取出来转化为一长串字符串
        def format_document(docs: list[Document]):
            if not docs:
                return "无相关参考资料"

            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str

        # 为检索器做格式化
        # 作用：获取输入，修改输入内容使得输入内容可以匹配向量检索器
        def format_for_retriever(value: dict) -> str:
            return value["input"]

        # 维持对话历史记录
        # 作用：将存储与format_document中的内容{input:{input,history}, context}转化为提示词所需的三种内容{input, context, history}
        def format_for_prompt_template(value):
            new_value = {
                "input": value["input"]["input"],
                "context": value["context"],
                "history": value["input"]["history"]
            }
            return new_value

        chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | format_document
            } | RunnableLambda(format_for_prompt_template) | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        return conversation_chain


if __name__ == "__main__":
    res = RagService().chain.invoke({"input": "颜色呢"}, config.session_config)
    print(res)
