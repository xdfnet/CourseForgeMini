import os
import sys
import base64

# 版本号
VERSION = "1.8.0"

def get_api_key():
    """获取 API key"""
    encoded_key = "NTg3NDczNmYzMzM5MDRlYjgwOThkNDUxNGQ1ZTAyZjMucmo4VkdNTnBSd0h1c1BaQQ=="
    try:
        return base64.b64decode(encoded_key).decode('utf-8')
    except Exception as e:
        print(f"解码 API key 失败: {str(e)}")
        return None

def load_config():
    """加载配置"""
    config = {
        'ZHIPU_API_KEY': get_api_key(),
        'BASE_URL': "https://open.bigmodel.cn/api/paas/v4",
        'MODEL': "glm-4-flash",
        'MAX_TOKENS': 2048,
        'MAX_HISTORY_LENGTH': 10
    }
    return config

# 导出配置
CONFIG = load_config()
