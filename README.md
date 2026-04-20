# RAG 项目实战

这是一个基于 FastAPI 和 LangChain 的 RAG（检索增强生成）项目，用于构建知识库问答系统。

## 功能特性

- 文档上传功能，支持 .txt 文件
- 多会话隔离的问答接口
- 会话历史记录查询
- 基于向量数据库的文档检索

## 项目结构

```
.
├── app_file_uploader.py
├── app_qa.py
├── config_data.py
├── file_history_store.py
├── knowledge_base.py
├── main.py
├── rag.py
├── vector_stores.py
├── data/                  # 示例数据文件
├── chat_history/          # 会话历史（会被 .gitignore 忽略）
├── chroma_db/             # 向量数据库（会被 .gitignore 忽略）
├── requirements.txt       # 项目依赖
└── .gitignore             # Git 忽略文件
```

## 安装步骤

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动服务：
   ```bash
   uvicorn main:app --reload
   ```

## API 接口

### 1. 上传文档

- **POST** `/upload`
- **参数**：file (上传的 .txt 文件)
- **返回**：上传状态和消息

### 2. 问答接口

- **POST** `/query`
- **参数**：
  - question: 用户问题
  - session_id: 会话ID（可选，默认为"default"）
- **返回**：问题、答案和会话ID

### 3. 查看会话历史

- **GET** `/history/{session_id}`
- **参数**：session_id (会话ID)
- **返回**：会话历史记录

### 4. 健康检查

- **GET** `/health`
- **返回**：服务状态

## 配置说明

项目配置位于 `config_data.py` 文件中，主要包括：

- Chroma 向量数据库配置
- 文本分割配置
- 检索器配置
- 模型配置
- 会话历史配置

## 注意事项

- 项目使用了 LangChain 的 DashScopeEmbeddings 和 ChatTongyi，需要确保环境中配置了相应的 API 密钥
- 向量数据库和会话历史会被 .gitignore 忽略，不会被提交到版本控制系统
- 仅支持 .txt 文件上传

## 许可证

MIT License
