<script setup lang="ts">
import type { CreateUserData } from '@/api/user';
import { useUserStore } from '@/stores/user';
import { ref } from 'vue';

const userStore = useUserStore();
const newUser = ref<CreateUserData>({
  name: '',
  email: '',
  role: 'user',
  password: '123456',
});

// Fetch users on component mount

userStore.fetch();
console.log('UserPage component loaded');

// Handle form submission to create a new user
const handleCreate = async () => {
  try {
    await userStore.create(newUser.value);
    // Reset form after successful creation
    newUser.value = { name: '', email: '', role: 'user', password: '' };
  } catch (error) {
    console.error('Failed to create user:', error);
  }
};

// Format date for display
const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString();
};
</script>


<template>
  <h1>Users</h1>

  <!-- Form to create a new user -->
  <h2>Add New User</h2>
  <form @submit.prevent="handleCreate">
    <div>
      <label for="name">Name:</label>
      <input v-model="newUser.name" id="name" type="text" required />
    </div>
    <div>
      <label for="email">Email:</label>
      <input v-model="newUser.email" id="email" type="email" required />
    </div>
    <div>
      <label for="role">Role:</label>
      <select v-model="newUser.role" id="role" required>
        <option value="admin">Admin</option>
        <option value="user">User</option>
      </select>
    </div>
    <button type="submit">Create User</button>
  </form>


  <!-- User list -->

  <h2>User List</h2>
  <div v-if="userStore.users.length === 0">No users found.</div>
  <ul v-else>
    <li v-for="user in userStore.users" :key="user.id">
      <strong>{{ user.name }}</strong> ({{ user.email }}) - Role: {{ user.role }}
      <small>(Created: {{ formatDate(user.created_at) }})</small>
    </li>
  </ul>
</template>
