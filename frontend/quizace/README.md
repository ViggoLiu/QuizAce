# QuizAce Frontend

QuizAce平台的前端界面，基于Vue 3框架开发。

## 技术栈

- **框架**: Vue 3
- **UI组件库**: Element Plus
- **状态管理**: Vuex
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **样式**: SCSS
- **构建工具**: Vue CLI
- **其他**: 
  - js-cookie (Cookie管理)
  - jsencrypt (数据加密)
  - qs (参数序列化)
  - svg-sprite-loader (SVG图标管理)

## 项目结构

```
frontend/quizace/
├── public/              # 静态资源
│   ├── index.html       # HTML入口
│   └── favicon.ico      # 网站图标
├── src/                 # 源代码
│   ├── assets/          # 资源文件
│   │   ├── icons/       # SVG图标
│   │   ├── images/      # 图片资源
│   │   └── styles/      # 全局样式
│   ├── components/      # 通用组件
│   │   ├── common/      # 基础组件
│   │   └── business/    # 业务组件
│   ├── views/           # 页面视图
│   │   ├── auth/        # 认证相关页面
│   │   ├── student/     # 学生端页面
│   │   ├── teacher/     # 教师端页面
│   │   └── admin/       # 管理员页面
│   ├── router/          # 路由配置
│   │   └── index.js     # 路由定义
│   ├── store/           # 状态管理
│   │   ├── index.js     # Vuex入口
│   │   └── modules/     # 模块状态
│   ├── api/             # API请求
│   │   ├── index.js     # Axios配置
│   │   └── modules/     # API模块
│   ├── utils/           # 工具函数
│   ├── config.js        # 项目配置
│   ├── App.vue          # 根组件
│   └── main.js          # 应用入口
├── package.json         # 项目配置
├── vue.config.js        # Vue CLI配置
├── babel.config.js      # Babel配置
├── jsconfig.json        # JavaScript配置
└── .gitignore           # Git忽略文件
```

## 核心功能模块

### 1. 认证模块 (auth)
- 用户登录/注册
- 忘记密码
- 个人信息管理
- 角色切换

### 2. 学生端功能
- 在线考试
- 练习模式
- 成绩查询
- 学习资源
- 论坛讨论
- 资源评论

### 3. 教师端功能
- 题库管理
- 试卷创建
- 考试管理
- 成绩批阅
- 数据统计
- 论坛管理

### 4. 管理员端功能
- 用户管理
- 系统配置
- 资源管理
- 日志监控
- 论坛管理

### 5. 论坛功能
- 课程论坛讨论
- 评论与回复
- 点赞功能
- 评论管理

## 安装与运行

### 环境要求
- Node.js 14+
- npm 6+

### 安装依赖

```bash
npm install
```

### 开发环境运行

```bash
npm run serve
```

项目将在 `http://localhost:8080` 启动

### 生产环境构建

```bash
npm run build
```

构建产物将输出到 `dist` 目录

## 开发指南

### 1. 组件开发

```vue
<template>
  <div class="custom-component">
    <!-- 组件内容 -->
  </div>
</template>

<script setup>
// 组件逻辑
import { ref, computed } from 'vue'

const props = defineProps({
  // 组件属性
})

const emit = defineEmits([
  // 组件事件
])
</script>

<style lang="scss" scoped>
.custom-component {
  // 组件样式
}
</style>
```

### 2. 页面开发

```vue
<template>
  <div class="page-container">
    <h1>页面标题</h1>
    <!-- 页面内容 -->
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

onMounted(() => {
  // 页面初始化逻辑
})
</script>

<style lang="scss" scoped>
.page-container {
  // 页面样式
}
</style>
```

### 3. API请求

```javascript
// api/modules/user.js
import request from '../index'

export function login(data) {
  return request({
    url: '/api/user/login/',
    method: 'post',
    data
  })
}

export function getProfile() {
  return request({
    url: '/api/user/profile/',
    method: 'get'
  })
}
```

### 4. 路由配置

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout'

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home')
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
```

### 5. 状态管理

```javascript
// store/modules/user.js
const state = {
  userInfo: null,
  token: ''
}

const mutations = {
  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo
  },
  SET_TOKEN(state, token) {
    state.token = token
  }
}

const actions = {
  async login({ commit }, data) {
    const response = await login(data)
    commit('SET_TOKEN', response.data.token)
    commit('SET_USER_INFO', response.data.user)
    return response
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
```

## 代码规范

### 1. 命名规范
- **组件名**: 大驼峰命名，如 `UserProfile.vue`
- **变量名**: 小驼峰命名，如 `userInfo`
- **函数名**: 小驼峰命名，如 `getUserInfo()`
- **常量名**: 全大写，下划线分隔，如 `API_BASE_URL`

### 2. 代码风格
- 使用ES6+语法
- 使用Vue 3 Composition API
- 组件样式使用SCSS，尽量使用scoped
- 代码缩进使用2个空格
- 每行不超过120个字符

### 3. 注释规范
- 组件需要添加说明注释
- 复杂逻辑需要添加注释
- API接口需要添加注释说明

## 配置文件

### vue.config.js

```javascript
module.exports = {
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  configureWebpack: {
    module: {
      rules: [
        {
          test: /\.svg$/,
          loader: 'svg-sprite-loader',
          include: [resolve('src/assets/icons')],
          options: {
            symbolId: 'icon-[name]'
          }
        }
      ]
    }
  }
}
```

### config.js

```javascript
export default {
  API_BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://api.quizace.com' 
    : 'http://localhost:8000/api',
  TIMEOUT: 10000,
  UPLOAD_MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ROLES: {
    STUDENT: 1,
    TEACHER: 2,
    ADMIN: 3
  }
}
```

## 测试

### 单元测试

```bash
# 安装测试依赖
npm install --save-dev @vue/test-utils jest

# 运行测试
npm run test
```

### 端到端测试

```bash
# 安装Cypress
npm install --save-dev cypress

# 运行测试
npx cypress open
```

## 部署

### 开发环境

```bash
npm run serve
```

### 生产环境

1. 构建项目
```bash
npm run build
```

2. 部署到Nginx

```nginx
server {
    listen 80;
    server_name quizace.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 注意事项

- 开发前请确保已安装Node.js和npm
- 请先启动后端服务再运行前端项目
- 接口调用前需要先登录获取token
- 开发环境下API请求会通过代理转发到后端

## 许可证

MIT License
