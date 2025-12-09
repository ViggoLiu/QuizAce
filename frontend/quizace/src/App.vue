<template>
  <div>
    <router-view/>
    <AIFloatBall v-if="isLoggedIn" />
  </div>
</template>

<script>
import AIFloatBall from './components/AIFloatBall.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'App',
  components: {
    AIFloatBall
  },
  computed: {
    ...mapGetters(['isLoggedIn'])
  }
}
</script>

<style>
@import './style/common.scss';
html,body,#app{
  height: 100%;
}

.app-container{
  padding:20px
}
</style>
