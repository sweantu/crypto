import apiClient from './index'

// Define the User interface based on the sample response
export interface User {
  id: string
  name: string
  email: string
  role: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

// Define the API response interface for getMany
export interface PaginatedUsersResponse {
  total: number
  page: number
  page_size: number
  items: User[]
}

// Define the input data for creating a user
export interface CreateUserData {
  name: string
  email: string
  role: string
  password: string
}

// Type the getMany function
export const getMany = async (): Promise<PaginatedUsersResponse> => {
  const { data } = await apiClient.get<PaginatedUsersResponse>('/admin/users/')
  return data
}

// Type the create function
export const create = async (data: CreateUserData): Promise<User> => {
  const { data: responseData } = await apiClient.post<User>('/admin/users/', data)
  return responseData
}


