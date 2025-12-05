<template>
  <div class="notification-container">
    <el-card shadow="hover" class="notification-card">
      <template #header>
        <div class="card-header">
          <h2>消息通知</h2>
          <el-button type="primary" size="small" @click="markAllAsRead" :disabled="notifications.length === 0">
            全部标记为已读
          </el-button>
        </div>
      </template>

      <!-- 消息列表 -->
      <div class="notifications-list">
        <div v-if="notifications.length === 0" class="no-notifications">
          <el-empty description="暂无消息通知" />
        </div>
        <div v-else>
          <el-timeline>
            <el-timeline-item
              v-for="notification in notifications"
              :key="notification.id"
              :timestamp="formatTime(notification.create_time)"
              :type="getNotificationType(notification.type)"
              placement="top"
            >
              <el-card
                :class="['notification-item', { 'unread': !notification.is_read }]"
                shadow="hover"
                @click="markAsRead(notification)"
              >
                <div class="notification-header">
                  <span class="notification-title">{{ getNotificationTitle(notification.type) }}</span>
                  <el-tag
                    :type="notification.is_read ? 'info' : 'success'"
                    size="small"
                    class="read-status"
                  >
                    {{ notification.is_read ? '已读' : '未读' }}
                  </el-tag>
                </div>
                <div class="notification-content">{{ notification.content }}</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { get, post } from '@/util/request.js'
import { ElMessage } from 'element-plus'

export default {
  name: 'NotificationView',
  data() {
    return {
      notifications: []
    };
  },
  mounted() {
    this.loadNotifications();
  },
  methods: {
    async loadNotifications() {
      try {
        const response = await get('/forum/notifications/');
        this.notifications = response.data.results || response.data;
      } catch (error) {
        console.error('加载消息通知失败:', error);
        ElMessage.error('加载消息通知失败，请稍后重试');
      }
    },

    async markAsRead(notification) {
      if (notification.is_read) return;

      try {
        await post(`/forum/notifications/${notification.id}/mark_as_read/`);
        notification.is_read = true;
        // 更新导航栏的未读消息数量
        this.$emit('update:unreadCount', this.notifications.filter(n => !n.is_read).length);
      } catch (error) {
        console.error('标记为已读失败:', error);
        ElMessage.error('标记为已读失败，请稍后重试');
      }
    },

    async markAllAsRead() {
      if (this.notifications.length === 0) return;

      try {
        await post('/forum/notifications/mark_all_as_read/');
        // 更新所有消息为已读
        this.notifications.forEach(notification => {
          notification.is_read = true;
        });
        // 更新导航栏的未读消息数量
        this.$emit('update:unreadCount', 0);
        ElMessage.success('全部标记为已读');
      } catch (error) {
        console.error('全部标记为已读失败:', error);
        ElMessage.error('全部标记为已读失败，请稍后重试');
      }
    },

    getNotificationType(type) {
      switch (type) {
        case 'comment_deleted':
          return 'danger';
        case 'user_banned':
          return 'warning';
        case 'system_notice':
          return 'info';
        default:
          return 'primary';
      }
    },

    getNotificationTitle(type) {
      switch (type) {
        case 'comment_deleted':
          return '评论被删除通知';
        case 'user_banned':
          return '用户禁言通知';
        case 'system_notice':
          return '系统通知';
        default:
          return '通知';
      }
    },

    formatTime(time) {
      const date = new Date(time);
      return date.toLocaleString();
    }
  }
};
</script>

<style scoped>
.notification-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.notification-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notifications-list {
  margin-top: 30px;
}

.no-notifications {
  text-align: center;
  padding: 50px 0;
}

.notification-item {
  cursor: pointer;
  transition: all 0.3s ease;
}

.notification-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.notification-item.unread {
  border-left: 4px solid #409eff;
  background-color: rgba(64, 158, 255, 0.05);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.notification-title {
  font-weight: bold;
  font-size: 16px;
}

.read-status {
  margin-left: 10px;
}

.notification-content {
  color: #606266;
  line-height: 1.6;
}

.el-timeline {
  margin-top: 20px;
}

.el-timeline-item {
  margin-bottom: 20px;
}
</style>
