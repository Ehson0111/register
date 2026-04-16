declare module "*.vue" {
  import type { DefineComponent } from "vue"
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, any>
  export default component
}

declare module "*/store/auth" {
  export const useAuthStore: any
}

declare module "*/store/auth.js" {
  export const useAuthStore: any
}

declare module "*/composables/useToast" {
  export const useToast: any
}

declare module "*/composables/useToast.js" {
  export const useToast: any
}

declare module "*/services/api" {
  const api: any
  export default api
}

declare module "*/services/api.js" {
  const api: any
  export default api
}

declare module "*/services/auth.js" {
  const auth: any
  export default auth
}
