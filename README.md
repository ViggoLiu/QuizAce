# QuizAce

武汉理工大学 软件工程 大作业 QuizAce 平台

Wuhan University of Technology Software Engineering Final Assignment — QuizAce Platform

## 项目介绍

QuizAce 是一个服务于高校课程考试的在线出题、答题与智能批阅平台。系统既可以收集历年真题与练习题形成题库，又能支持课堂小测、在线考试、AI/教师批阅等多种教学场景。

This repository stores the code for an **QuizAce**, an online exam and smart grading system tailored to university courses. It focuses on curating question banks (past exams/practice drills) and enabling online exams, in-class quizzes, and AI- or teacher-assisted grading workflows.

## 功能特性

### 核心功能
- 🏢 **多角色支持**：学生、教师、管理员三种角色，权限分明
- 📚 **题库管理**：支持多种题型（选择题、填空题、简答题等），可导入/导出题目
- 📝 **在线出题**：教师可快速创建试卷，支持随机组卷、手动组卷
- 📄 **在线考试**：支持定时考试、防作弊监控、自动提交
- 🤖 **智能批阅**：选择题自动批阅，主观题AI辅助批阅
- 📊 **成绩统计**：多维度成绩分析，可视化报表
- 📚 **学习资源**：支持上传和管理学习资料

### 技术亮点
- 前后端分离架构，开发效率高
- 响应式设计，适配多种设备
- 模块化开发，便于扩展
- 支持RESTful API，接口规范

## 技术栈

### 后端
- **框架**：Django 4.2.7
- **语言**：Python 3.x
- **数据库**：MySQL
- **依赖**：numpy, pandas, tensorflow (for AI features)

### 前端
- **框架**：Vue 3
- **UI组件库**：Element Plus
- **状态管理**：Vuex
- **路由**：Vue Router
- **HTTP客户端**：Axios
- **样式**：SCSS

## 目录结构

```
QuizAce/
├── backend/                  # 后端代码
│   └── quizace/             # Django项目
│       ├── quizace/         # 项目配置
│       ├── user/            # 用户模块
│       ├── learning_resource/ # 学习资源模块
│       ├── templates/       # 模板文件
│       ├── manage.py        # Django管理脚本
│       ├── requirements.txt # 依赖列表
│       └── readme.md        # 后端说明文档
├── frontend/                # 前端代码
│   └── quizace/             # Vue项目
│       ├── public/          # 静态资源
│       ├── src/             # 源代码
│       ├── package.json     # 项目配置
│       └── README.md        # 前端说明文档
├── se.sql                   # 数据库初始化脚本
└── README.md                # 项目总说明文档
```

## 安装与运行

### 环境要求
- Python 3.8+
- Node.js 14+
- MySQL 8.0+

### 后端部署

1. **安装依赖**
   ```bash
   cd backend/quizace
   pip install -r requirements.txt
   ```

2. **配置数据库**
   - 创建MySQL数据库
   - 修改`quizace/settings.py`中的数据库配置

3. **初始化数据库**
   ```bash
   python manage.py migrate
   ```

4. **运行开发服务器**
   ```bash
   python manage.py runserver
   ```

### 前端部署

1. **安装依赖**
   ```bash
   cd frontend/quizace
   npm install
   ```

2. **配置API地址**
   - 修改`src/config.js`中的API基础地址

3. **运行开发服务器**
   ```bash
   npm run serve
   ```

4. **构建生产版本**
   ```bash
   npm run build
   ```

## 项目说明

### 模块划分

#### 后端模块
- `user`: 用户认证与管理
- `quiz`: 题库与考试管理
- `learning_resource`: 学习资源管理

#### 前端模块
- `views`: 页面组件
- `components`: 通用组件
- `api`: API请求封装
- `store`: Vuex状态管理
- `router`: 路由配置

### 开发规范

1. **代码风格**
   - Python: PEP 8
   - JavaScript/HTML/CSS: 遵循ESLint和Prettier配置

2. **命名规范**
   - 文件名: 小写字母，下划线分隔
   - 类名: 驼峰式命名
   - 函数/变量名: 小写字母，下划线分隔

3. **提交规范**
   - 提交信息: 简洁明了，使用中文
   - 提交频率: 每个功能模块完成后提交一次

## 团队成员

- **项目经理**: XXX
- **后端开发**: XXX, XXX
- **前端开发**: XXX, XXX
- **测试**: XXX
- **文档**: XXX

## 许可证

MIT License

## 致谢

感谢武汉理工大学计算机科学与技术学院提供的指导和支持。

## 联系方式

如有问题或建议，请通过以下方式联系我们：
- Email: xxx@example.com
- GitHub: https://github.com/yourusername/QuizAce

---

**Note**: This code is provided for reference purposes only. If you find it helpful, please give us a star.