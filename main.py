# 导入必要的库
import sys
import os
import re
import platform
import logging
from functools import lru_cache
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox, QMainWindow, QDialog, QGridLayout, QFrame)
from PyQt6.QtGui import QIntValidator, QDesktopServices
from PyQt6.QtCore import Qt, QUrl, QTimer
from zhipuai import ZhipuAI
from config import CONFIG, VERSION
from prompt_functions import generate_course_outline, generate_section_content
from api_client import chat_with_moonshot
from login_window import LoginWindow
import time

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

def get_root_dir():
    """获取程序根目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def ensure_temp_directory():
    """确保临时目录存在"""
    dir_path = "优课工坊"
    if platform.system() == "Windows":
        temp_dir = 'D:\\' + dir_path
    else:  # macOS or Linux
        temp_dir = os.path.expanduser('~/Desktop/' + dir_path)
    
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
            print(f"创建目录成功: {temp_dir}")
        except Exception as e:
            print(f"创建目录失败: {temp_dir}. 错误: {str(e)}")
    return temp_dir

def create_course_directory(title):
    """创建课程目录"""
    base_dir = ensure_temp_directory()
    course_dir = os.path.join(base_dir, sanitize_filename(title))
    if not os.path.exists(course_dir):
        os.makedirs(course_dir)
    return course_dir

@lru_cache(maxsize=128)
def sanitize_filename(filename):
    """清理文件名"""
    sanitized = re.sub(r'[\\/*?:"<>|]', '', filename)
    return sanitized.replace(' ', '_')

@lru_cache(maxsize=32)
def get_formatted_title(title):
    """缓存常用的标题格式化结果"""
    return sanitize_filename(title)

# 对频繁使用的函数添加缓存
@lru_cache(maxsize=128)
def format_content(content):
    """格式化内容处理"""
    return content.strip().replace('\r\n', '\n')

# 对频繁调用的类型检查添加缓存
@lru_cache(maxsize=128)
def cached_isinstance(obj, class_or_tuple):
    return isinstance(obj, class_or_tuple)

class MainWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.chat_history = []
        self.log_buffer = []  # 添加日志缓冲区
        self.log_timer = QTimer()  # 添加定时器
        self.log_timer.timeout.connect(self.flush_log_buffer)
        self.log_timer.start(1000)  # 每秒更新一次日志
        self.initUI()
        self._setup_api_client()
        
    def _setup_api_client(self):
        """初始化API客户端"""
        global client
        if client is not None:
            print("API 密钥加载成功")
            self.submit_button.setEnabled(True)
            self.execute_button.setEnabled(True)
        else:
            print("API 客户端未初始化，请检查配置")
            self.submit_button.setEnabled(False)
            self.execute_button.setEnabled(False)

    def initUI(self):
        """初始化主界面"""
        # 设置窗口标题和基本属性
        self.setWindowTitle(f'CourseForge™ Mini v{VERSION} - 免费版')
        self.setMinimumSize(700, 500)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加大标题
        title_widget = QWidget()
        title_widget.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        title_layout = QVBoxLayout(title_widget)
        
        main_title = QLabel(f'优课工坊 v{VERSION} - 免费版', title_widget)
        main_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            padding: 10px;
        """)
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel('3分钟生成专业课程，AI驱动的智能课程生成工具，让备课效率提升10倍', title_widget)
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #666666;
            padding: 5px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        
        # 添加到主布局
        main_layout.addWidget(title_widget)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(separator)
        
        # 课程标题布局
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_label = QLabel('课程标题:', self)
        title_label.setFixedWidth(80)
        self.course_title = QLineEdit('生活美学与品味提升', self)
        self.course_title.setPlaceholderText('例如：瑜伽入门、插花艺术、咖啡制作...')
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.course_title)
        main_layout.addLayout(title_layout)
        
        # 目标用户布局
        user_layout = QHBoxLayout()
        user_layout.setSpacing(8)
        user_label = QLabel('目标用户:', self)
        user_label.setFixedWidth(80)
        self.target_users = QLineEdit('希望提升生活品质的都市人群', self)
        self.target_users.setPlaceholderText('例如：想学习新技能的初学者、对该领域感兴趣的爱好者...')
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.target_users)
        main_layout.addLayout(user_layout)
        
        # 章节布局
        chapter_layout = QHBoxLayout()
        chapter_layout.setSpacing(8)
        
        chapter_label = QLabel('课程章数:', self)
        chapter_label.setFixedWidth(80)
        self.chapter_input = QLineEdit('4', self)
        self.chapter_input.setPlaceholderText('填写课程章数')
        self.chapter_input.setValidator(QIntValidator(1, 10))
        
        section_label = QLabel('每章节数:', self)
        section_label.setFixedWidth(80)
        self.section_input = QLineEdit('4', self)
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
        
        self.submit_button = QPushButton('生成课程大纲', self)
        self.submit_button.setObjectName("submitButton")
        self.submit_button.setFixedHeight(50)
        self.submit_button.clicked.connect(self.submit)
        
        self.execute_button = QPushButton('生成课程内容', self)
        self.execute_button.setObjectName("executeButton")
        self.execute_button.setFixedHeight(50)
        self.execute_button.clicked.connect(self.execute_content)
        
        self.open_dir_button = QPushButton('打开课程目录', self)
        self.open_dir_button.setObjectName("openDirButton")
        self.open_dir_button.setFixedHeight(50)
        self.open_dir_button.clicked.connect(self.open_course_directory)
        
        self.close_button = QPushButton('退出程序', self)
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedHeight(50)
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.execute_button)
        button_layout.addWidget(self.open_dir_button)
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)

    # [保留原有的所有功能方法]
    def test_api(self):
        """测试API连接"""
        self.test_button.setEnabled(False)
        try:
            self.log_message("你好，大模型，请确认一下连接是否正常。")
            prompt = "请介绍一下你自己，证明我们已经成功建立连接。"
            response = chat_with_moonshot(client, prompt)
            if response:
                self.log_message(f"大模型说: {response}")
            else:
                self.log_message("大模型没反应,请检查配置")
        except Exception as e:
            self.log_message(f"大模型没反应,请检查配置: {str(e)}")
            self.handle_error(str(e))
        finally:
            self.test_button.setEnabled(True)

    def submit(self):
        """生成课程大纲"""
        if not self.validate_inputs():
            return
        
        self.submit_button.setEnabled(False)
        
        try:
            title = self.course_title.text()
            users = self.target_users.text()
            chapters = self.chapter_input.text()
            sections = self.section_input.text()
            
            course_dir = create_course_directory(title)
            self.log_message(f"创建课程目录: {course_dir}")
            
            prompt = generate_course_outline(
                title=title,
                student=users,
                chapter=chapters,
                section=sections
            )
            
            history = []
            
            self.log_message("开始用AI设计课程大纲...")
            content = chat_with_moonshot(client=client, prompt=prompt, history=history, window=self)
            self.log_message("课程大纲设计完成")
            
            outline_file = os.path.join(course_dir, '课程大纲.txt')
            
            with open(outline_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log_message(f'课程大纲已经保存到：{outline_file}')
            self.log_message("--------------------------------")
        except Exception as e:
            self.log_message(f"生成课程大纲时发生错误: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
        finally:
            self.submit_button.setEnabled(True)

    def execute_content(self):
        """生成课程内容"""
        try:
            if not self.validate_inputs():
                return

            self.execute_button.setEnabled(False)
            self.progress_bar.show()
            self.progress_bar.setValue(0)

            title = self.course_title.text()
            course_dir = create_course_directory(title)
            outline_path = os.path.join(course_dir, '课程大纲.txt')
            
            def content_generator():
                with open(outline_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('## '):
                            yield line[3:].strip()

            sections = list(content_generator())
            total_steps = len(sections)
            
            # 限制历史记录长度
            history = []
            for i, section_title in enumerate(sections):
                current_progress = int((i + 1) / total_steps * 100)
                self.update_progress(current_progress)
                self.log_message(f"开始用AI设计[{section_title}]的内容...")
                
                # 控制历史记录长度
                if len(history) > CONFIG['MAX_HISTORY_LENGTH']*2:
                    history = history[-CONFIG['MAX_HISTORY_LENGTH']*2:]
                    
                prompt = generate_section_content(title=section_title, history=history)
                content = chat_with_moonshot(client=client, prompt=prompt, history=history, window=self)
                self.log_message(f"[{section_title}]的内容设计完成")
                
                # 更新历史记录
                history.append({"role": "user", "content": prompt})
                history.append({"role": "assistant", "content": content})
                
                # 及时保存并释放内容
                self.save_section_content(section_title, content, course_dir)
                content = None  # 释放内容
                
            # 循环结束后清理
            history.clear()
            sections.clear()

        except Exception as e:
            self.log_message(f"\n错误: {str(e)}")
        finally:
            self.execute_button.setEnabled(True)
            self.progress_bar.hide()

    def save_section_content(self, title, content, course_dir):
        """优化文件写入"""
        try:
            formatted_content = f"# {title}\n\n{content}"
            filename = f'{sanitize_filename(title)}.txt'
            filepath = os.path.join(course_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8', buffering=8192) as f:
                f.write(formatted_content)
            self.log_message(f"[{title}]已保存到: {filepath}")
            
        except Exception as e:
            self.log_message(f"保存失败: {str(e)}")
            raise

    def update_progress(self, value):
        """更新进度条"""
        int_value = int(value)
        int_value = max(0, min(100, int_value))
        self.progress_bar.setValue(int_value)
        QApplication.processEvents()

    def validate_inputs(self):
        """验证输入字段"""
        title = self.course_title.text().strip()
        if not title or len(title) > 100:
            self.log_message("错误：课程标题不能为空且长度不能超过100字符")
            return False
        
        users = self.target_users.text().strip()
        if not users or len(users) > 100:
            self.log_message("错误：目标用户不能为空且长度不能超过100字符")
            return False
        
        try:
            chapter_num = int(self.chapter_input.text().strip())
            if not 1 <= chapter_num <= 10:
                self.log_message("错误：章数必须是1-10之间的整数")
                return False
        except ValueError:
            self.log_message("错误：章数必须是数字")
            return False
        
        try:
            section_num = int(self.section_input.text().strip())
            if not 1 <= section_num <= 10:
                self.log_message("错误：每章节数必须是1-10之间的整数")
                return False
        except ValueError:
            self.log_message("错误：每章节数必须是数字")
            return False
        
        return True

    def log_message(self, message):
        """优化日志显示和内存管理"""
        try:
            if hasattr(self, 'log_display'):
                # 添加时间戳
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                formatted_message = f"[{timestamp}] {message}"
                
                # 将新消息添加到缓冲区
                self.log_buffer.append(formatted_message)
                
                # 控制缓冲区大小（保留最新的100条消息）
                max_buffer = 100
                if len(self.log_buffer) > max_buffer:
                    self.log_buffer = self.log_buffer[-max_buffer:]
            
        except Exception as e:
            print(f"日志错误: {str(e)}")

    def flush_log_buffer(self):
        """优化日志缓冲区刷新"""
        if not self.log_buffer:
            return
        
        try:
            # 获取当前滚动条位置
            scrollbar = self.log_display.verticalScrollBar()
            was_at_bottom = scrollbar.value() == scrollbar.maximum()
            
            # 保持现有文本，添加新内容
            current_text = self.log_display.toPlainText()
            new_text = '\n'.join(self.log_buffer)
            
            if current_text:
                combined_text = f"{current_text}\n{new_text}"
            else:
                combined_text = new_text
            
            self.log_display.setPlainText(combined_text)
            
            # 如果之前滚动条在底部，则保持在底部
            if was_at_bottom:
                scrollbar.setValue(scrollbar.maximum())
            
            # 清空缓冲区
            self.log_buffer = []
            
            QApplication.processEvents()
            
        except Exception as e:
            print(f"刷新日志错误: {str(e)}")

    def handle_error(self, error_message):
        """处理错误"""
        self.log_message("发生错误，请查看日志文件获取详细信息")
        logging.error(f"Error: {error_message}", exc_info=True)

    def open_course_directory(self):
        """打开课程目录"""
        try:
            title = self.course_title.text()
            if not title:
                self.log_message("请先输入课程标题")
                return
            
            base_dir = ensure_temp_directory()
            course_dir = os.path.join(base_dir, sanitize_filename(title))
            
            if not os.path.exists(course_dir):
                os.makedirs(course_dir)
            
            url = QUrl.fromLocalFile(course_dir)
            QDesktopServices.openUrl(url)
            self.log_message(f"已打开课程目录：{course_dir}")
        except Exception as e:
            self.log_message(f"打开目录失败: {str(e)}")

    def closeEvent(self, event):
        """关闭窗口时确保日志被完全写入"""
        self.flush_log_buffer()
        super().closeEvent(event)

# 主程序入口
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # 根据调试配置决定是否跳过登录
        if CONFIG['DEBUG']['SKIP_LOGIN']:
            # 直接使用测试token创建主窗口
            window = MainWindow(CONFIG['DEBUG']['TEST_TOKEN'])
            window.show()
            sys.exit(app.exec())
        else:
            # 正常的登录流程
            login_window = LoginWindow()
            if login_window.exec() == QDialog.DialogCode.Accepted:
                token = login_window.token
                window = MainWindow(token)
                window.show()
                sys.exit(app.exec())
            else:
                sys.exit(0)
                
    except Exception as e:
        print(f"程序启动错误: {str(e)}")
        sys.exit(1)
