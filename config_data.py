md5_path = './md5.text'

# Chroma
collection_name = "rag"
persist_directory = "./chroma_db"

# Spliter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
min_split_char_number = 1000  # 文本分隔的阈值

# retriever
similarity_threshold = 2  # 检索返回匹配的文档数量

# model
embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3-max"

# Chat_history
chat_history_path = "./chat_history"

# session_id配置
session_config = {
    "configurable": {
        "session_id": "user_001"
    }
}
