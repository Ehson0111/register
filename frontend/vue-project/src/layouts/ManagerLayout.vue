<template>
  <div
    class="relative min-h-screen overflow-hidden"
    :style="{
      backgroundImage: `url('${backgroundImageUrl}')`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed',
    }"
  >
    <div class="absolute inset-0 bg-gradient-to-br from-slate-950/70 via-slate-900/62 to-blue-950/55"></div>
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.22),transparent_45%)]"></div>

    <div class="relative z-10 min-h-screen">
      <aside
        class="group/sidebar fixed inset-y-0 left-0 w-20 hover:w-64 transition-all duration-300 bg-slate-900/62 backdrop-blur-xl shadow-2xl border-r border-white/20 overflow-hidden z-20"
      >
        <div class="flex flex-col h-full">
          <div class="flex items-center h-16 border-b border-white/20 px-4">
            <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
              <span class="text-white font-bold text-sm">CRM</span>
            </div>
            <span class="logo-label ml-3 text-lg font-semibold text-white whitespace-nowrap">BusinessCRM</span>
          </div>

          <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            <router-link
              to="/manager/dashboard"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('dashboard') }"
            >
              <HomeIcon class="menu-icon" />
              <span class="menu-label">Главная</span>
            </router-link>

            <router-link
              to="/manager/contacts"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('contacts') }"
            >
              <UsersIcon class="menu-icon" />
              <span class="menu-label">Контакты</span>
            </router-link>

            <router-link
              to="/manager/deals"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('/manager/deals') && !$route.path.includes('/manager/deals-kanban') }"
            >
              <BriefcaseIcon class="menu-icon" />
              <span class="menu-label">Сделки</span>
            </router-link>

            <router-link
              to="/manager/deals-kanban"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('/manager/deals-kanban') }"
            >
              <Squares2X2Icon class="menu-icon" />
              <span class="menu-label">Канбан сделок</span>
            </router-link>

            <router-link
              to="/manager/services"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('services') }"
            >
              <CogIcon class="menu-icon" />
              <span class="menu-label">Услуги</span>
            </router-link>

            <router-link
              to="/manager/calendar"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('calendar') }"
            >
              <CalendarIcon class="menu-icon" />
              <span class="menu-label">Календарь</span>
            </router-link>

            <router-link
              to="/manager/analytics"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('analytics') }"
            >
              <ChartBarIcon class="menu-icon" />
              <span class="menu-label">Аналитика</span>
            </router-link>

            <router-link
              to="/manager/marketing"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('marketing') }"
            >
              <MegaphoneIcon class="menu-icon" />
              <span class="menu-label">Маркетинг</span>
            </router-link>

            <router-link
              to="/manager/documents"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('documents') }"
            >
              <DocumentTextIcon class="menu-icon" />
              <span class="menu-label">Документы</span>
            </router-link>

            <router-link
              to="/manager/chats"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('/manager/chats') }"
            >
              <ChatBubbleLeftRightIcon class="menu-icon" />
              <span class="menu-label">Чаты</span>
            </router-link>

            <router-link
              to="/manager/emails"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('/manager/emails') }"
            >
              <EnvelopeIcon class="menu-icon" />
              <span class="menu-label">Почта</span>
            </router-link>

            <router-link
              to="/manager/meetings"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('/manager/meetings') }"
            >
              <CalendarDaysIcon class="menu-icon" />
              <span class="menu-label">Встречи</span>
            </router-link>

            <router-link
              to="/manager/applications"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('applications') }"
            >
              <DocumentTextIcon class="menu-icon" />
              <span class="menu-label">Заявки</span>
            </router-link>

            <router-link
              to="/manager/users"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('/manager/users') }"
            >
              <UserPlusIcon class="menu-icon" />
              <span class="menu-label">Пользователи</span>
            </router-link>

            <router-link
              to="/manager/work-process"
              class="menu-link"
              :class="{ 'menu-link-active': $route.path.includes('/manager/work-process') }"
            >
              <PuzzlePieceIcon class="menu-icon" />
              <span class="menu-label">Автоматизация</span>
            </router-link>
          </nav>

          <div class="p-3 border-t border-white/20">
            <router-link to="/manager/profile" class="menu-link !px-2">
              <div class="w-9 h-9 bg-white/20 rounded-full flex items-center justify-center shrink-0">
                <span class="text-white text-sm font-medium">{{ userInitials }}</span>
              </div>
              <div class="menu-label">
                <p class="text-sm font-medium text-white truncate">{{ authStore.userName }}</p>
                <p class="text-xs text-white/70 truncate">{{ portalRoleLabel }}</p>
              </div>
            </router-link>
            <div class="flex justify-center group-hover/sidebar:justify-end mt-2 transition-all duration-200">
              <button
                @click="handleLogout"
                class="p-2 text-white/70 hover:text-white transition-colors"
                title="Выйти"
              >
                <ArrowRightOnRectangleIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      <div class="ml-20">
        <header class="bg-slate-900/32 backdrop-blur-md border-b border-white/15 shadow-sm">
          <div class="px-8 py-4">
            <h1 class="text-2xl font-semibold text-white drop-shadow-sm">{{ currentPageTitle }}</h1>
            <p class="text-sm text-white/75 mt-1">{{ currentPageSubtitle }}</p>
          </div>
        </header>

        <main class="p-6 md:p-8">
          <div class="manager-content-skin rounded-2xl border border-white/20 bg-slate-900/26 backdrop-blur-md shadow-xl p-4 md:p-6 text-white">
            <router-view />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
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
  UserPlusIcon,
  ChatBubbleLeftRightIcon,
  EnvelopeIcon,
  CalendarDaysIcon,
  Squares2X2Icon,
  PuzzlePieceIcon,
} from "@heroicons/vue/24/outline";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const backgroundImageUrl = "/manager-bg.jpg";

const portalRoleLabel = computed(() => {
  const r = authStore.user?.role;
  if (r === "admin") return "Администратор";
  if (r === "manager") return "Менеджер";
  return "Сотрудник";
});

const currentPageTitle = computed(() => {
  const routeName = route.name as string;
  const titles: Record<string, string> = {
    ManagerDashboard: "Главная",
    ManagerContacts: "Контакты",
    ContactDetail: "Детали контакта",
    ManagerDeals: "Сделки",
    ManagerDealsKanban: "Канбан сделок",
    NewDeal: "Новая сделка",
    DealDetail: "Детали сделки",
    ManagerServices: "Услуги",
    ManagerCalendar: "Календарь",
    ManagerAnalytics: "Аналитика",
    ManagerMarketing: "Маркетинг",
    ManagerDocuments: "Документы",
    ManagerChats: "Чаты",
    ManagerEmails: "Почта",
    ManagerMeetings: "Встречи",
    ManagerProfile: "Профиль",
    Applications: "Заявки",
    ManagerApplications: "Заявки",
    ManagerUsers: "Пользователи",
    ManagerWorkProcesses: "Автоматизация процессов",
  };
  return titles[routeName] || "Панель управления";
});

const currentPageSubtitle = computed(() => {
  const routeName = route.name as string;
  const subtitles: Record<string, string> = {
    ManagerDashboard: "Ключевые показатели и быстрый обзор активности.",
    ManagerContacts: "Управление клиентами и партнерами.",
    ManagerDeals: "Контроль воронки продаж и текущих сделок.",
    ManagerDealsKanban: "Визуальная работа со стадиями сделок.",
    ManagerServices: "Каталог услуг и их параметры.",
    ManagerCalendar: "Планирование задач и встреч команды.",
    ManagerAnalytics: "Аналитика эффективности и конверсии.",
    ManagerMarketing: "Кампании, рассылки и маркетинговые активности.",
    ManagerDocuments: "Хранилище и управление документами.",
    ManagerChats: "Коммуникации с клиентами и командой.",
    ManagerEmails: "Работа с входящей и исходящей почтой.",
    ManagerMeetings: "Управление встречами и договоренностями.",
    ManagerApplications: "Заявки с Яндекс Форм и быстрая обработка.",
    ManagerUsers: "Управление сотрудниками и ролями доступа.",
    ManagerWorkProcesses: "Автоматизация процессов через блок-схемы.",
  };
  return subtitles[routeName] || "Рабочая зона менеджера CRM.";
});

const userInitials = computed(() => {
  const name = authStore.userName || "Менеджер";
  return name
    .split(" ")
    .map((part: string) => part.charAt(0))
    .join("")
    .toUpperCase()
    .slice(0, 2);
});

const handleLogout = async () => {
  await authStore.logout();
  router.push("/login");
};
</script>

<style scoped>
.menu-link {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.5rem;
  border-radius: 0.5rem;
  color: rgb(255 255 255);
  transition: background-color 0.2s ease, color 0.2s ease, padding 0.2s ease;
}

.menu-link:hover {
  background-color: rgba(15, 23, 42, 0.45);
  color: rgb(255 255 255);
}

.menu-link-active {
  background-color: rgba(59, 130, 246, 0.35);
  color: rgb(255 255 255);
}

.menu-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: rgb(255 255 255);
}

.menu-label {
  white-space: nowrap;
  opacity: 0;
  max-width: 0;
  overflow: hidden;
  transition: opacity 0.2s ease, max-width 0.2s ease;
}

.group\/sidebar:hover .menu-link {
  justify-content: flex-start;
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.group\/sidebar:hover .menu-label {
  opacity: 1;
  max-width: 220px;
}

.logo-label {
  opacity: 0;
  max-width: 0;
  overflow: hidden;
  transition: opacity 0.2s ease, max-width 0.2s ease;
}

.group\/sidebar:hover .logo-label {
  opacity: 1;
  max-width: 220px;
}

:deep(.manager-content-skin .bg-white) {
  background-color: rgba(15, 23, 42, 0.36) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

:deep(.manager-content-skin [class*="bg-white"]) {
  background-color: rgba(15, 23, 42, 0.36) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

:deep(.manager-content-skin .bg-gray-50) {
  background-color: rgba(30, 41, 59, 0.45) !important;
}

:deep(.manager-content-skin .border-gray-200),
:deep(.manager-content-skin .border-gray-300) {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

:deep(.manager-content-skin .text-gray-900),
:deep(.manager-content-skin .text-gray-800),
:deep(.manager-content-skin .text-gray-700) {
  color: rgba(255, 255, 255, 0.95) !important;
}

:deep(.manager-content-skin .text-gray-600),
:deep(.manager-content-skin .text-gray-500),
:deep(.manager-content-skin .text-gray-400) {
  color: rgba(226, 232, 240, 0.88) !important;
}

:deep(.manager-content-skin input),
:deep(.manager-content-skin select),
:deep(.manager-content-skin textarea) {
  background-color: rgba(15, 23, 42, 0.45) !important;
  color: rgba(255, 255, 255, 0.96) !important;
  border-color: rgba(255, 255, 255, 0.28) !important;
}

:deep(.manager-content-skin input::placeholder),
:deep(.manager-content-skin textarea::placeholder) {
  color: rgba(226, 232, 240, 0.7) !important;
}

:deep(.manager-content-skin button.bg-white) {
  color: rgba(248, 250, 252, 0.95) !important;
}

:deep(.manager-content-skin .hover\:bg-gray-50:hover) {
  background-color: rgba(30, 41, 59, 0.55) !important;
}
</style>
