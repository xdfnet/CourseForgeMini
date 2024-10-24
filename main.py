# 导入必要的库
import sys, os, re, json, markdown, requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QProgressBar
from PyQt6.QtGui import QIcon, QIntValidator
from openai import OpenAI
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from PyQt6.QtCore import QThread, pyqtSignal
from functools import lru_cache

# 设置 Moonshot 模型常量
MOONSHOT_MODEL = "moonshot-v1-128k"
MAX_TOKENS = 128000

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-9eVg2GTPjYcMEtfGntrNZlsBwSt0nOBcuHIZ5sSXP2SL3HtS",
    base_url="https://api.moonshot.cn/v1"
)

@lru_cache(maxsize=32)
def sanitize_filename(filename):
    # 清理文件名,移除非法字符
    sanitized = re.sub(r'[\\/*?:"<>|]', '', filename)
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def read_file(file_path):
    # 读取指定文件的内容
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def ensure_temp_directory():
    temp_dir = 'D:\\temp'
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
            print(f"创建目录成功: {temp_dir}")
        except Exception as e:
            print(f"创建目录失败: {temp_dir}. 错误: {str(e)}")
    return temp_dir

def create_course_directory(title):
    temp_dir = ensure_temp_directory()
    course_dir = os.path.join(temp_dir, sanitize_filename(title))
    os.makedirs(course_dir, exist_ok=True)
    return course_dir

def chat_with_moonshot(prompt, history=None):
    messages = []
    if history:
        for m in history:
            if m["role"] in ["user", "assistant"]:
                messages.append({"role": m["role"], "content": m["content"]})
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=MOONSHOT_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS
        )
        
        result = response.choices[0].message.content
        if history is not None:
            history.append({"role": "user", "content": prompt})
            history.append({"role": "assistant", "content": result})
        return result
    except Exception as e:
        print(f"Moonshot API 调用错误: {str(e)}")
        raise

class HeaderCollectorProcessor(Treeprocessor):
    def __init__(self, max_level):
        super().__init__()
        self.headers = []
        self.max_level = max_level

    def run(self, root):
        for elem in root:
            if elem.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(elem.tag[1])
                if level <= self.max_level:
                    self.headers.append(elem.text)

class HeaderCollectorExtension(Extension):
    def __init__(self, max_level):
        self.max_level = max_level
        super().__init__()

    def extendMarkdown(self, md):
        self.collector = HeaderCollectorProcessor(self.max_level)
        md.treeprocessors.register(self.collector, 'headercollector', 15)

def extract_h2_titles(content):
    """
    从文本内容中提取以 '##' 开头的行，并返回去掉 '##' 后的内容列表
    """
    h2_titles = []
    for line in content.split('\n'):
        if line.strip().startswith('##'):
            h2_titles.append(line.strip()[2:].strip())  # 去掉 '##' 并清理空白
    return h2_titles

class MainWindow(QWidget):
    """
    主窗口类，用于创建和管理用户界面。
    
    包含课程标题、目标用户、章节数量等输入字段，
    以及生成课程大纲和内容的功能。
    """

    def __init__(self):
        super().__init__()
        self.initUI()
        self.chat_history = []
        ensure_temp_directory()  # 确保 temp 目录存在

    def initUI(self):
        """
        初始化用户界面。
        
        创建并布局所有UI元素，包括输入字段、按钮、日志显示和进度条。
        """
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setWindowTitle('CourseForge优课工坊-AI智能课程生成器')
        self.setFixedSize(600, 400)  # 调整窗口大小

        # 创建输入框和标签
        input_fields = [
            ('课程标题:', '新媒体运营入门', '填写课程标题'),
            ('目标用户:', '新媒体运营小白', '填目标用户'),
        ]

        for label_text, default_text, placeholder_text in input_fields:
            hbox = QHBoxLayout()
            label = QLabel(label_text, self)
            label.setFixedWidth(70)  # 设置标签固定宽度
            hbox.addWidget(label)

            input_field = QLineEdit(default_text, self)
            input_field.setPlaceholderText(placeholder_text)
            hbox.addWidget(input_field)

            main_layout.addLayout(hbox)
            setattr(self, label_text.replace(':', ''), input_field)

        # 创建章数和节数输入框
        chapter_section_layout = QHBoxLayout()

        chapter_label = QLabel('章数:', self)
        chapter_label.setFixedWidth(70)
        chapter_section_layout.addWidget(chapter_label)

        self.chapter_input = QLineEdit('2', self)
        self.chapter_input.setPlaceholderText('填写章数')
        self.chapter_input.setValidator(QIntValidator(1, 6))  # 限制输入为1-6的整数
        chapter_section_layout.addWidget(self.chapter_input)

        section_label = QLabel('节数:', self)
        section_label.setFixedWidth(70)
        chapter_section_layout.addWidget(section_label)

        self.section_input = QLineEdit('2', self)
        self.section_input.setPlaceholderText('填写节数')
        self.section_input.setValidator(QIntValidator(1, 6))  # 限制输入为1-6的整数
        chapter_section_layout.addWidget(self.section_input)

        main_layout.addLayout(chapter_section_layout)

        # 创按钮
        button_layout = QHBoxLayout()
        self.submit_button = QPushButton('生成课程纲', self)
        self.submit_button.setFixedHeight(50)
        self.submit_button.clicked.connect(self.submit)
        button_layout.addWidget(self.submit_button)

        self.execute_button = QPushButton('生成课程内容', self)
        self.execute_button.setFixedHeight(50)
        self.execute_button.clicked.connect(self.execute_content)
        button_layout.addWidget(self.execute_button)

        # 添加关闭按钮（现在一直显示）
        self.close_button = QPushButton('关闭课程工具', self)
        self.close_button.setFixedHeight(50)
        self.close_button.clicked.connect(self.close_application)
        button_layout.addWidget(self.close_button)

        # 添加日志显示
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.log_display.setFixedHeight(200)
        main_layout.addWidget(self.log_display)

        # 添加进度条
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_bar)
        self.progress_bar.hide()

        main_layout.addLayout(button_layout)    

        # 设置布局
        self.setLayout(main_layout)

    def log_message(self, message):
        """
        记录日志信息
        
        参数:
        message (str): 要记录的消息
        """
        self.log_display.append(message)

    def submit(self):
        """处理提交按钮点击事件，生成课程大纲"""
        if not self.validate_inputs():
            return

        self.submit_button.setEnabled(False)
        self.log_message("开始生成课程大纲...")
        QApplication.processEvents()

        try:
            title = self.课程标题.text()
            student = self.目标用户.text()
            chapter = self.chapter_input.text()
            section = self.section_input.text()

            self.log_message(f"课程标题: {title}")
            self.log_message(f"目标用户: {student}")
            self.log_message(f"章数: {chapter}")
            self.log_message(f"节数: {section}")

            course_dir = create_course_directory(title)
            self.log_message(f"课程目录: {course_dir}")

            prompt = f"""## 任务（Task）：
您的任务是做一个课程标题{title}，目标学员为{student}的课程大纲。

## 规则与限制（Rules & Restrictions）：
1、课程大纲只有两层结构，章和节。
2、共{chapter}章，每章{section}节。
3、只撰写章名称和节的名字。

## 示例（Example）：
# 第一章 名称
## 1.1 名称
# 第二章 名称
## 2.1 名称

## 输入格式（Format）：
markdown

最后你必须严格按照 <规则与限制><示例>的规则输出;不得输出其他任何无关的内容，更不要做任何多余的解释；"""

            self.log_message("正在用 API 生成内容...")
            content = chat_with_moonshot(prompt)
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
        self.log_message("开始生成课程内容...")
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        try:
            title = self.课程标题.text()
            course_dir = create_course_directory(title)
            course_outline_content = read_file(os.path.join(course_dir, '课程大纲.md'))

            h2_titles = extract_h2_titles(course_outline_content)
            total_steps = len(h2_titles)
            history = []

            for i, section_title in enumerate(h2_titles):
                self.log_message(f"正在生成第 {i+1}/{total_steps} 节：{section_title}")
                content = self.generate_section_content(section_title, history)
                self.save_section_content(section_title, content, course_dir)
                self.update_progress(int((i + 1) / total_steps * 100))
                self.log_message(f"第 {i+1} 节 '{section_title}' 内容生成完成")

            self.log_message("所有课程内容生成完成！")
            self.log_message(f"内容已保存到目录：{course_dir}")
        except Exception as e:
            self.log_message(f"生成课程内容时发生错误: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
        finally:
            self.execute_button.setEnabled(True)
            self.progress_bar.hide()
            self.log_message("课程内容生成过程结束。")

    def generate_section_content(self, title, history):
        prompt = f"""
{title}，怎么理解。
您的任务是做一个课程PPT和授课台词。

## 规则与限制（Rules & Restrictions）：
1、PPT内容为Mircosoft Powerpoint里的SmartArt格式。
2、授课台词要800个字右

## 示例（Example）：
# PPT内容
上线准备
    发布计划
    测试和部署
    培训和文档
发布活动
    营销推广
    用户教育    
    反馈收集

# 授课台词
台词台词

## 输入格式（Format）：
markdown

最后你必须严格按照 <规则与限制>和<示例>的规则输出;不得输出其他任何无关的内容，更不要做任何多余的解释；"""
        return chat_with_moonshot(prompt, history)

    def save_section_content(self, title, content, course_dir):
        formatted_content = f"# {title}\n\n{content}"
        filename = f'{sanitize_filename(title)}.md'
        filepath = os.path.join(course_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        self.log_message(f"{title} - 内容已保存到 {filename}")

    def validate_inputs(self):
        """验证所有输入字段"""
        if not self.课程标题.text().strip():
            self.log_message("错误：课程标题不能为空")
            return False
        if not self.目标用户.text().strip():
            self.log_message("错误：目标用户不能为空")
            return False
        if not self.chapter_input.text().strip():
            self.log_message("错误：章数不能为空")
            return False
        if not self.section_input.text().strip():
            self.log_message("错误：节数不能为空")
            return False
        return True

    def close_application(self):
        self.close()

    def handle_error(self, error_message):
        self.log_message(f"发生错误: {error_message}")
        import traceback
        self.log_message(traceback.format_exc())

if __name__ == '__main__':
    ensure_temp_directory()  # 在程序启动时确保 temp 目录存在
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
