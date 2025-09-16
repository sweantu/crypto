<template>
  <div>
    <h1>Todos</h1>
    <div v-if="todoStore.loading">Loading...</div>
    <div v-if="todoStore.error">{{ todoStore.error }}</div>
    <ul>
      <li v-for="todo in todoStore.todos" :key="todo.id">
        {{ todo.text }}
        <button @click="todoStore.removeTodo(todo.id)">Delete</button>
      </li>
    </ul>
    <input v-model="newTodo" @keyup.enter="todoStore.addTodo({ text: newTodo })" />
  </div>
</template>

<script setup lang="ts">
import { useTodoStore } from '@/stores/todo';
import { ref } from 'vue';

const todoStore = useTodoStore();
const newTodo = ref('');

// Load todos on mount
todoStore.loadTodos();

</script>
