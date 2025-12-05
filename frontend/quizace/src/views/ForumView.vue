<template>
  <div class="forum-container">
    <el-card shadow="hover" class="forum-card">
      <template #header>
        <div class="card-header">
          <h2>论坛讨论</h2>
        </div>
      </template>

      <!-- 发表评论区域 -->
      <el-form label-position="top" class="comment-form">
        <el-form-item label="发表评论">
          <el-input
            type="textarea"
            v-model="commentForm.content"
            :rows="4"
            placeholder="写下你的想法..."
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitComment" :loading="submitting">发表评论</el-button>
        </el-form-item>
      </el-form>

      <!-- 评论列表 -->
      <div class="comments-list">
        <h3>最新评论</h3>
        <div v-if="comments.length === 0" class="no-comments">
          <el-empty description="暂无评论，快来发表第一条评论吧！" />
        </div>
        <div v-else>
          <el-card
            v-for="comment in comments"
            :key="comment.id"
            shadow="hover"
            class="comment-item"
          >
            <div class="comment-header">
              <div class="user-info">
                <el-avatar :src="getAvatarUrl(comment.user.avatar)" :size="40" />
                <div class="user-details">
                  <div class="username">{{ comment.user.username }}</div>
                  <div class="role">{{ comment.user.role === 'student' ? '学生' : comment.user.role === 'teacher' ? '老师' : '管理员' }}</div>
                </div>
              </div>
              <div class="comment-time">{{ formatTime(comment.create_time) }}</div>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
            <div class="comment-actions">
              <el-button
                type="text"
                @click="toggleLike(comment)"
                :icon="comment.is_liked ? 'el-icon-thumb' : 'el-icon-thumb'"
                :class="comment.is_liked ? 'liked' : ''"
              >
                {{ comment.is_liked ? '已点赞' : '点赞' }} ({{ comment.like_count }})
              </el-button>
              <el-button type="text" @click="showReplyDialog(comment)">
                回复 ({{ comment.reply_count }})
              </el-button>
              <el-button type="text" @click="viewReplies(comment)">
                查看回复
              </el-button>
              <!-- 管理员功能 -->
              <template v-if="$store.getters.getUserRole === 'admin'">
                <el-button type="text" danger @click="deleteComment(comment)">
                  删除
                </el-button>
              </template>
            </div>

            <!-- 回复列表 -->
            <div v-if="comment.showReplies && comment.replies.length > 0" class="replies-list">
              <div
                v-for="reply in comment.replies"
                :key="reply.id"
                class="reply-item"
              >
                <div class="reply-header">
                  <el-avatar :src="getAvatarUrl(reply.user.avatar)" :size="30" />
                  <div class="reply-content-wrapper">
                    <div class="reply-user-info">
                      <span class="reply-username">{{ reply.user.username }}</span>
                      <span class="reply-to">回复</span>
                      <span class="reply-to-username">{{ reply.to_user.username }}</span>
                      <span class="reply-time">{{ formatTime(reply.create_time) }}</span>
                    </div>
                    <div class="reply-content">{{ reply.content }}</div>
                  </div>
                </div>
                <div class="reply-actions">
                  <el-button type="text" size="small" @click="showReplyDialog(comment, reply)">
                    回复
                  </el-button>
                  <!-- 管理员功能 -->
                      <template v-if="$store.getters.getUserRole === 'admin'">
                        <el-button type="text" size="small" danger @click="deleteReply(reply, comment)">
                          删除
                        </el-button>
                      </template>
                </div>


              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- 回复对话框 -->
    <el-dialog
      v-model="replyDialogVisible"
      title="回复评论"
      width="50%"
    >
      <el-form ref="replyForm" :model="replyForm" label-position="top">
        <el-form-item label="回复内容">
          <el-input
            type="textarea"
            v-model="replyForm.content"
            :rows="3"
            placeholder="写下你的回复..."
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="replyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitReply" :loading="submittingReply">
            提交回复
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post, del } from '@/util/request.js'

export default {
  name: 'ForumView',
  data() {
    return {
      commentForm: {
        content: ''
      },
      replyForm: {
        content: ''
      },
      comments: [],
      submitting: false,
      submittingReply: false,
      replyDialogVisible: false,
      currentComment: null,
      currentReply: null
    };
  },
  mounted() {
    this.loadComments();
  },
  methods: {
    async loadComments() {
      try {
        const response = await get('/forum/forum/comments/');
        this.comments = response.data.results || response.data;
        // 为每个评论添加showReplies属性
        this.comments.forEach(comment => {
          comment.showReplies = false;
        });
      } catch (error) {
        console.error('加载评论失败:', error);
        ElMessage.error('加载评论失败，请稍后重试');
      }
    },

    async submitComment() {
      if (!this.commentForm.content.trim()) {
        ElMessage.warning('评论内容不能为空');
        return;
      }

      this.submitting = true;
      try {
        const response = await post('/forum/forum/comments/', {
          content: this.commentForm.content
        });
        this.comments.unshift(response.data);
        this.comments[0].showReplies = false;
        this.commentForm.content = '';
        ElMessage.success('评论发表成功');
      } catch (error) {
        console.error('发表评论失败:', error);
        ElMessage.error('发表评论失败，请稍后重试');
      } finally {
        this.submitting = false;
      }
    },

    async toggleLike(comment) {
      try {
        const response = await post(`/forum/forum/comments/${comment.id}/like/`);
        comment.is_liked = !comment.is_liked;
        comment.like_count = response.data.like_count;
      } catch (error) {
        console.error('点赞失败:', error);
        ElMessage.error('点赞失败，请稍后重试');
      }
    },

    showReplyDialog(comment, reply = null) {
      this.currentComment = comment;
      this.currentReply = reply;
      this.replyForm.content = '';
      this.replyDialogVisible = true;
    },

    async submitReply() {
      if (!this.replyForm.content.trim()) {
        ElMessage.warning('回复内容不能为空');
        return;
      }

      this.submittingReply = true;
      let data = {};
      try {
        // 确保currentComment存在
        if (!this.currentComment) {
          throw new Error('当前评论不存在');
        }
        
        // 确定回复目标用户ID
        let toUserId = this.currentComment.user.id;
        if (this.currentReply && this.currentReply.user) {
          toUserId = this.currentReply.user.id;
        }
        
        data = {
          content: this.replyForm.content,
          to_user_id: toUserId // 改为使用to_user_id字段名，确保与后端API匹配
        };

        // 不再设置parent_reply，所有回复都作为一级回复处理
        // 这样所有回复都会显示在同一层级

        const response = await post(`/forum/forum/comments/${this.currentComment.id}/reply/`, data);
        
        // 更新评论的回复数
        this.currentComment.reply_count++;
        
        // 所有回复都作为一级回复添加到评论的回复列表
        this.currentComment.replies.push(response.data);
        
        this.replyDialogVisible = false;
        ElMessage.success('回复成功');
      } catch (error) {
        console.error('回复失败:', error);
        console.error('回复数据:', data);
        console.error('当前评论:', this.currentComment);
        console.error('当前回复:', this.currentReply);
        ElMessage.error('回复失败，请稍后重试');
      } finally {
        this.submittingReply = false;
      }
    },

    viewReplies(comment) {
      comment.showReplies = !comment.showReplies;
    },

    async deleteComment(comment) {
      // 提供删除原因选择
      ElMessageBox.prompt('请选择删除原因', '删除评论', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'select',
        inputOptions: [
          { label: '违规内容', value: '违规内容' },
          { label: '垃圾广告', value: '垃圾广告' },
          { label: '恶意攻击', value: '恶意攻击' },
          { label: '其他原因', value: '其他原因' }
        ],
        type: 'warning'
      }).then(async (action) => {
        const deletedReason = action.value;
        try {
          // 使用POST方法删除评论（根据后端API要求调整）
          await post(`/forum/forum/comments/${comment.id}/delete_comment/`, {
            deleted_reason: deletedReason
          });
          this.comments = this.comments.filter(c => c.id !== comment.id);
          ElMessage.success('评论删除成功');
        } catch (error) {
          console.error('删除评论失败:', error);
          ElMessage.error('删除评论失败，请稍后重试');
        }
      }).catch(() => {
        ElMessage.info('已取消删除');
      });
    },

    async deleteReply(reply, comment) {
      // 提供删除原因选择
      ElMessageBox.prompt('请选择删除原因', '删除回复', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'select',
        inputOptions: [
          { label: '违规内容', value: '违规内容' },
          { label: '垃圾广告', value: '垃圾广告' },
          { label: '恶意攻击', value: '恶意攻击' },
          { label: '其他原因', value: '其他原因' }
        ],
        type: 'warning'
      }).then(async (action) => {
        const deletedReason = action.value;
        try {
          // 调用后端API删除回复
          await post(`/forum/forum/comments/${comment.id}/delete_reply/`, {
            reply_id: reply.id,
            deleted_reason: deletedReason
          });
          // 更新回复数
          comment.reply_count--;
          // 从列表中移除回复（所有回复都是一级回复）
          const replyIndex = comment.replies.findIndex(r => r.id === reply.id);
          if (replyIndex > -1) {
            comment.replies.splice(replyIndex, 1);
          }
          ElMessage.success('回复删除成功');
        } catch (error) {
          console.error('删除回复失败:', error);
          ElMessage.error('删除回复失败，请稍后重试');
        }
      }).catch(() => {
        ElMessage.info('已取消删除');
      });
    },

    formatTime(time) {
      const date = new Date(time);
      return date.toLocaleString();
    },

    getAvatarUrl(avatar) {
      if (!avatar) {
        return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
      }
      // 如果头像URL已经是完整的URL，直接返回
      if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
        return avatar;
      }
      // 如果是相对路径，拼接完整的URL
      return `http://localhost:8000${avatar}`;
    }
  }
};
</script>

<style scoped>
.forum-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.forum-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-form {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.comments-list {
  margin-top: 30px;
}

.comments-list h3 {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: bold;
}

.no-comments {
  text-align: center;
  padding: 50px 0;
}

.comment-item {
  margin-bottom: 20px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-details {
  margin-left: 15px;
}

.username {
  font-weight: bold;
  margin-bottom: 5px;
}

.role {
  font-size: 12px;
  color: #1884f2;
}

.comment-time {
  font-size: 12px;
  color: #909090;
}

.comment-content {
  margin-bottom: 15px;
  line-height: 1.6;
}

.comment-actions {
  display: flex;
  gap: 15px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.liked {
  color: #f56c6c;
}

.replies-list {
  margin-top: 20px;
  padding-left: 50px;
}

.reply-item {
  margin-bottom: 15px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
}

.reply-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.reply-content-wrapper {
  flex: 1;
}

.reply-user-info {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 5px;
}

.reply-username {
  font-weight: bold;
  font-size: 14px;
}

.reply-to {
  font-size: 12px;
  color: #909090;
}

.reply-to-username {
  font-weight: bold;
  font-size: 14px;
  color: #1884f2;
}

.reply-time {
  font-size: 12px;
  color: #909090;
  margin-left: 10px;
}

.reply-content {
  font-size: 14px;
  line-height: 1.5;
}

.reply-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.child-replies {
  margin-left: 40px;
  margin-top: 15px;
}

.child-reply-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 6px;
}
</style>
