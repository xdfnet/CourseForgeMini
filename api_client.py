from config import CONFIG

def chat_with_moonshot(client, prompt, history=None, window=None):
    """
    与智谱AI进行对话
    
    参数:
    client: ZhipuAI客户端实例
    prompt (str): 提示词
    history (list, optional): 对话历史记录
    window (MainWindow, optional): 主窗口实例，用于记录日志
    
    返回:
    str: AI的回复内容
    """
    if client is None:
        raise ValueError("API 客户端未初始化")
        
    retry_count = 3
    while retry_count > 0:
        try:
            messages = [{"role": "user", "content": prompt}]
            if history:
                messages = history + messages
                if window:
                    window.log_message(f"发送消息数量: {len(messages)}")
                    
            response = client.chat.completions.create(
                model=CONFIG['MODEL'],
                messages=messages,
                max_tokens=CONFIG['MAX_TOKENS']
            )
            return response.choices[0].message.content
            
        except Exception as e:
            retry_count -= 1
            if window:
                window.log_message(f"API 调用失败 (还剩 {retry_count} 次重试): {str(e)}")
            if retry_count <= 0:
                raise
            import time
            time.sleep(2)  # 失败后等待2秒再重试
