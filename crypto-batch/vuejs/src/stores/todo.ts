import { createTodo, deleteTodo, fetchTodos } from '@/api/todo'
import { defineStore } from 'pinia'

export const useTodoStore = defineStore('todo', {
  state: () => ({
    todos: [],
    loading: false,
    error: null,
  }),
  actions: {
    async loadTodos() {
      try {
        this.loading = true
        this.todos = await fetchTodos()
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
    async addTodo(todoData) {
      try {
        this.loading = true
        const newTodo = await createTodo(todoData)
        this.todos.push(newTodo)
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
    async removeTodo(id) {
      try {
        this.loading = true
        await deleteTodo(id)
        this.todos = this.todos.filter((todo) => todo.id !== id)
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
  },
})
