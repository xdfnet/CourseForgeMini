# 导入必要的库
import sys
import os
import re
import platform
import logging
from functools import lru_cache
from urllib import request
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox)
from PyQt6.QtGui import QIntValidator
from zhipuai import ZhipuAI
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from config import CONFIG, VERSION  # 从 config.py 导入配置
from prompt_functions import generate_course_outline, generate_section_content
from api_client import chat_with_moonshot
from urllib.request import urlopen  # 导入 urlopen
import json  # 导入 json
import base64

def get_root_dir():
    """获取程序根目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# 初始化客户端
client = None
if CONFIG['ZHIPU_API_KEY']:
    try:
        client = ZhipuAI(api_key=CONFIG['ZHIPU_API_KEY'])
        print("API 客户端初始化成功")
    except Exception as e:
        print(f"初始化智谱 API 客户端失败: {str(e)}")
else:
    print("API key 获取失败")

# 在文件开头的导入部分下面添加这些函数

def ensure_temp_directory():
    """确保临时目录存在"""
    if platform.system() == "Windows":
        temp_dir = 'D:\\temp'
    else:  # macOS or Linux
        temp_dir = os.path.expanduser('~/Desktop/temp')
    
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
            print(f"创建目录成功: {temp_dir}")
        except Exception as e:
            print(f"创建目录失败: {temp_dir}. 错误: {str(e)}")
    return temp_dir

def create_course_directory(title):
    """
    创建课程目录
    
    参数:
    title (str): 课程标题
    
    返回:
    str: 课程目录路径
    """
    base_dir = ensure_temp_directory()
    course_dir = os.path.join(base_dir, sanitize_filename(title))
    if not os.path.exists(course_dir):
        os.makedirs(course_dir)
    return course_dir

@lru_cache(maxsize=32)
def sanitize_filename(filename):
    sanitized = re.sub(r'[\\/*?:"<>|]', '', filename)
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def read_file(filepath):
    """
    读取文件内容
    
    参数:
    filepath (str): 文件路径
    
    返回:
    str: 文件内容
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {str(e)}")
        raise

def extract_h2_titles(content):
    """
    从 Markdown 内容中提取二级标题
    
    参数:
    content (str): Markdown 格式的内容
    
    返回:
    list: 二级标题列表
    """
    titles = []
    for line in content.split('\n'):
        if line.startswith('## '):
            titles.append(line[3:].strip())
    return titles

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.chat_history = []
        
        # 检查全局客户端是否可用
        global client
        if client is not None:
            print("API 密钥加载成功")
            self.submit_button.setEnabled(True)
            self.execute_button.setEnabled(True)
        else:
            print("API 客户端未初始化，请检查配置")
            print("请确保 .env 文件中包含正确的 API 密钥")
            self.submit_button.setEnabled(False)
            self.execute_button.setEnabled(False)

    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setWindowTitle(f'CourseForge Mini v{VERSION}')
        self.setMinimumSize(700, 500)

        # 调整布局间距
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 课程标题布局
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_label = QLabel('课程标题:', self)
        title_label.setFixedWidth(80)
        self.course_title = QLineEdit('新媒体运营入门', self)
        self.course_title.setPlaceholderText('填写课程标题')
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.course_title)
        main_layout.addLayout(title_layout)

        # 目标用户布局
        user_layout = QHBoxLayout()
        user_layout.setSpacing(8)
        user_label = QLabel('目标用户:', self)
        user_label.setFixedWidth(80)
        self.target_users = QLineEdit('新媒体运营小白', self)
        self.target_users.setPlaceholderText('填写目标用户')
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.target_users)
        main_layout.addLayout(user_layout)

        # 章节布局
        chapter_layout = QHBoxLayout()
        chapter_layout.setSpacing(8)
        
        chapter_label = QLabel('课程章数:', self)
        chapter_label.setFixedWidth(80)
        self.chapter_input = QLineEdit('2', self)
        self.chapter_input.setPlaceholderText('填写课程章数')
        self.chapter_input.setValidator(QIntValidator(1, 10))
        
        section_label = QLabel('每章节数:', self)
        section_label.setFixedWidth(80)
        self.section_input = QLineEdit('2', self)
        self.section_input.setPlaceholderText('填写每章节数')
        self.section_input.setValidator(QIntValidator(1, 10))
        
        chapter_layout.addWidget(chapter_label)
        chapter_layout.addWidget(self.chapter_input)
        chapter_layout.addWidget(section_label)
        chapter_layout.addWidget(self.section_input)
        main_layout.addLayout(chapter_layout)

        # 创建日志显示区域
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(200)
        main_layout.addWidget(self.log_display)

        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.test_button = QPushButton('测试连接', self)
        self.test_button.setObjectName("testButton")
        self.test_button.setFixedHeight(50)
        self.test_button.clicked.connect(self.test_api)

        self.submit_button = QPushButton('生成课程大纲', self)
        self.submit_button.setObjectName("submitButton")
        self.submit_button.setFixedHeight(50)
        self.submit_button.clicked.connect(self.submit)

        self.execute_button = QPushButton('生成课程内容', self)
        self.execute_button.setObjectName("executeButton")
        self.execute_button.setFixedHeight(50)
        self.execute_button.clicked.connect(self.execute_content)

        self.close_button = QPushButton('关闭课程工具', self)
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedHeight(50)
        self.close_button.clicked.connect(self.close_application)

        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.execute_button)
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)

        # 设置主布局
        self.setLayout(main_layout)

    def log_message(self, message):
        """在日志显示区域输出信息"""
        # 直接输出原始消息
        self.log_display.append(message)

    def submit(self):
        """处理提交按钮点击事件，生成课程大纲"""
        if not self.validate_inputs():
            return
        
        self.submit_button.setEnabled(False)
        self.log_message("开始生成课程大纲...")
        
        try:
            title = self.course_title.text()
            users = self.target_users.text()
            chapters = self.chapter_input.text()
            sections = self.section_input.text()
            
            # 创建课程目录
            course_dir = create_course_directory(title)  # 添加这行
            self.log_message(f"创建课程目录: {course_dir}")
            
            # 使用模板生成提示词
            prompt = generate_course_outline(
                title=title,
                student=users,
                chapter=chapters,
                section=sections
            )
            
            # 初始化空的历史记录
            history = []
            
            self.log_message("正在用 API 生成内容...")
            content = chat_with_moonshot(client=client, prompt=prompt, history=history, window=self)
            self.log_message("API 调用成功，内容生成完成")
            
            outline_file = os.path.join(course_dir, '课程大纲.md')
            self.log_message(f"准备将内容写入文件: {outline_file}")
            
            with open(outline_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log_message(f'课程大纲生成成功！文件保存在：{outline_file}')
            self.log_message("你现在可以点击'生成课程内容'按钮来生成详细内容。")
        except Exception as e:
            self.log_message(f"生成课程大纲时发生错误: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
        finally:
            self.submit_button.setEnabled(True)
            self.log_message("课程大纲生成过程结束。")

    def update_progress(self, value):
        """
        更新进度条的值
        
        参数:
        value (float): 进度值（0-100之间的浮点数）
        """
        # 将浮点数转换为整数
        int_value = int(value)
        # 确保值在0-100之间
        int_value = max(0, min(100, int_value))
        self.progress_bar.setValue(int_value)
        QApplication.processEvents()

    def execute_content(self):
        """处理执行按钮点击事件，生成课程内容"""
        if not self.validate_inputs():
            return

        self.execute_button.setEnabled(False)
        self.log_message("\n=== 开始生成课程内容 ===")
        self.progress_bar.show()  # 显示进度条
        self.progress_bar.setValue(0)  # 初始化进度条

        try:
            title = self.course_title.text()
            self.log_message(f"课程标题: {title}")
            
            course_dir = create_course_directory(title)
            self.log_message(f"课程目录: {course_dir}")
            
            outline_path = os.path.join(course_dir, '课程大纲.md')
            self.log_message(f"正在课程大纲: {outline_path}")
            course_outline_content = read_file(outline_path)

            h2_titles = extract_h2_titles(course_outline_content)
            total_steps = len(h2_titles)
            self.log_message(f"共找到 {total_steps} 个小节需要生成")
            
            history = []  # 初始化历史记录
            self.log_message("\n=== 开始逐节生成内容 ===")

            for i, section_title in enumerate(h2_titles):
                current_progress = int((i + 1) / total_steps * 100)
                self.update_progress(current_progress)  # 更新进度条
                self.log_message(f"\n[{i+1}/{total_steps}] 开始生成: {section_title}")
                self.log_message("-------------------")
                
                self.log_message("正在调用 AI 接口...")
                # 生成提示词
                prompt = generate_section_content(title=section_title, history=history)
                # 调用 AI 接口
                content = chat_with_moonshot(client=client, prompt=prompt, history=history, window=self)
                self.log_message("AI 内容生成完成")
                
                # 更新历史记录
                history.append({"role": "user", "content": prompt})
                history.append({"role": "assistant", "content": content})
                
                # 如果历史记录太长，保留最近的几条
                if len(history) > CONFIG['MAX_HISTORY_LENGTH'] * 2:
                    history = history[-CONFIG['MAX_HISTORY_LENGTH']*2:]
                
                self.log_message("正在保存内容到文件...")
                self.save_section_content(section_title, content, course_dir)
                
                self.log_message(f"第 {i+1} 节 '{section_title}' 内容生成完成")
                self.log_message("-------------------")

            self.log_message("\n=== 课程生成完成 ===")
            self.log_message(f"所有内容已保存到目录：{course_dir}")
            self.log_message(f"共生成 {total_steps} 个小节")
            self.log_message(f"历史记录长度：{len(history)}")
            
        except Exception as e:
            self.log_message("\n=== 生成过程出现错误 ===")
            self.log_message(f"错误类型: {type(e).__name__}")
            self.log_message(f"错误信息: {str(e)}")
            import traceback
            self.log_message("\n详细错误信息:")
            self.log_message(traceback.format_exc())
        finally:
            self.execute_button.setEnabled(True)
            self.progress_bar.hide()
            self.log_message("\n=== 生成过程结束 ===")

    def save_section_content(self, title, content, course_dir):
        self.log_message(f"准备保存 '{title}' 的内容")
        formatted_content = f"# {title}\n\n{content}"
        filename = f'{sanitize_filename(title)}.md'
        filepath = os.path.join(course_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            self.log_message(f"内容已成功保存到: {filename}")
        except Exception as e:
            self.log_message(f"保存文件时出错: {str(e)}")
            raise

    def validate_inputs(self):
        """验证所有输入字段"""
        # 检查课程标题
        title = self.course_title.text().strip()
        if not title or len(title) > 100:
            self.log_message("错误：课程标题不能为空且长度不能超过100字符")
            return False
        
        # 检查目标用户
        users = self.target_users.text().strip()
        if not users or len(users) > 100:
            self.log_message("误：目标用户不能为空且长度不能超过100字符")
            return False
        
        # 检查章数
        try:
            chapter_num = int(self.chapter_input.text().strip())
            if not 1 <= chapter_num <= 10:
                self.log_message("错误：章数必须是1-10之间的整数")
                return False
        except ValueError:
            self.log_message("错误：章数必须是数字")
            return False
        
        # 检查节数
        try:
            section_num = int(self.section_input.text().strip())
            if not 1 <= section_num <= 10:
                self.log_message("错误：每章节数必须是1-10之间的整数")
                return False
        except ValueError:
            self.log_message("错误：节数必须是数字")
            return False
        
        return True

    def close_application(self):
        self.close()

    def handle_error(self, error_message):
        self.log_message("发生错误，请查看日志文件获取详细信息")  # 修复乱码
        logging.error(f"Error: {error_message}", exc_info=True)
    
    def test_api(self):
        self.test_button.setEnabled(False)
        try:
            # 测试API连接
            self.log_message("你好，大模型，请确认一下连接是否正常。")
            prompt = "请介绍一下你自己，证明我们已经成功建立连接。"  # 定义 prompt
            response = chat_with_moonshot(client, prompt)  # 传递 client 和 prompt
            if response:
                self.log_message(f"大模型说: {response}")
            else:
                self.log_message("API 大模型没反应,请检查配置")
        except Exception as e:
            self.log_message(f"API 大模型没反应,请检查配置: {str(e)}")
            self.handle_error(str(e))
        finally:
            self.test_button.setEnabled(True)

# 主程序入口
if __name__ == '__main__':
    ensure_temp_directory()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
