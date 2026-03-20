import os
import yaml

# 读取配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")

with open(config_path, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# API配置 - 必须在config.yaml中配置，否则抛出错误
API_VERSION = config["API"]["Version"]
API_ENVIRONMENT = config["API"]["Environment"]
if "Max_Comments" not in config["API"]:
    raise ValueError("config.yaml 中缺少必需的 'API.Max_Comments' 配置项")
MAX_COMMENTS = config["API"]["Max_Comments"]

# Web配置 - 必须在config.yaml中配置，否则抛出错误
if "Max_Take_URLs" not in config["Web"]:
    raise ValueError("config.yaml 中缺少必需的 'Web.Max_Take_URLs' 配置项")
MAX_TAKE_URLS = config["Web"]["Max_Take_URLs"]
