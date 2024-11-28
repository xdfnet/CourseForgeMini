# CourseForge™ Mini (优课工坊-免费版)

## 使命愿景

致力于通过 AI 技术革新教育内容创作，让每位教育工作者都能轻松打造专业、高质量的课程内容。我们相信，通过降低优质课程的创作门槛，可以让更多学习者受益于更好的教育资源。

## 项目概述

CourseForge™ Mini (优课工坊免费版) 是一款轻量级的 AI 课程生成工具，专注于快速创建结构化的课程内容。基于智谱 AI 的 GLM-4 模型，为教育工作者提供智能辅助。本项目具有以下特点：

- **简单易用**：直观的图形界面，三步即可完成课程生成
- **智能辅助**：利用先进的 AI 模型，自动生成专业的课程内容
- **结构化输出**：自动创建层次分明的课程大纲和详细内容
- **本地化存储**：所有生成的内容都保存为易于编辑的 Markdown 文件
- **持续迭代**：定期更新优化，不断提升生成内容的质量

## 特性

- 🚀 快速生成课程大纲
- 📚 自动创建详细课程内容
- 🎯 支持自定义章节结构
- 💾 自动保存为 Markdown 文件
- 🔄 保持上下文连贯性

## 新增特性

- 🔐 扫码登录功能
- 📊 实时进度显示
- 🔄 API 连接测试
- 💾 自动创建课程目录
- 📝 分章节保存内容
- ⚡ 优化的内存管理
- 🛡️ 输入验证保护

## 技术特点

- 基于 PyQt6 的现代图形界面
- 支持 Windows/macOS 跨平台
- 智能的上下文管理
- 异常处理和错误提示
- 实时日志显示
- 多线程任务处理

## 快速开始

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **运行程序**

   ```bash
   python main.py
   ```

## 使用说明

1. 输入课程基本信息：
   - 课程标题
   - 目标用户
   - 章节数量

2. 点击"生成课程大纲"
3. 点击"生成课程内容"
4. 在桌面的 temp 目录下查看生成的内容

## 系统要求

- Python 3.8+
- PyQt6
- 智谱 AI API 支持

## 开发环境设置

1. **克隆仓库**

   ```bash
   git clone https://github.com/xdfnet/CourseForgeMini.git
   cd CourseForgeMini
   ```

2. **创建虚拟环境**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

## 打包说明

使用 PyInstaller 打包：

```python
# windows
pyinstaller -F -w -i images/app.ico main.py
# mac
pyinstaller --clean --windowed --onefile "--name 'CourseForgeMini' --icon images/app.icns main.py
# linux
pyinstaller --clean --windowed --onefile "--name 'CourseForgeMini' --icon images/app.icns main.py
```

## 目录结构

```plaintext
CourseForgeMini/
├── main.py # 主程序
├── config.py # 配置管理
├── api_client.py # API 客户端
├── prompt_functions.py # 提示词生成
└── requirements.txt # 依赖清单
```

## 系统配置

- Python 3.11+ (推荐)
- 智谱AI GLM-4 API
- 最小 2GB 可用内存
- 500MB 可用磁盘空间

## 目录说明

```plaintext
CourseForgeMini/
├── main.py # 主程序入口
├── config.py # 配置文件
├── api_client.py # API 客户端
├── login_window.py # 登录窗口
├── build_pack.py # 打包脚本
├── images/ # 图标资源
│ ├── app.ico # Windows图标
│ └── app.icns # macOS图标
└── requirements.txt # 依赖清单
```

## 使用限制

- 每章节数限制：1-10
- 每章小节数限制：1-10
- 标题长度：≤100字符
- 用户描述：≤100字符

## 常见问题

1. **生成内容失败？**
   - 检查网络连接
   - 查看日志获取详细错误信息

## 联系方式

- 邮箱：<xdfnet@gmail.com>
- 官网：
  - [CourseForge™ Global](https://www.course-forge.com)
  - [优课工坊中国](https://www.courseforge.cn)

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

Copyright (c) 2024 CourseForge

## 致谢

感谢智谱 AI 提供的 GLM-4 模型支持。
