<script setup lang="ts">
import { useCounter } from '@/composables/useCounter'
import { useUserStore } from '@/stores/user'

const { count, increment } = useCounter()
const userStore = useUserStore()

console.log('HomePage component loaded')
</script>

<template>
  <h1 class="text-3xl font-bold text-blue-500 underline">You did it!</h1>
  <p>
    Visit <a href="https://vuejs.org/" target="_blank" rel="noopener">vuejs.org</a> to read the
    documentation
  </p>
  <button @click="increment">Count: {{ count }}</button>

  <h2>User List</h2>
  <div v-if="userStore.users.length === 0">No users found.</div>
  <ul v-else>
    <li v-for="user in userStore.users" :key="user.id">
      <strong>{{ user.name }}</strong> ({{ user.email }}) - Role: {{ user.role }}
    </li>
  </ul>
</template>
