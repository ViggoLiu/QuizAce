import { createRouter, createWebHistory } from 'vue-router'
import store from '../store' // 导入Vuex store

// 基础路由，所有角色都可以访问
const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue')
  },
  // 主布局路由，包含角色相关的子路由
  {
    path: '/',
    name: 'home',
    component: () => import('../layout/index.vue'),
    meta: { requiresAuth: true }, // 添加路由元信息，表示需要登录
    children: [
      // 欢迎界面
      {
        path: '',
        name: 'welcome',
        component: () => import('../views/Welcome.vue'),
        meta: { requiresAuth: true }
      },
      // 个人中心路由
      {
        path: '/profile',
        name: 'profile',
        component: () => import('../views/PersonalCenter.vue'),
        meta: { requiresAuth: true }
      },
      // 学生路由
      {
        path: '/student/questions',
        name: 'student-questions',
        component: () => import('../views/student/StudentQuestionView.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: '/student/exam',
        name: 'student-exam',
        component: () => import('../views/student/StudentExamView.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: '/student/wrong-book',
        name: 'student-wrong-book',
        component: () => import('../views/student/StudentWrongBookView.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: '/student/resource',
        name: 'student-resource',
        component: () => import('../views/student/StudentResourceView.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: '/student/resource/detail/:id',
        name: 'student-resource-detail',
        component: () => import('../views/student/StudentResourceDetailView.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: '/student/analysis',
        name: 'student-analysis',
        component: () => import('../views/student/StudentAnalysisView.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      // 老师路由
      {
        path: '/teacher/questions',
        name: 'teacher-questions',
        component: () => import('../views/teacher/TeacherQuestionView.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: '/teacher/exam-manage',
        name: 'teacher-exam-manage',
        component: () => import('../views/teacher/TeacherExamManageView.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: '/teacher/marking',
        name: 'teacher-marking',
        component: () => import('../views/teacher/TeacherMarkingView.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: '/teacher/analysis',
        name: 'teacher-analysis',
        component: () => import('../views/teacher/TeacherAnalysisView.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      },
      // 管理员路由
      {
        path: '/admin/user-manage',
        name: 'admin-user-manage',
        component: () => import('../views/admin/AdminUserManageView.vue'),
        meta: { requiresAuth: true, role: 'admin' }
      },
      {
        path: '/admin/resource-audit',
        name: 'admin-resource-audit',
        component: () => import('../views/admin/AdminResourceAuditView.vue'),
        meta: { requiresAuth: true, role: 'admin' }
      },
      {
        path: '/admin/system-analysis',
        name: 'admin-system-analysis',
        component: () => import('../views/admin/AdminSystemAnalysisView.vue'),
        meta: { requiresAuth: true, role: 'admin' }
      }
    ]
  }
]

// src/router/index.js
const router = createRouter({
  history: createWebHistory(), // 去掉#号
  routes
})

// 添加全局路由守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  // 获取用户登录状态和角色
  const isLoggedIn = store.getters.isLoggedIn
  const userRole = store.getters.getUserRole

  if (requiresAuth && !isLoggedIn) {
    // 需要认证但未登录，跳转到登录页
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    // 已登录但访问登录或注册页，跳转到欢迎界面
    next('/')
  } else if (requiresAuth && isLoggedIn) {
    // 已登录且访问需要认证的路由，检查角色权限
    const routeRole = to.meta.role
    if (routeRole && routeRole !== userRole) {
      // 没有权限访问该路由，跳转到欢迎界面
      next('/')
    } else {
      // 有权限，正常跳转
      next()
    }
  } else {
    // 其他情况，正常跳转
    next()
  }
})

export default router
