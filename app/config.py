import os
import yaml

# 读取配置文件
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml"
)

with open(config_path, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# API配置
API_VERSION = config["API"]["Version"]
API_ENVIRONMENT = config["API"]["Environment"]
MAX_COMMENTS = config["API"].get("Max_Comments", 50000)

# Web配置
MAX_TAKE_URLS = config["Web"]["Max_Take_URLs"]
