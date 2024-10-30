def generate_course_outline(title, student, chapter, section):
    prompt = f"""## 任务（Task）：
您的任务是做一个课程标题{title}，目标学员为{student}的课程大纲。

## 规则与限制（Rules & Restrictions）：
1、课程大纲只有两层结构，章和节。
2、共{chapter}章，每章{section}节。
3、只写章名称和节的名字。

## 示例（Example）：
# 第一章 名称
## 1.1 名称
# 第二章 名称
## 2.1 名称

## 输入格式（Format）：
markdown

最后你必须严格按照 <规则与限制><示例>的规则输出;不得输出其他任何无关的内容，更不要做任何多余的解释；"""
    return prompt

def generate_section_content(title, history=None):
    prompt = f"""
您的任务是理解{title}这个主题，并制作一个课程PPT和授课台词。

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
    return prompt
