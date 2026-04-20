from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from knowledge_base import KnowledgeBaseService
from rag import RagService

app = FastAPI(title="RAG Knowledge Base API")

# 初始化服务（单例）
knowledge_service = KnowledgeBaseService()
rag_service = RagService()


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档，存入知识库（所有用户共享）"""
    if not file.filename.endswith('.txt'):
        raise HTTPException(400, "仅支持 .txt 文件")

    content_bytes = await file.read()
    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "文件编码不是 UTF-8")

    result_msg = knowledge_service.upload_by_str(text, file.filename)

    if "[成功]" in result_msg:
        return {"status": "success", "message": result_msg}
    else:
        return {"status": "skipped", "message": result_msg}


@app.post("/query")
async def ask_question(
        question: str = Form(...),
        session_id: str = Form("default")  # 允许用户自定义 session_id
):
    """
    问答接口 - 支持多会话隔离
    - question: 用户问题
    - session_id: 会话ID，不同 ID 对话历史完全隔离
    """
    if not question:
        raise HTTPException(400, "问题不能为空")

    # 动态构造 config，覆盖默认的 session_id
    run_config = {
        "configurable": {
            "session_id": session_id
        }
    }

    try:
        # 调用 RAG 链，传入动态 config
        answer = rag_service.chain.invoke(
            {"input": question},
            config=run_config
        )
    except Exception as e:
        raise HTTPException(500, f"RAG 生成失败: {str(e)}")

    return {
        "question": question,
        "answer": answer,
        "session_id": session_id
    }


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """查看指定会话的历史记录"""
    from file_history_store import get_history
    history_obj = get_history(session_id)
    messages = history_obj.messages
    from langchain_core.messages import message_to_dict
    history_dicts = [message_to_dict(msg) for msg in messages]
    return {"session_id": session_id, "history": history_dicts}


@app.get("/health")
async def health():
    return {"status": "ok"}
