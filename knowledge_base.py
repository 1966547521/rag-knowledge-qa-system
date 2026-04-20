"""
知识库
"""
import os
import config_data as config
import hashlib
from datetime import datetime
from langchain_chroma import Chroma  # 数据库相关
from langchain_community.embeddings import DashScopeEmbeddings  # 向量转化相关
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 文本分隔相关，（此为递归文本分割器）
import logging

logger = logging.getLogger(__name__)


def check_md5(md5_str: str):
    """检查传入的md5字符串是否已经被处理过了
        return False(md未处理) True(已处理，记录)
    """

    if not os.path.exists(config.md5_path):
        # if进入表示文件不存在，即该文件为未处理文件
        open(config.md5_path, 'w', encoding='utf-8').close()
        return False
    else:
        # 逻辑：打开文件遍历主要内容，再处理一遍，相同即已经处理过了
        for line in open(config.md5_path, 'r', encoding='utf-8').readlines():
            line = line.strip()  # 处理字符串前后的空格和回车
            if line == md5_str:
                return True  # 已处理

        return False


def save_md5(md5_str: str):
    """将传入的md5字符串，记录到文件内保存"""
    with open(config.md5_path, 'w', encoding='utf-8') as f:
        f.write(md5_str + '\n')


def get_string_md5(input_str: str, encoding='utf-8'):
    """将传入的字符串转换为md5字符串"""

    # 将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding=encoding)

    # 创建md5对象
    md5_obj = hashlib.md5()  # 得到md5对象
    md5_obj.update(str_bytes)  # 更新md5对象内的内容
    md5_hex = md5_obj.hexdigest()  # 将内容转化为十六进制字符串

    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        # 检验文件夹是否存在，不存在则创建，存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,  # 数据库表名
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            persist_directory=config.persist_directory,  # 数据库本地文件夹
        )  # 向量存储的实例 Chroma向量库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  # 分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,  # 连续文本段之间的字符重叠数量
            separators=config.separators,  # 自然段落分隔的符号
            length_function=len,  # 使用Python自带的len函数做长度统计的依据
        )  # 文本分割器的对象

    def upload_by_str(self, data: str, filename):
        try:
            md5_hex = get_string_md5(data)
            if check_md5(md5_hex):
                return {"status": "skipped", "message": "内容已在数据库中存在"}

            # 分割文本
            if len(data) > config.min_split_char_number:
                knowledge_chunks = self.spliter.split_text(data)
            else:
                knowledge_chunks = [data]

            metadata = {
                "filename": filename,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "operator": "Yinsky",
            }

            # 向量化入库（捕获异常）
            try:
                self.chroma.add_texts(knowledge_chunks, metadatas=[metadata for _ in knowledge_chunks])
            except Exception as e:
                logger.error(f"向量库写入失败: {e}", exc_info=True)
                return {"status": "error", "message": f"向量化失败: {str(e)}"}

            # 保存MD5（捕获异常）
            try:
                save_md5(md5_hex)
            except IOError as e:
                logger.error(f"MD5文件写入失败: {e}")
                # 不影响主流程，但需提醒用户
                return {"status": "partial", "message": "内容已入库但MD5记录失败"}

            logger.info(f"成功入库文件: {filename}, 分块数: {len(knowledge_chunks)}")
            return {"status": "success", "message": "内容已成功载入向量库"}

        except Exception as e:
            logger.error(f"上传处理未预期异常: {e}", exc_info=True)
            return {"status": "error", "message": f"系统内部错误: {str(e)}"}


if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("石田", "testfile")
    print(r)