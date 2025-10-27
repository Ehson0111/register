<template>
  <div style="min-height: 100vh; padding: 2rem; background: #f7fafc;">
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <h1 style="color: #2d3748; margin-bottom: 1rem;">Главная панель</h1>
      <p style="color: #718096;">Добро пожаловать в вашу CRM систему!</p>
      <button 
        @click="handleLogout"
        style="margin-top: 2rem; padding: 0.5rem 1rem; background: #e53e3e; color: white; border: none; border-radius: 6px; cursor: pointer;"
      >
        Выйти
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('isAuthenticated')
  router.push('/login')
}
</script>