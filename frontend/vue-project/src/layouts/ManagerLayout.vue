<!-- frontend/src/layouts/ManagerLayout.vue -->
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <div class="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div
          class="flex items-center justify-center h-16 border-b border-gray-200"
        >
          <div class="flex items-center space-x-2">
            <div
              class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center"
            >
              <span class="text-white font-bold text-sm">CRM</span>
            </div>
            <span class="text-xl font-bold text-gray-800">BusinessCRM</span>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-4 py-6 space-y-2">
          <router-link
            to="/manager/dashboard" 
          
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('dashboard'),
            }"
          >
            <HomeIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Дашборд</span>
          </router-link>

          <router-link
            to="/manager/contacts"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('contacts'),
            }"
          >
            <UsersIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Контакты</span>
          </router-link>

          <router-link
            to="/manager/deals"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('deals'),
            }"
          >
            <BriefcaseIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Сделки</span>
          </router-link>

          <router-link
            to="/manager/services"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('services'),
            }"
          >
            <CogIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Услуги</span>
          </router-link>

          <router-link
            to="/manager/calendar"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('calendar'),
            }"
          >
            <CalendarIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Календарь</span>
          </router-link>

          <router-link
            to="/manager/analytics"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('analytics'),
            }"
          >
            <ChartBarIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Аналитика</span>
          </router-link>

          <router-link
            to="/manager/marketing"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('marketing'),
            }"
          >
            <MegaphoneIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Маркетинг</span>
          </router-link>

          <router-link
            to="/manager/documents"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
            :class="{
              'bg-blue-50 text-blue-600': $route.path.includes('documents'),
            }"
          >
            <DocumentTextIcon class="w-5 h-5 mr-3" />
            <span class="font-medium">Документы</span>
          </router-link>
        </nav>

        <!-- User Menu -->
        <div class="p-4 border-t border-gray-200">
          <router-link
            to="/manager/profile"
            class="flex items-center space-x-3 hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors"
          >
            <div
              class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center"
            >
              <span class="text-blue-600 text-sm font-medium">
                {{ userInitials }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ authStore.userName }}
              </p>
              <p class="text-sm text-gray-500 truncate">Менеджер</p>
            </div>
          </router-link>
          <div class="flex justify-end mt-2">
            <button
              @click="handleLogout"
              class="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="Выйти"
            >
              <ArrowRightOnRectangleIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="pl-64">
      <!-- Header -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="px-8 py-4">
          <h1 class="text-2xl font-semibold text-gray-900">
            {{ currentPageTitle }}
          </h1>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-8">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";

// В ManagerLayout.vue обновляем импорты:
import {
  HomeIcon,
  UsersIcon,
  BriefcaseIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  CalendarIcon,
  ChartBarIcon,
  MegaphoneIcon,
  DocumentTextIcon,
  UserCircleIcon
} from '@heroicons/vue/24/outline'
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

//: Чтобы в шапке страницы писать не ManagerDeals, а нормальное «Сделки».
const currentPageTitle = computed(() => {
  const routeName = route.name as string;
  const titles: Record<string, string> = {
    ManagerDashboard: "Дашборд",
    ManagerContacts: "Контакты",
    ContactDetail: "Детали контакта",
    ManagerDeals: "Сделки",
    NewDeal: "Новая сделка",
    DealDetail: "Детали сделки",
    ManagerServices: "Услуги",
    ManagerCalendar: "Календарь",
    ManagerAnalytics: "Аналитика",
    ManagerMarketing: "Маркетинг",
    ManagerDocuments: "Документы",
    ManagerProfile: "Профиль",
  };
  return titles[routeName] || "Панель управления";
});

const userInitials = computed(() => {
  const name = authStore.userName || "Менеджер";
  return name
    .split(" ")
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase()
    .slice(0, 2);
});

const handleLogout = async () => {
  await authStore.logout();
  router.push("/login");
};
</script>