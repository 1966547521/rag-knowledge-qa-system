import os
import random
from utils.config_handler import agent_conf
from utils.logger_handler import logger
from utils.path_tool import get_abs_path
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService

rag = RagSummarizeService()
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]

external_data = {}

_user_city = None


def set_user_city(city: str):
    global _user_city
    _user_city = city


@tool(description='从向量存储中检索参考资料')
def rag_summarize_service(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description='获取指定城市的实时天气，返回天气描述信息字符串')
def get_weather(city: str) -> str:
    from utils.geo_location import fetch_weather
    return fetch_weather(city)


@tool(description='获取用户所在城市名称，优先使用手动输入的城市和IP定位，以纯字符串的形式返回')
def get_user_location() -> str:
    global _user_city
    if _user_city:
        return _user_city
    from utils.geo_location import get_city_name
    city = get_city_name()
    if city:
        return city
    return random.choice(["长沙", "上海", "南京"])


@tool(description='获取用户id，以纯字符串的形式返回')
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description='获取当前月份，以纯字符串形式返回')
def get_current_month() -> str:
    return random.choice(month_arr)


# 将外部数据进行整理归类
def generate_external_data():
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(external_data_path):
            raise Exception(f"[外部数据]指定的{external_data_path}路径不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }


@tool(description='从外部系统中获取用户的使用记录，以纯字符串形式返回，未检索到则返回空字符串')
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()

    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warn(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用数据")
        return ""


@tool(description='无入参，无返回值，调用后触发中间件，自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息')
def fill_context_report():
    return "fill_context_report已调用"

if __name__ == '__main__':
    print(fetch_external_data("1001", "2025-01"))
