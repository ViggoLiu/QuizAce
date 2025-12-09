<template>
  <el-dialog
    title="题目图片与答案设置"
    :model-value="visible"
    width="520px"
    @close="handleClose"
    @update:modelValue="handleClose"
  >
    
    <el-form :model="form" label-width="100px">
      <el-form-item label="题干图片">
        <el-upload
          class="upload-demo"
          action=""
          :auto-upload="false"
          :show-file-list="true"
          :on-change="handleFileChange"
        >
          <el-button type="primary">选择图片</el-button>
        </el-upload>
      </el-form-item>
      
      <!-- 明确的条件渲染：客观题 -->
      <el-form-item v-if="questionType === 'objective'" label="正确答案">
        <div style="margin-bottom:8px;">
          <span style="margin-right:8px;">请选择正确选项的序号：</span>
          <el-select v-model="form.answer" placeholder="选择正确选项" style="width:120px;">
            <el-option v-for="idx in 4" :key="idx" :label="String.fromCharCode(65 + idx - 1)" :value="idx - 1" />
          </el-select>
        </div>
        <div style="color:#606266;font-size:14px;margin-top:8px;">
          提示：选项顺序与图片中保持一致（A/B/C/D）
        </div>
      </el-form-item>
      
      <!-- 明确的条件渲染：主观题 -->
      <el-form-item v-else label="设置参考答案">
        <el-input type="textarea" v-model="form.answer" placeholder="请输入参考答案" :rows="4" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fileUpload, post } from '@/util/request.js'
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  questionType: {
    type: String,
    default: 'objective'
  },
  course: {
    type: String,
    default: ''
  }
})
// 解构props以便在模板和脚本中直接使用
const { questionType, course } = props
const emit = defineEmits(['close', 'submit'])
const form = reactive({  image: null,  answer: ''})
// 监听visible变化，初始化表单
watch(() => props.visible, v => {
  if (v) {
    form.image = null
    form.answer = ''
  }
})
const handleFileChange = (file) => {
  form.image = file.raw
}
// 客观题不再需要添加选项功能
const handleClose = () => {
  emit('close')
}
const handleSubmit = async () => {
  if (!form.image) {
    ElMessage.error('请选择题干图片');
    return;
  }
  
  try {
    // 先上传图片获取URL
      const imageFormData = new FormData();
      imageFormData.append('image', form.image);
      imageFormData.append('subject', props.course); // 添加科目信息
      const uploadResponse = await fileUpload('/exam/teacher/questions/image-upload/', imageFormData);
      
      if (uploadResponse.data && uploadResponse.data.data && uploadResponse.data.data.image_url) {
        // 准备题目数据
        const questionData = {
          question_type: props.questionType,
          subject: props.course, // 后端期望的字段名是subject
          content: '', // 题目内容为空，因为使用图片展示
          media_url: uploadResponse.data.data.image_url
        };
      
      // 根据题目类型处理答案
      if (props.questionType === 'objective') {
        // 客观题：转换答案格式（数字索引转字母A/B/C/D）
        const correctAnswer = String.fromCharCode(65 + Number(form.answer));
        questionData.answer = correctAnswer;
      } else {
        // 主观题：直接使用答案
        questionData.answer = form.answer;
      }
      
      // 调用创建题目API
      const createResponse = await post('/exam/teacher/questions/create/', questionData);
      
      if (createResponse.data.code === 201) {
        ElMessage.success('题目上传成功');
        emit('close');
        emit('submit', {
          course: course,
          questionType: questionType,
          image: form.image,
          answer: form.answer
        });
      } else {
        ElMessage.error(createResponse.data.info || '题目创建失败');
      }
    } else {
      ElMessage.error('图片上传失败');
    }
  } catch (err) {
    console.error('上传题目出错:', err);
    ElMessage.error('网络请求失败，请稍后重试');
  }
}
</script>

<style scoped>
.upload-demo {
  margin-bottom: 12px;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
