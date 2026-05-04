<!-- views/LoginView.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Данные формы
const formData = ref({
  email: '',
  password: '',
  rememberMe: false
})

const isLoading = ref(false)
const errorMessage = ref('')

// Валидация email
const isValidEmail = (email: string) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

// Обработка авторизации
const handleLogin = async () => {
  // Сброс ошибки
  errorMessage.value = ''

  // Валидация
  if (!formData.value.email || !formData.value.password) {
    errorMessage.value = 'Все поля обязательны для заполнения'
    return
  }

  if (!isValidEmail(formData.value.email)) {
    errorMessage.value = 'Введите корректный email адрес'
    return
  }

  // Симуляция запроса к API
  isLoading.value = true
  
  try {
    // Здесь будет реальный запрос к вашему бэкенду
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Симуляция успешной авторизации
    localStorage.setItem('auth_token', 'demo_token')
    
    // Переход на главную страницу CRM
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = 'Ошибка авторизации. Проверьте данные и попробуйте снова.'
  } finally {
    isLoading.value = false
  }
}

// Быстрый вход для демо
const quickDemoLogin = () => {
  formData.value.email = 'demo@company.com'
  formData.value.password = 'demo123'
}
</script>

<template>
  <div class="login-page">
    <!-- Левая часть - форма -->
    <div class="login-form-section">
      <div class="form-container">
        <!-- Логотип -->
        <div class="logo">
          <div class="logo-icon">⚡</div>
          <h1>BusinessCRM</h1>
        </div>

        <!-- Заголовок -->
        <div class="header">
          <h2>С возвращением!</h2>
          <p>Войдите в вашу CRM-систему</p>
        </div>

        <!-- Форма -->
        <form @submit.prevent="handleLogin" class="form">
          <!-- Поле email -->
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              placeholder="your@email.com"
              :disabled="isLoading"
            >
          </div>

          <!-- Поле пароля -->
          <div class="form-group">
            <label for="password">Пароль</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              placeholder="Введите ваш пароль"
              :disabled="isLoading"
            >
          </div>

          <!-- Дополнительные опции -->
          <div class="form-options">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="formData.rememberMe"
                :disabled="isLoading"
              >
              <span class="checkmark"></span>
              Запомнить меня
            </label>
            <a href="#" class="forgot-password">Забыли пароль?</a>
          </div>

          <!-- Сообщение об ошибке -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
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
              Выполняется вход...
            </span>
          </button>

          <!-- Демо вход -->
          <button
            type="button"
            class="demo-button"
            @click="quickDemoLogin"
            :disabled="isLoading"
          >
            Быстрый демо-вход
          </button>
        </form>

        <!-- Футер формы -->
        <div class="form-footer">
          <p>Ещё нет аккаунта? <a href="#">Зарегистрироваться</a></p>
        </div>
      </div>
    </div>

    <!-- Правая часть - баннер -->
    <div class="login-banner">
      <div class="banner-content">
        <!-- Анимированные карточки статистики -->
        <div class="floating-cards">
          <div class="stats-card card-1">
            <div class="card-icon">👥</div>
            <div class="card-content">
              <div class="card-value">+245%</div>
              <div class="card-label">Рост лидов</div>
            </div>
          </div>
          
          <div class="stats-card card-2">
            <div class="card-icon">💰</div>
            <div class="card-content">
              <div class="card-value">98%</div>
              <div class="card-label">Успешных сделок</div>
            </div>
          </div>
          
          <div class="stats-card card-3">
            <div class="card-icon">⏱️</div>
            <div class="card-content">
              <div class="card-value">-60%</div>
              <div class="card-label">Время на задачи</div>
            </div>
          </div>
        </div>

        <!-- Текст баннера -->
        <div class="banner-text">
          <h3>Управляйте бизнесом эффективно</h3>
          <p>Более 500+ малых компаний уже управляют продажами и клиентами с нашей CRM</p>
        </div>

        <!-- Преимущества -->
        <div class="features-list">
          <div class="feature">
            <span class="feature-icon">✅</span>
            <span>Рост продаж</span>
          </div>
          <div class="feature">
            <span class="feature-icon">✅</span>
            <span>Управление клиентами</span>
          </div>
          <div class="feature">
            <span class="feature-icon">✅</span>
            <span>Аналитика в реальном времени</span>
          </div>
          <div class="feature">
            <span class="feature-icon">✅</span>
            <span>Интеграции с популярными сервисами</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  min-height: 100vh;
  background: #ffffff;
}

/* Левая часть - форма */
.login-form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: #ffffff;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

/* Логотип */
.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 3rem;
}

.logo-icon {
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

/* Заголовок */
.header {
  margin-bottom: 2.5rem;
}

.header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}

.header p {
  color: #718096;
  margin: 0;
  font-size: 1rem;
}

/* Форма */
.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #2d3748;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.875rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
  background: #ffffff;
}

.form-group input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.form-group input:disabled {
  background: #f7fafc;
  cursor: not-allowed;
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

.checkbox-label input {
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

.checkbox-label input:checked + .checkmark {
  background: #4299e1;
  border-color: #4299e1;
}

.checkbox-label input:checked + .checkmark::after {
  content: '✓';
  color: white;
  font-size: 12px;
}

.forgot-password {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

/* Сообщение об ошибке */
.error-message {
  background: #fed7d7;
  color: #c53030;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  border: 1px solid #feb2b2;
}

/* Кнопки */
.login-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.login-button.loading {
  cursor: wait;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.demo-button {
  background: transparent;
  color: #667eea;
  border: 2px solid #cbd5e0;
  padding: 0.875rem 2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.demo-button:hover:not(:disabled) {
  border-color: #667eea;
  background: #f7fafc;
}

/* Футер формы */
.form-footer {
  text-align: center;
  margin-top: 2rem;
  color: #718096;
  font-size: 0.875rem;
}

.form-footer a {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}

/* Правая часть - баннер */
.login-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.banner-content {
  color: white;
  text-align: center;
  max-width: 500px;
  position: relative;
  z-index: 2;
}

/* Плавающие карточки */
.floating-cards {
  position: relative;
  height: 200px;
  margin-bottom: 3rem;
}

.stats-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 160px;
  animation: float 6s ease-in-out infinite;
}

.card-1 {
  top: 0;
  left: 0;
  animation-delay: 0s;
}

.card-2 {
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  animation-delay: 2s;
}

.card-3 {
  bottom: 0;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.card-icon {
  font-size: 1.5rem;
}

.card-content {
  text-align: left;
}

.card-value {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.card-label {
  font-size: 0.8rem;
  opacity: 0.9;
}

/* Текст баннера */
.banner-text {
  margin-bottom: 2.5rem;
}

.banner-text h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  line-height: 1.2;
}

.banner-text p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
  line-height: 1.5;
}

/* Список преимуществ */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
  justify-content: center;
}

.feature-icon {
  font-size: 1.1rem;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .login-page {
    grid-template-columns: 1fr;
  }
  
  .login-banner {
    display: none;
  }
}

@media (max-width: 768px) {
  .login-form-section {
    padding: 1rem;
  }
  
  .header h2 {
    font-size: 1.75rem;
  }
  
  .form-options {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .logo {
    justify-content: center;
    margin-bottom: 2rem;
  }
  
  .header {
    text-align: center;
    margin-bottom: 2rem;
  }
}
</style>