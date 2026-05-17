/** Коды статусов сделок в API и подписи для интерфейса */
export const DEAL_STATUS_OPTIONS = [
  { value: 'new', label: 'Новая' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'on_hold', label: 'На паузе' },
  { value: 'won', label: 'Выиграна' },
  { value: 'lost', label: 'Проиграна' },
] as const

export type DealStatusValue = (typeof DEAL_STATUS_OPTIONS)[number]['value']

export function getDealStatusLabel(status: string): string {
  return DEAL_STATUS_OPTIONS.find((item) => item.value === status)?.label ?? status
}
