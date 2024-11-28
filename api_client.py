from config import CONFIG
from functools import lru_cache
import time
from typing import List, Dict, Optional
from PyQt6.QtWidgets import QMainWindow

@lru_cache(maxsize=128)
def cached_isinstance(obj, class_or_tuple):
    return isinstance(obj, class_or_tuple)

@lru_cache(maxsize=128)
def cached_len(obj):
    return len(obj)

def chat_with_moonshot(client, prompt: str, history: Optional[List[Dict]] = None, window: Optional[QMainWindow] = None) -> str:
    """
    与 API 进行对话
    
    Args:
        client: API客户端实例
        prompt: 提示词
        history: 对话历史
        window: 主窗口实例，用于显示日志
    
    Returns:
        str: API返回的响应内容
    """
    try:
        if history is None:
            history = []
            
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = client.chat.completions.create(
                    model=CONFIG['MODEL'],
                    messages=[
                        *history,
                        {"role": "user", "content": prompt}
                    ],
                    temperature=CONFIG['TEMPERATURE'],
                    max_tokens=CONFIG['MAX_TOKENS'],
                    top_p=CONFIG['TOP_P'],
                    stream=False
                )
                
                if response and response.choices:
                    return response.choices[0].message.content
                else:
                    raise Exception("API返回为空")
                    
            except Exception as e:
                retry_count += 1
                if window:
                    window.log_message(f"API调用失败，正在进行第{retry_count}次重试...")
                time.sleep(2)  # 重试前等待2秒
                
                if retry_count >= max_retries:
                    raise Exception(f"API调用失败，已重试{max_retries}次: {str(e)}")
                
    except Exception as e:
        if window:
            window.log_message(f"发生错误: {str(e)}")
        raise e
        
    return ""
