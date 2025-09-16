// src/composables/useTodos.js
import { createTodo, deleteTodo, fetchTodos } from '@/api/todo'
import { ref } from 'vue'

export function useTodos() {
  const todos = ref([])
  const loading = ref(false)
  const error = ref(null)

  const loadTodos = async () => {
    try {
      loading.value = true
      todos.value = await fetchTodos()
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const addTodo = async (todoData) => {
    try {
      loading.value = true
      const newTodo = await createTodo(todoData)
      todos.value.push(newTodo)
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const removeTodo = async (id: number) => {
    try {
      loading.value = true
      await deleteTodo(id)
      todos.value = todos.value.filter((todo) => todo.id !== id)
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return { todos, loading, error, loadTodos, addTodo, removeTodo }
}
