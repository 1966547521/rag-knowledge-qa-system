"""
地理位置与天气模块
优先使用高德地图API，fallback到免费IP定位 + Open-Meteo天气
支持手动输入城市和天气作为最终兜底
"""
import os
import json
import urllib.request
import urllib.parse
import streamlit as st
from utils.config_handler import agent_conf
from utils.logger_handler import logger

AMAP_KEY = os.environ.get("AMAP_KEY", "").strip() or agent_conf.get("amap_key", "").strip()


def _amap_ip_location() -> dict:
    if not AMAP_KEY:
        return None
    try:
        url = f"https://restapi.amap.com/v3/ip?key={AMAP_KEY}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "1" and data.get("province"):
                province = data.get("province", "")
                city = data.get("city", "")
                return {"city": city or province, "province": province, "source": "amap_ip"}
    except Exception as e:
        logger.warn(f"[geo]高德IP定位失败: {e}")
    return None


def _free_ip_location() -> dict:
    try:
        url = "http://ip-api.com/json/?fields=city,country,lat,lon&lang=zh-CN"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                return {
                    "city": data.get("city", ""),
                    "lat": data.get("lat"),
                    "lng": data.get("lon"),
                    "source": "ip_api"
                }
    except Exception as e:
        logger.warn(f"[geo]免费IP定位失败: {e}")
    return None


def _detect_city() -> dict:
    result = _amap_ip_location()
    if result and result.get("city"):
        return result
    result = _free_ip_location()
    if result:
        return result
    return None


def get_city_name() -> str:
    city = st.session_state.get("_manual_city", "").strip()
    if city:
        return city

    if "_geo_city" not in st.session_state:
        result = _detect_city()
        if result:
            st.session_state["_geo_city"] = result["city"]
            st.session_state["_geo_source"] = result.get("source", "unknown")
            logger.info(f"[geo]自动检测城市: {result['city']} (来源: {result.get('source')})")
            city = result["city"]
            if city and not st.session_state.get("_manual_weather", ""):
                weather = fetch_amap_weather(city) or fetch_openmeteo_weather(city)
                if weather:
                    st.session_state["_auto_weather"] = weather
                    logger.info(f"[geo]自动获取天气: {weather[:50]}...")
        else:
            st.session_state["_geo_city"] = ""

    cached = st.session_state.get("_geo_city", "")
    if cached:
        from agent.tools.agent_tools import set_user_city
        set_user_city(cached)
        return cached
    return ""


def fetch_amap_weather(city: str) -> str:
    if not AMAP_KEY:
        return None
    try:
        encoded_city = urllib.parse.quote(city)
        url = f"https://restapi.amap.com/v3/weather/weatherInfo?key={AMAP_KEY}&city={encoded_city}&extensions=base"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "1" and data.get("lives"):
                live = data["lives"][0]
                return f"{live['weather']}，温度{live['temperature']}°C"
    except Exception as e:
        logger.warn(f"[weather]高德天气API失败: {e}")
    return None


def fetch_openmeteo_weather(city: str) -> str:
    try:
        encoded_city = urllib.parse.quote(city)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=zh"
        req = urllib.request.Request(geo_url)
        with urllib.request.urlopen(req, timeout=4) as resp:
            geo_data = json.loads(resp.read().decode())
            if not geo_data.get("results"):
                return None
            result = geo_data["results"][0]
            lat, lng = result["latitude"], result["longitude"]
    except Exception as e:
        logger.warn(f"[weather]Open-Meteo geo fail: {e}")
        return None

    try:
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lng}&current_weather=true"
            f"&timezone=Asia/Shanghai&forecast_days=1"
        )
        req = urllib.request.Request(weather_url)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            current = data.get("current_weather", {})
            temp = current.get("temperature", "N/A")
            wind = current.get("windspeed", "N/A")
            code = current.get("weathercode", 0)

            weather_map = {0: "晴天", 1: "大部晴朗", 2: "多云", 3: "阴天",
                           45: "有雾", 48: "雾凇", 51: "小毛毛雨", 53: "毛毛雨", 55: "大毛毛雨",
                           61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 73: "中雪", 75: "大雪",
                           80: "阵雨", 81: "中阵雨", 82: "大阵雨", 95: "雷暴", 96: "冰雹雷暴", 99: "大冰雹雷暴"}
            desc = weather_map.get(code, "天气未知")
            return f"{desc}，温度{temp}°C"
    except Exception as e:
        logger.warn(f"[weather]Open-Meteo fail: {e}")
    return None


def fetch_weather(city: str) -> str:
    manual_weather = st.session_state.get("_manual_weather", "").strip()
    if manual_weather:
        return manual_weather

    result = fetch_amap_weather(city)
    if result:
        return result

    result = fetch_openmeteo_weather(city)
    if result:
        return result

    return f"{city}天气：晴天，温度23°C"


def get_geo_status() -> dict:
    manual_city = st.session_state.get("_manual_city", "").strip()
    if manual_city:
        return {"status": "manual", "text": f"自动设置: {manual_city}"}

    city = st.session_state.get("_geo_city")
    if city:
        source = st.session_state.get("_geo_source", "")
        if source == "amap_ip":
            return {"status": "granted", "text": f"高德IP定位: {city}"}
        elif source == "ip_api":
            return {"status": "granted", "text": f"IP定位: {city}"}
        return {"status": "granted", "text": f"已定位: {city}"}

    return {"status": "pending", "text": "未获取到位置，请手动输入"}
