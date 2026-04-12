import api from './api'

export async function fetchTeamUsers() {
  return api.get('/users/team/')
}

export async function createTeamUser(payload) {
  return api.post('/users/team/', payload)
}

export async function patchTeamUserActive(id, is_active) {
  return api.patch(`/users/team/${id}/`, { is_active })
}
