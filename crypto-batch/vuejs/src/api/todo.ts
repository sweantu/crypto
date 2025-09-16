// src/api/todo.js
import apiClient from './index'

export interface Todo {
  id: number
  text: string
  completed: boolean
}

export const fetchTodos = async (): Promise<Todo[]> => {
  try {
    const response = await apiClient.get('/todos')
    return response.data
  } catch (error) {
    console.error('Error fetching todos:', error)
    throw error
  }
}

export const createTodo = async (todoData: Omit<Todo, 'id'>): Promise<Todo> => {
  try {
    const response = await apiClient.post('/todos', todoData)
    return response.data
  } catch (error) {
    console.error('Error creating todo:', error)
    throw error
  }
}

export const deleteTodo = async (id: number) => {
  try {
    await apiClient.delete(`/todos/${id}`)
  } catch (error) {
    console.error('Error deleting todo:', error)
    throw error
  }
}
