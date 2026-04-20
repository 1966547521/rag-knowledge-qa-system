"""
基于Streamlit完成WEB网页上传服务

Streamlit：当WEB页面元素变化时，代码会重新进行一次
"""
import time

import streamlit as st
from knowledge_base import KnowledgeBaseService

# 网页标题
st.title("知识库更新")

# file_uploader
uploader_file = st.file_uploader(
    "请上传TXT文件",
    type=["txt"],
    accept_multiple_files=False,  # False 表示只接受一个文件的上传
)

# 将创建的KnowledgeBaseService对象存入session_state中
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


if uploader_file is not None:
    # 提取文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024  # 换算单位为kb

    st.subheader(f"文件名{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f}kb")

    # # 获取文件内容 getvalue -> bytes -> decode('utf-8')
    text = uploader_file.getvalue().decode("UTF-8")
    # st.write(file_value)

    with st.spinner("载入知识库中..."):           # spinner转圈载入动画
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(text, file_name)
        st.write(result)
