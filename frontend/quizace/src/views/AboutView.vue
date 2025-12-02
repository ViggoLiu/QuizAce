<template>
  
      <el-button type="primary" @click="handLogin">测试登录</el-button>
      <el-button type="success" @click="handGetUserList">测试获取用户信息列表</el-button>
     
</template>

<script  setup>
import request from '@/util/request'

const handLogin = async () => {
  try {
    let result = await request.get('user/jwt_test')
    let data = result.data
    if (data.code === 200) {
      const token = data.token
      console.log("登录成功,token:" + token)
      window.sessionStorage.setItem('token', token)
    } else {
      console.log("登录失败, code:", data.code, "info:", data.info)
    }
  } catch (err) {
    console.error('调用 /user/jwt_test 接口失败:', err.response?.status, err.response?.data || err)
  }
}


const handGetUserList =async()=>{
  let result = await request.get('user/test')
  let data=result.data
  if(data.code===200){
    const userList =data.data
    console.log("用户信息列表"+userList)
  }else{
    console.log("获取用户信息列表失败,错误信息:")
  }
}
</script>
