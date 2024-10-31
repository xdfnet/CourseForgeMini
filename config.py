import os
import sys  # 添加这行
from dotenv import load_dotenv

# 版本号
VERSION = "1.6.0"

def load_config():
    """加载配置"""
    # 确定 .env 文件路径
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    env_path = os.path.join(base_path, '.env')
    
    # 加载环境变量
    load_dotenv(env_path)
    
    # 添加调试信息
    api_key = os.getenv('ZHIPU_API_KEY')
    
    config = {
        'ZHIPU_API_KEY': api_key,
        'BASE_URL': "https://open.bigmodel.cn/api/paas/v4",
        'MODEL': "glm-4-flash",
        'MAX_TOKENS': 2048,
        'MAX_HISTORY_LENGTH': 10
    }
    return config

# 导出配置
CONFIG = load_config()
