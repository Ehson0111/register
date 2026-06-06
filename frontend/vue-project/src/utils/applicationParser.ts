import type { ApplicationItem } from '../services/applications'

const escapeRe = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const normalizeSource = (raw: string) =>
  (raw || '')
    .replace(/\u00a0/g, ' ')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .trim()

/** Значения из шаблона Яндекс.Форм, которые не считаем ответом */
const isNoiseValue = (value: string, label?: string) => {
  const v = value.trim().toLowerCase()
  const lbl = (label || '').trim().toLowerCase()
  return (
    !v
    || v.startsWith('это письмо содержит ответы')
    || v === 'поступила новая заявка.'
    || v === 'поступила новая заявка'
    || (lbl && v === lbl)
    || v === 'id ответа'
  )
}

export const normalizeInn = (raw: string) => {
  const digits = (raw || '').replace(/\D/g, '')
  if (digits.length === 10 || digits.length === 12) return digits
  return ''
}

export const readApplicationField = (source: string, label: string): string => {
  const text = normalizeSource(source)
  if (!text) return ''

  const esc = escapeRe(label)
  const patterns = [
    // «Метка: значение» в начале строки
    new RegExp(`(?:^|\\n)\\s*${esc}\\s*:\\s*([^\\n]+)`, 'i'),
    // markdown-таблица после html2text: | Метка | значение |
    new RegExp(`\\|\\s*${esc}\\s*\\|\\s*([^|\\n]+?)\\s*\\|`, 'i'),
    // метка и значение где угодно в тексте
    new RegExp(`${esc}\\s*:\\s*([^\\n]+)`, 'i'),
    // метка на одной строке, значение на следующей
    new RegExp(`(?:^|\\n)\\s*${esc}\\s*\\n\\s*([^\\n]+)`, 'i'),
  ]

  for (const re of patterns) {
    const match = text.match(re)
    const value = match?.[1]?.trim()
    if (value && !isNoiseValue(value, label)) {
      return value
    }
  }
  return ''
}

export const normalizeFormDate = (raw: string) => {
  const iso = raw.match(/\d{4}-\d{2}-\d{2}/)
  if (iso) return iso[0]
  const dotted = raw.match(/(\d{1,2})[./](\d{1,2})[./](\d{4})/)
  if (!dotted) return ''
  const [, d, m, y] = dotted
  return `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`
}

export type ParsedApplication = {
  firstName: string
  lastName: string
  company: string
  position: string
  address: string
  inn: string
  phone: string
  serviceName: string
  amount: number
  email: string
  expectedCloseDate: string
  title: string
  description: string
}

export const parseApplication = (item: Pick<ApplicationItem, 'text' | 'subject'>): ParsedApplication => {
  // Тема письма часто содержит название сделки; тело — все поля формы
  const source = normalizeSource(`${item.subject || ''}\n${item.text || ''}`)
  const subjectDeal = (item.subject || '').replace(/^Новая заявка:\s*/i, '').trim()

  const firstName = readApplicationField(source, 'Имя')
  const lastName = readApplicationField(source, 'Фамилия')

  const descriptionMatch = source.match(/Описание:\s*([\s\S]*?)(?:\n\s*Это письмо содержит ответы|$)/i)

  const phone =
    readApplicationField(source, 'Контакт')
    || readApplicationField(source, 'Телефон')
  const email =
    readApplicationField(source, 'Почта')
    || readApplicationField(source, 'Email')
    || readApplicationField(source, 'E-mail')

  return {
    firstName,
    lastName,
    company: readApplicationField(source, 'Компания'),
    position: readApplicationField(source, 'Должность'),
    address: readApplicationField(source, 'Адрес'),
    inn: normalizeInn(readApplicationField(source, 'ИНН')),
    phone,
    serviceName: readApplicationField(source, 'Услуга'),
    amount: Number((readApplicationField(source, 'Сумма сделки') || '0').replace(/[^\d.]/g, '')) || 0,
    email,
    expectedCloseDate: normalizeFormDate(readApplicationField(source, 'Ожидаемая дата закрытия')),
    title:
      readApplicationField(source, 'Название сделки')
      || (subjectDeal && !subjectDeal.toLowerCase().includes('например') ? subjectDeal : '')
      || 'Заявка с сайта',
    description: descriptionMatch?.[1]?.trim() || '',
  }
}

export const contactDisplayName = (item: Pick<ApplicationItem, 'text' | 'subject'>) => {
  const parsed = parseApplication(item)
  const full = `${parsed.firstName} ${parsed.lastName}`.trim()
  return full || '-'
}
