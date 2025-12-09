# QuizAce

武汉理工大学 软件工程基础实验 大作业 QuizAce 平台

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
- 💬 **论坛功能**：支持课程论坛、评论管理，增强师生互动
- 📖 **做题板块**：丰富的练习模式，记录学习轨迹
- 👤 **个人中心**：个性化设置，学习进度跟踪
- ☁️ **云端数据库**：数据安全存储，支持多终端访问

### 技术亮点
- 前后端分离架构，开发效率高
- 响应式设计，适配多种设备
- 模块化开发，便于扩展
- 支持RESTful API，接口规范

## 技术栈

### 后端
- **框架**：Django 4.2.7
- **语言**：Python 3.x
- **数据库**：SQLPub
- **认证**：JWT-based authentication

### 前端
- **框架**：Vue 3
- **UI组件库**：Element Plus
- **状态管理**：Vuex
- **路由**：Vue Router
- **HTTP客户端**：Axios
- **样式**：SCSS
- **AI服务**：ZenMux

## 安装与运行

### 环境要求
- Python 3.8+
- Node.js 14+
- MySQL 8.0+

### 前后端详细部署及说明

详见 `backend/quizace/readme.md` 和 `frontend/quizace/readme.md`

## 开发日志
- 2025-11-28：项目基本框架，
- 2025-12-02：项目框架完善、学习资料上传审核查看
- 2025-12-03：更新做题相关模块，加入云端数据库
- 2025-12-05：添加论坛板块，评论以及评论管理
- 2026-12-09：完善所有模块，接入AI服务


## 许可证

MIT License


## 联系方式

### 开发团队

- **团队成员**：
  - 刘明杰- Email: 499783408@qq.com
  - 钟鸣楚- Email: 1446035863@qq.com

- GitHub: https://github.com/ViggoLiu/QuizAce

如有问题或建议，请通过以上方式联系我们：

---

**Note**: This code is provided for reference purposes only. If you find it helpful, please give us a star.