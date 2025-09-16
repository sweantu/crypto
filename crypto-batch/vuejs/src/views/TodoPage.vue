<template>
  <div>
    <h1>Todos</h1>
    <div v-if="loading">Loading...</div>
    <div v-if="error">{{ error }}</div>
    <ul>
      <li v-for="todo in todos" :key="todo.id">
        {{ todo.text }}
        <button @click="removeTodo(todo.id)">Delete</button>
      </li>
    </ul>
    <input v-model="newTodo" @keyup.enter="addTodo({ text: newTodo })" />
  </div>
</template>

<script setup lang="ts">
import { useTodos } from '@/composables/useTodos';
import { ref } from 'vue';

const { todos, loading, error, loadTodos, addTodo, removeTodo } = useTodos();
const newTodo = ref('');

// Load todos on component mount
loadTodos();

</script>
