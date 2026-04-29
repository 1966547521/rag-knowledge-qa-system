# 🤖 智扫通 · 机器人智能客服系统

基于 LangChain + Streamlit 构建的扫地机器人领域 AI 智能客服，集成 RAG 知识库检索、实时天气查询、使用报告生成等功能。

## 功能特性

- **💬 智能问答** — React Agent 多工具编排，支持 RAG 知识检索、天气查询、用户数据查询
- **📚 RAG 知识库** — Chroma 向量数据库，涵盖选购指南、故障排除、维护保养等模块
- **🌤 实时天气** — 高德地图 API 定位 + 天气查询，支持 Open-Meteo 免费降级和手动输入兜底
- **📊 报告生成** — 根据用户使用记录自动生成扫地机器人使用报告
- **💾 会话管理** — 多会话新建/删除/切换，本地 JSON 持久化，预留数据库接口
- **🎨 科技感 UI** — Streamlit 定制蓝黑渐变侧边栏，思考动画，版本信息固定展示

## 技术栈

| 技术 | 用途 |
|---|---|
| Python | 开发语言 |
| LangChain / LangGraph | Agent 编排框架与工作流 |
| Streamlit | Web 交互界面 |
| Chroma | 向量数据库 |
| 通义千问 (Qwen) | 大语言模型 |
| DashScope Embeddings | 文本嵌入模型 |
| 高德地图 API | IP 定位 + 实时天气 |
| Open-Meteo API | 免费天气降级方案 |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/1966547521/rag-knowledge-qa-system.git
cd rag-knowledge-qa-system
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

**方式一：环境变量（推荐）**

```bash
# Windows PowerShell
$env:AMAP_KEY="你的高德地图Key"
$env:DASHSCOPE_API_KEY="你的通义千问API Key"
```

**方式二：配置文件**

编辑 `config/agent.yml` 填入高德地图 Key：

```yaml
amap_key: "你的高德地图Key"
```

### 4. 启动应用

```bash
streamlit run app.py
```

### 5. 构建知识库（首次使用）

侧边栏点击「加载文档到知识库」，将 `data/` 目录下的文档导入向量数据库。

## 项目结构

```
├── agent/                  # Agent 层
│   ├── react_agent.py      # Agent 定义与流式输出
│   └── tools/
│       ├── agent_tools.py  # 工具函数（RAG/天气/用户数据）
│       └── middleware.py   # Agent 中间件（日志/提示词切换）
├── config/                 # 配置文件
│   ├── agent.yml           # Agent 配置（amap_key 等）
│   ├── chroma.yml          # 向量库配置
│   ├── prompts.yml         # 提示词路径配置
│   └── rag.yml             # 模型与嵌入配置
├── data/                   # 知识库原始文档
│   ├── 选购指南.txt
│   ├── 故障排除.txt
│   ├── 维护保养.txt
│   └── external/records.csv  # 用户使用记录
├── model/
│   └── factory.py          # 模型工厂（ChatModel / Embeddings）
├── prompts/                # 系统提示词
├── rag/                    # RAG 模块
│   ├── rag_service.py      # RAG 检索服务
│   └── vevtor_store.py     # 向量存储服务
├── utils/                  # 工具模块
│   ├── geo_location.py     # 地理位置与天气
│   ├── session_manager.py  # 会话管理（接口 + JSON 实现）
│   ├── ui_components.py    # UI 组件（侧边栏/版本/思考动画）
│   └── ...
├── app.py                  # 主入口
└── README.md
```

## 会话管理

- **新建会话** — 存在空会话时不重复创建
- **切换会话** — 点击历史会话即可切换，保留完整对话记录
- **删除会话** — 删除后自动切换到最近会话或新建

系统支持通过实现 `StorageInterface` 接口切换到数据库存储。

## 定位与天气

定位优先级：

1. 手动输入城市（最高优先级）
2. 高德地图 IP 定位
3. ip-api.com 免费 IP 定位
4. 随机默认城市（最终兜底）

天气优先级：

1. 手动输入天气
2. 高德地图实时天气 API
3. Open-Meteo 免费天气 API
4. 默认值（晴天，23°C）

## 许可证

MIT License
