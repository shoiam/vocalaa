/* eslint-disable @typescript-eslint/no-explicit-any */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export const createProfile = async (profileData: any, token: string) => {
  const response = await fetch(`${API_BASE_URL}/profile/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(profileData),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create profile')
  }

  return response.json()
}

export const updateProfile = async (profileData: any, token: string) => {
  const response = await fetch(`${API_BASE_URL}/profile/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(profileData),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update profile')
  }

  return response.json()
}

export const getProfile = async (token: string) => {
  const response = await fetch(`${API_BASE_URL}/profile/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })

  if (response.status === 404) {
    return null // No profile exists yet
  }

  if (!response.ok) {
    throw new Error('Failed to fetch profile')
  }

  return response.json()
}