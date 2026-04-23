import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


# 获取文件的MD5的十六进制字符串
def get_file_md5_hex(file_path: str):
    if not os.path.exists(file_path):
        logger.error(f"[md5计算]{file_path}文件不存在")
        return None

    if not os.path.isfile(file_path):
        logger.error(f"[md5计算]{file_path}不是文件")
        return None

    md5_obj = hashlib.md5()

    chunk_size = 4096  # 4kb分片，防止爆内存
    try:
        with open(file_path, 'rb') as f:  # 分片模式必须二进制读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            """
            等同于下方写法，是一种简便的写法
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5_obj.update(chunk)
            """
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception:
        logger.error(f"获取文件MD5失败：{file_path}")


# 返回文件夹内的文件列表（允许的文件的后缀），返回一个绝对路径
def listdir_with_allowed_type(path: str, allowed_type: tuple[str]):
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_type

    for f in os.listdir(path):
        # 判断后缀是否符合传入要求
        if f.endswith(allowed_type):
            files.append(os.path.join(path, f))

    return tuple(files)


def pdf_loader(file_path: str, password=None) -> list[Document]:
    return PyPDFLoader(file_path, password).load()


def txt_loader(file_path: str) -> list[Document]:
    return TextLoader(file_path, encoding="utf-8").load()
