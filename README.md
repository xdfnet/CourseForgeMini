# 优课工坊迷你版（CourseForge™ Mini）

## 使命愿景

致力于通过 AI 技术革新教育内容创作，让每位教育工作者都能轻松打造专业、高质量的课程内容。我们相信，通过降低优质课程的创作门槛，可以让更多学习者受益于更好的教育资源。

## 项目概述

优课工坊迷你版是一款轻量级的 AI 课程生成工具，专注于快速创建结构化的课程内容。基于智谱 AI 的 GLM-4 模型，为教育工作者提供智能辅助。本项目具有以下特点：

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

## 快速开始

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **配置 API**

   创建 `.env` 文件并添加：

   ```
   ZHIPU_API_KEY=你的智谱AI密钥
   ```

3. **运行程序**

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
- 智谱 AI API 密钥

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

```bash
pyinstaller smac.spec
```

## 目录结构

```
CourseForgeMini/
├── main.py           # 主程序
├── config.py         # 配置管理
├── api_client.py     # API 客户端
├── prompt_functions.py # 提示词生成
├── requirements.txt  # 依赖清单
└── .env             # 环境变量
```

## 常见问题

1. **找不到 .env 文件？**
   - 确保在项目根目录创建 .env 文件
   - 检查 API 密钥格式是否正确

2. **生成内容失败？**
   - 检查网络连接
   - 确认 API 密钥有效
   - 查看日志获取详细错误信息

## 联系方式

- 邮箱：<xdfnet@gmail.com>
- 官网：
  - [www.courseforge.cn](https://www.courseforge.cn)
  - [www.course-forge.com](https://www.course-forge.com)

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

Copyright (c) 2024 CourseForge

## 致谢

感谢智谱 AI 提供的 GLM-4 模型支持。
