import os
import sys
import base64

# 版本号
VERSION = "2.0.4" #修改了课程标题和目标用户的提示语

# 调试配置
DEBUG = {
    'SKIP_LOGIN': False,  # 是否跳过扫码登录
    'TEST_TOKEN': 'debug_token'  # 调试模式下使用的测试token
}

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
        'MAX_HISTORY_LENGTH': 1,
        'TEMPERATURE': 0.7,
        'TOP_P': 0.95,
        'DEBUG': DEBUG
    }
    return config

# 导出配置
CONFIG = load_config()
