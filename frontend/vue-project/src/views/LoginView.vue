<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Логотип и заголовок -->
      <div class="logo-section">
        <div class="logo">🚀</div>
        <h1 class="title">BusinessCRM</h1>
        <p class="subtitle">Войдите в вашу учетную запись</p>
      </div>

      <!-- Форма авторизации -->
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Поле email -->
        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            class="form-input"
            :class="{ 'error': errors.email }"
            placeholder="your@email.com"
            required
          >
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <!-- Поле пароля -->
        <div class="form-group">
          <label for="password" class="form-label">Пароль</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            class="form-input"
            :class="{ 'error': errors.password }"
            placeholder="Введите ваш пароль"
            required
          >
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <!-- Дополнительные опции -->
        <div class="form-options">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="formData.rememberMe"
              class="checkbox"
            >
            <span class="checkmark"></span>
            Запомнить меня
          </label>
          <a href="#" class="forgot-link">Забыли пароль?</a>
        </div>

        <!-- Кнопка входа -->
        <button
          type="submit"
          class="login-button"
          :class="{ 'loading': isLoading }"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">Войти в систему</span>
          <span v-else class="loading-text">
            <div class="spinner"></div>
            Вход...
          </span>
        </button>
      </form>

      <!-- Демо данные -->
      <div class="demo-section">
        <p class="demo-title">Демо доступ:</p>
        <div class="demo-accounts">
          <div class="demo-account" @click="fillDemoData('admin')">
            <span class="demo-role">Администратор</span>
            
            <span class="demo-credentials">admin@crm.ru / admin123</span>
          </div>
          <div class="demo-account" @click="fillDemoData('manager')">
            <span class="demo-role">Менеджер</span>
            <span class="demo-credentials">manager@crm.ru / manager123</span>
          </div>
        </div>
      </div>

      <!-- Футер -->
      <div class="footer">
        <p>Нет аккаунта? <a href="#" class="register-link">Зарегистрироваться</a></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Данные формы
const formData = reactive({
  email: '',
  password: '',
  rememberMe: false
})

// Состояние загрузки и ошибки
const isLoading = ref(false)
const errors = reactive({
  email: '',
  password: ''
})

// Демо аккаунты
const demoAccounts = {
  admin: {
    email: 'admin@crm.ru',
    password: 'admin123'
  },
  manager: {
    email: 'manager@crm.ru',
    password: 'manager123'
  }
}

// Валидация email
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Валидация формы
const validateForm = (): boolean => {
  let isValid = true

  // Сброс ошибок
  errors.email = ''
  errors.password = ''

  // Валидация email
  if (!formData.email) {
    errors.email = 'Email обязателен для заполнения'
    isValid = false
  } else if (!validateEmail(formData.email)) {
    errors.email = 'Введите корректный email адрес'
    isValid = false
  }

  // Валидация пароля
  if (!formData.password) {
    errors.password = 'Пароль обязателен для заполнения'
    isValid = false
  } else if (formData.password.length < 6) {
    errors.password = 'Пароль должен содержать минимум 6 символов'
    isValid = false
  }

  return isValid
}

// Заполнение демо данных
const fillDemoData = (role: keyof typeof demoAccounts) => {
  formData.email = demoAccounts[role].email
  formData.password = demoAccounts[role].password
}

// Обработка авторизации
const handleLogin = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    // Симуляция запроса к API
    await new Promise(resolve => setTimeout(resolve, 1500))

    // Проверка демо данных
    const isAdmin = formData.email === demoAccounts.admin.email && 
                   formData.password === demoAccounts.admin.password
    const isManager = formData.email === demoAccounts.manager.email && 
                     formData.password === demoAccounts.manager.password

    if (isAdmin || isManager) {
      // Сохраняем данные авторизации
      localStorage.setItem('isAuthenticated', 'true')
      localStorage.setItem('userEmail', formData.email)
      localStorage.setItem('userRole', isAdmin ? 'admin' : 'manager')
      
      if (formData.rememberMe) {
        localStorage.setItem('rememberMe', 'true')
      }

      // Переход на главную страницу
      router.push('/dashboard')
    } else {
      errors.password = 'Неверный email или пароль'
    }
  } catch (error) {
    errors.password = 'Ошибка при входе. Попробуйте еще раз.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 440px;
}

/* Логотип и заголовок */
.logo-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #718096;
  font-size: 1rem;
  margin: 0;
}

/* Форма */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: #2d3748;
  font-size: 0.9rem;
}

.form-input {
  padding: 0.875rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
  background: #ffffff;
}

.form-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.form-input.error {
  border-color: #e53e3e;
}

.error-message {
  color: #e53e3e;
  font-size: 0.8rem;
  font-weight: 500;
}

/* Опции формы */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #4a5568;
}

.checkbox {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e0;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.checkbox:checked + .checkmark {
  background: #4299e1;
  border-color: #4299e1;
}

.checkbox:checked + .checkmark::after {
  content: '✓';
  color: white;
  font-size: 12px;
}

.forgot-link {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

/* Кнопка входа */
.login-button {
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 52px;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4);
}

.login-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Демо секция */
.demo-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.demo-title {
  color: #718096;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  text-align: center;
}

.demo-accounts {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.demo-account {
  background: #f7fafc;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.demo-account:hover {
  background: #edf2f7;
  transform: translateX(4px);
}

.demo-role {
  font-weight: 600;
  color: #2d3748;
  font-size: 0.9rem;
}

.demo-credentials {
  color: #718096;
  font-size: 0.8rem;
  font-family: monospace;
}

/* Футер */
.footer {
  text-align: center;
  margin-top: 2rem;
  color: #718096;
  font-size: 0.875rem;
}

.register-link {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

/* Адаптивность */
@media (max-width: 480px) {
  .login-card {
    padding: 2rem 1.5rem;
  }
  
  .form-options {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .logo {
    font-size: 2.5rem;
  }
  
  .title {
    font-size: 1.5rem;
  }
}
</style>