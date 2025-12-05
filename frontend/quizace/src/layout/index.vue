<template>
	<div id="layout">
		<el-container>
			<el-header>
				<el-row type="flex" justify="space-between">
					<a href="/"><img src="../assets/logo.png" height="50px" /></a>
					<el-menu :default-active="activeIndex" class="el-menu-title" mode="horizontal" @select="handleSelect"
					 background-color="#ffffff" text-color="#85baef" active-text-color="#1884f2" :router="true">
						<!-- 学生菜单 -->
						<template v-if="getUserRole === 'student'">
							<el-menu-item index="/student/exam">考试中心</el-menu-item>
							<el-menu-item index="/student/questions">模拟练习</el-menu-item>
							<el-menu-item index="/student/analysis">学习分析</el-menu-item>
							<el-menu-item index="/student/wrong-book">错题本</el-menu-item>
							<el-menu-item index="/student/resource">学习资源</el-menu-item>
							<el-menu-item index="/forum">论坛</el-menu-item>
						</template>
						
						<!-- 老师菜单 -->
						<template v-else-if="getUserRole === 'teacher'">
							<el-menu-item index="/teacher/questions">题目管理</el-menu-item>
							<el-menu-item index="/teacher/exam-manage">考试发布</el-menu-item>
							<el-menu-item index="/teacher/marking">阅卷管理</el-menu-item>
							<el-menu-item index="/teacher/analysis">教学分析</el-menu-item>
							<el-menu-item index="/forum">论坛</el-menu-item>
						</template>
						
						<!-- 管理员菜单 -->
						<template v-else-if="getUserRole === 'admin'">
							<el-menu-item index="/admin/user-manage">用户管理</el-menu-item>
							<el-menu-item index="/admin/resource-audit">资源审核</el-menu-item>
							<el-menu-item index="/admin/system-analysis">系统分析</el-menu-item>
							<el-menu-item index="/forum">论坛</el-menu-item>
						</template>
					</el-menu>
					<el-dropdown>
						<span class="el-dropdown-link" style="height: 50px;">
							<el-row>
								<!-- <img src="../assets/avatar.png" height="35px" /> -->
								<span>
										<i class="el-icon-user-solid"></i>
										<span>{{getUser ? getUser.username : '未登录'}}</span>
										<span class="user-role">({{getUserRoleLabel}})</span>
										<i class="el-icon-arrow-down el-icon--right"></i>
								</span>
								
							</el-row>
						</span>
						<template #dropdown>
				<el-dropdown-menu>
					<el-dropdown-item @click="toCenter" class="dropdown-item">
						<span class="dropdown-item-content">个人中心</span>
					</el-dropdown-item>
					<el-dropdown-item @click="toMessages" class="dropdown-item">
						<span class="dropdown-item-content">
							消息
							<el-badge v-if="unreadCount > 0" :value="unreadCount" class="message-badge"></el-badge>
						</span>
					</el-dropdown-item>
					<el-dropdown-item @click="toUpdatePwd" class="dropdown-item">
						<span class="dropdown-item-content">修改密码</span>
					</el-dropdown-item>
					<el-dropdown-item divided @click="loginOut" class="dropdown-item">
						<span class="dropdown-item-content">退出登录</span>
					</el-dropdown-item>
				</el-dropdown-menu>
			</template>
					</el-dropdown>
				</el-row>
			</el-header>
			<el-main>
				<router-view />
			</el-main>
			<el-footer>
				<b>@Copyright 2025-Present. ALL Rights Reserved. QuizAce - 高校课程考试在线出题、答题与智能批阅平台</b>
			</el-footer>
		</el-container>
	</div>
</template>

<script>
	export default {
		name: "layout",
		data() {
			return {
				activeIndex: this.$route.path
			};
		},
		computed: {
			getUser() {
				return this.$store.state.user;
			},
			getUserRole() {
				return this.$store.getters.getUserRole;
			},
			getUserRoleLabel() {
				const roleMap = {
					'student': '学生',
					'teacher': '老师',
					'admin': '管理员'
				};
				return roleMap[this.getUserRole] || '';
			}
		},
		methods: {
			handleSelect(key, keyPath) {
				//console.log(key, keyPath);
				this.activeIndex = key
			},
			loginOut() {
				// 使用 Vuex 退出登录
				this.$store.dispatch('logout')
				this.$router.push('/login');
			},
			toCenter() {
				// 跳转到统一的个人中心
				this.$router.push('/profile');
			},
			toMessages() {
				// 跳转到消息页面
				this.$router.push('/notifications');
			},
			toUpdatePwd() {
				// 根据角色跳转到对应的修改密码页面
				if (this.getUserRole === 'student') {
					this.$router.push('/student/update-pwd');
				} else if (this.getUserRole === 'teacher') {
					this.$router.push('/teacher/update-pwd');
				} else if (this.getUserRole === 'admin') {
					this.$router.push('/admin/update-pwd');
				}
			}
		},
		created() {
		// 初始化用户信息（从本地存储获取）
		this.$store.dispatch('initUserInfo')
	}
	}
</script>

<style lang="scss" scoped>
	#layout {
		margin: 0px auto;
		width: 1400px; /* 增加布局宽度 */
		max-width: 95%; /* 响应式设计 */
	}

	.el-header {
		background-color: #ffffff !important;
		border-bottom: solid 1px #e6e6e6 !important;
		padding: 0 20px !important;
	}

	.el-main {
		height: auto;
		min-height: 580px;
		_height: 580px;
		padding: 20px 0 !important;
	}

	.el-footer {
		text-align: center;
		padding: 20px 0 !important;
		background-color: #f5f7fa;
	}

	.el-dropdown img {
		margin-top: 10px;
	}

	.el-menu-title {
		flex: 1;
		justify-content: center;
	}

	.el-menu-item {
		font-size: 16px; /* 减小字体大小 */
		padding: 0 20px !important; /* 调整菜单项间距 */
	}

	.el-dropdown {
		margin-top: 10px;
	}

	.el-dropdown-link {
		cursor: pointer;
		color: #909090;
		font-size: 16px;
	}

	.user-role {
		font-size: 14px;
		color: #1884f2;
		margin-left: 5px;
	}

	.el-icon-arrow-down {
		font-size: 16px;
	}

	.dropdown-item-content {
		width: 100%;
		height: 100%;
		padding: 10px 20px;
		cursor: pointer;
		text-align: left;
		transition: background-color 0.2s;
	}

	.el-dropdown-item {
		padding: 0 !important;
	}

	.el-dropdown-item:hover {
		background-color: rgba(64, 158, 255, 0.1) !important;
	}

	.message-badge {
		margin-left: 5px;
		vertical-align: top;
		min-width: 18px;
		height: 18px;
		line-height: 18px;
		padding: 0 4px;
		font-size: 12px;
	}
</style>
