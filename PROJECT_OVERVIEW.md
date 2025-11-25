# QuizAce Online Exam & Grading Overview

## 项目概览
- 目标：面向高校课程考试，提供题库管理、在线考试/练习、课堂小测以及智能批阅能力，缓解课程真题与练习资源匮乏问题
- 结构：`quizace-frontend/` (Vue 2 + Element UI) 作为前端；`quizace-backend/` (Django 3 + DRF + SQLite) 提供 REST API 与 JWT 认证
- 运行：后端 `pip install -r quizace-backend/requirements.txt` 并 `python manage.py runserver`；前端在 `quizace-frontend/` 执行 `npm install` + `npm run serve`，通过 `/api/...` 访问后端
- 配置：`quizace-backend/ExamOnline/settings.py` 中启用 `rest_framework`, `django_filters`, `import_export`, `xadmin` 及自定义 app，REST 默认 Basic/Session/JWT 认证，并通过 `JWT_AUTH` 自定义响应体

## 前端 quizace-frontend
- 启动：`src/main.js` 注册 VueRouter/Vuex，加载 `plugins/axios.js`（自动附带 Authorization 与 CSRF）和 `plugins/element.js`
- 布局：`src/layout/index.vue` 定义头部菜单 + 用户下拉；`src/router/index.js` 配置 history 路由和守卫（检查 `sessionStorage.Authorization` 并设置标题）
- 认证：`Login.vue`/`Register.vue` 使用 `SlideVerification` 滑块，分别调用 `/api/jwt-auth/` 与 `/api/register/`，成功后将 user/student/token 写入 Vuex + sessionStorage（`src/store/index.js`）
- 考试流程：
  - `Exam.vue` 分页搜索 `/api/exams/`，老师可下发课程测验，学生报名后把考试与试卷 JSON 缓存到 localStorage 并跳转 `Pay.vue`
  - `Answer.vue` 读取缓存 exam/paper，按题型请求 `/api/choices|fills|judges|subjective/`，客观题本地判分并在练习模式下写入 `/api/records/*/`，主观题通过 `/api/upload-subjective/` 上传（带 8 位 identifier）；`TimeCountDown` 倒计时
  - `Practice.vue` 生成练习配置并创建 `/api/practices/` 记录；`Grade.vue` 分页查询 `/api/grades/` 并支持及格筛选；`Record.vue` 回放练习记录，分别命中 `/api/records/...`
- 组件：`Pagination.vue` 包装 Element 分页，`TimeCountDown.vue` 统一倒计时，`SlideVerification.vue` 实现拖动验证

## 后端 quizace-backend/ExamOnline
- 路由：`ExamOnline/urls.py` 注册 DefaultRouter，暴露 `/api/exams|grades|choices|...`，并提供 `/jwt-auth/`、`/upload-subjective/`、`/update-pwd/`
- 用户模块 (`user/`):
  - 模型：`Clazz`, `Student`, `Teacher`（学生与 `auth.User` 一对一）
  - 视图：`RegisterViewSet` 创建用户+学生并加密密码；`StudentViewSet`/`ClazzListViewSet` 提供 CRUD；`UpdatePwdApi` 校验旧密码更新；`jwt_response_payload_handler` 返回 token+用户+学生信息
- 考试模块 (`exam/`):
  - 模型：`Paper`（自动计算总分）、`Exam`（多班级）、`Grade`（含 identifier 用于关联主观题）、`Practice`（练习记录）、`SubjectiveAnswer`（主观题作答/打分）
  - 视图：`ExamListViewSet` 按 student_id 过滤可参加考试，支持搜索/排序；`GradeListViewSet` 汇总成绩并叠加对应 `SubjectiveAnswer` 分数；`PracticeListViewSet` 管理练习；`SubjectiveListViewSet` 按 `score` 是否为空排序返回待批阅主观题
  - 过滤：`exam/filter.py` 允许考试日期范围查询
  - 注意：`exam/serializers.py` 中 `SubjectiveSerializer` 试图导入 `exam.models.Subjective`，但该模型不存在（应为 `SubjectiveAnswer` 或 `question.Subjective`），运行前需修正引用
- 题库模块 (`question/`):
  - `models.py` 定义选择/填空/判断/主观题，带难度、解析和分值
  - `views.py` 按题量和难度随机抽题，`UploadSubjective` API 保存学生主观题答案及 identifier
- 练习记录 (`record/`):
  - `Record` 抽象基类派生 `ChoiceRecord`, `FillRecord`, `JudgeRecord`, `SubjectiveRecord`（主观题额外保存执行输出）
  - ViewSet/Serializer 提供 `/api/records/*/` 列表与创建，供前端练习回放页使用
- 管理端：集成 `xadmin` 与 `import_export`（静态与模板目录提供资源），方便录题与批阅

## 端到端流程
1. 注册/登录：JWT 返回 token + user + student 信息，前端存入 Vuex/sessionStorage，路由守卫放行
2. 组卷/练习：教师可在题库选题发布课程测验，学生在 `Exam.vue` 报名或在 `Practice.vue` 自主生成练习，均将试卷配置写入 localStorage
3. 答题：`Answer.vue` 调用题库 API，客观题即时判分；练习模式下写入 `/api/records/...`
4. 批阅：客观题分数即时计算，主观题通过 `/api/upload-subjective/` 上传，教师或 AI 批阅后成绩合并回 `Grade.vue`
5. 复盘：`Record.vue` 拉取 `/api/records/*/` 查看练习详情；`Center.vue` 允许更新学生信息（调用 `/api/students/<id>/`）

## 后续建议
1. 修复 `ExamOnline/exam/serializers.py` 中缺失的 `Subjective` 模型引用，确保主观题待批阅接口可用
2. 阅读 `ExamOnline/*/tests/` 了解接口契约，必要时扩展测试覆盖
3. 如需部署，可参考 `nginx_website_setting.conf` 配置，将前端构建产物托管并反向代理 `/api`
