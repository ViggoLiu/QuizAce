import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null, // 用户信息
    token: null // 认证令牌
  },
  getters: {
    getUser: state => state.user,
    getToken: state => state.token,
    isLoggedIn: state => !!state.token,
    getUserRole: state => state.user ? state.user.role : null
  },
  mutations: {
    // 设置用户信息
    setUser(state, user) {
      state.user = user
    },
    // 设置令牌
    setToken(state, token) {
      state.token = token
    },
    // 清除用户信息和令牌（退出登录）
    clearUserInfo(state) {
      state.user = null
      state.token = null
    }
  },
  actions: {
    // 初始化用户信息（从本地存储获取）
    initUserInfo({ commit }) {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('currentUser')
      
      if (token) {
        commit('setToken', token)
      }
      
      if (user) {
        commit('setUser', JSON.parse(user))
      }
    },
    // 登录成功后保存用户信息
    loginSuccess({ commit }, { token, user }) {
      commit('setToken', token)
      commit('setUser', user)
      
      // 同时保存到 localStorage 实现持久化
      localStorage.setItem('token', token)
      localStorage.setItem('currentUser', JSON.stringify(user))
    },
    // 退出登录
    logout({ commit }) {
      commit('clearUserInfo')
      
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
      localStorage.clear()
    }
  },
  modules: {
  }
})
