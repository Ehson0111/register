<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-xl shadow-sm p-8 border border-gray-100">
      <h2 class="text-2xl font-bold text-black mb-2">Forgot password</h2>
      <p class="text-gray-500 text-sm mb-6">
        We will send a 6-digit code to your email.
      </p>

      <form v-if="step === 'request'" @submit.prevent="requestCode" class="space-y-5">
        <BaseInput
          v-model="email"
          type="email"
          label="Email Address"
          placeholder="Enter your email"
          :error="errors.email"
          :required="true"
        />

        <div v-if="errors.general" class="p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-red-600 text-sm">{{ errors.general }}</p>
        </div>

        <BaseButton type="submit" variant="primary" size="lg" :loading="loading" block class="bg-black text-white">
          Send code
        </BaseButton>

        <div class="text-center text-sm">
          <router-link to="/login" class="text-black hover:text-gray-700 font-medium">
            Back to login
          </router-link>
        </div>
      </form>

      <form v-else @submit.prevent="confirmReset" class="space-y-5">
        <BaseInput v-model="code" type="text" label="Code" placeholder="6-digit code" :required="true" />
        <BaseInput
          v-model="newPassword"
          :type="showPassword ? 'text' : 'password'"
          label="New password"
          placeholder="New password"
          :required="true"
        />
        <BaseInput
          v-model="newPasswordConfirm"
          :type="showPassword ? 'text' : 'password'"
          label="Confirm new password"
          placeholder="Confirm new password"
          :required="true"
        />

        <label class="flex items-center text-sm text-gray-600">
          <input type="checkbox" v-model="showPassword" class="h-4 w-4 text-black focus:ring-black border-gray-300 rounded" />
          <span class="ml-2">Show password</span>
        </label>

        <div v-if="errors.general" class="p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-red-600 text-sm">{{ errors.general }}</p>
        </div>

        <BaseButton type="submit" variant="primary" size="lg" :loading="loading" block class="bg-black text-white">
          Reset password
        </BaseButton>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import authService from '@/services/auth.js'

const router = useRouter()
const step = ref('request') // request | confirm
const email = ref('')
const code = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errors = ref({})

async function requestCode() {
  errors.value = {}
  if (!email.value) {
    errors.value.email = 'Email is required'
    return
  }
  loading.value = true
  try {
    await authService.passwordResetRequest(email.value)
    step.value = 'confirm'
  } catch (e) {
    errors.value.general = e.response?.data?.error || 'Failed to send code'
  } finally {
    loading.value = false
  }
}

async function confirmReset() {
  errors.value = {}
  if (!code.value || !newPassword.value || !newPasswordConfirm.value) {
    errors.value.general = 'Fill all fields'
    return
  }
  if (newPassword.value !== newPasswordConfirm.value) {
    errors.value.general = 'Passwords do not match'
    return
  }
  loading.value = true
  try {
    await authService.passwordResetConfirm({
      email: email.value,
      code: code.value,
      new_password: newPassword.value,
      new_password_confirm: newPasswordConfirm.value
    })
    router.push('/login')
  } catch (e) {
    errors.value.general = e.response?.data?.error || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}
</script>

