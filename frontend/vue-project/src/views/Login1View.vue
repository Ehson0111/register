<!-- frontend/src/views/RegisterView.vue -->
<template>
  <!-- <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-lg shadow-sm border border-gray-100 p-6"> -->
    <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-xl shadow-sm p-8 border border-gray-100">
      <Login1Form  />
    </div>
</div>
</template>

<script>
// import Login1Form from '../components/auth/Login1Form.vue'
import Login1Form from '../components/auth/login1Form.vue'

export default {
  name: 'Login1View',
  components: {
    Login1Form 
  }
}
</script>
