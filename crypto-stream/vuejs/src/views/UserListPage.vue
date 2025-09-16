<!-- src/components/UserCrud.vue -->
<script setup lang="ts">
import { reactive, ref } from 'vue'

type User = {
  id: number
  name: string
  email: string
  role: string
}

const users = ref<User[]>([
  { id: 1, name: 'Alice Johnson', email: 'alice@example.com', role: 'Admin' },
  { id: 2, name: 'Bob Smith', email: 'bob@example.com', role: 'User' },
])

// Modal state
const showModal = ref(false)
const isEdit = ref(false)
const currentUser = reactive<User>({ id: 0, name: '', email: '', role: '' })

// Open Create modal
const openCreate = () => {
  isEdit.value = false
  Object.assign(currentUser, { id: 0, name: '', email: '', role: '' })
  showModal.value = true
}

// Open Edit modal
const openEdit = (user: User) => {
  isEdit.value = true
  Object.assign(currentUser, user)
  showModal.value = true
}

// Save user (Create or Update)
const saveUser = () => {
  if (isEdit.value) {
    const index = users.value.findIndex((u) => u.id === currentUser.id)
    if (index !== -1) users.value[index] = { ...currentUser }
  } else {
    const newId = Math.max(...users.value.map((u) => u.id), 0) + 1
    users.value.push({ ...currentUser, id: newId })
  }
  showModal.value = false
}

// Delete user
const deleteUser = (id: number) => {
  users.value = users.value.filter((u) => u.id !== id)
}
</script>

<template>
  <div class="p-6">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-2xl font-bold">User Management</h2>
      <button
        @click="openCreate"
        class="rounded-xl bg-green-600 px-4 py-2 text-white hover:bg-green-700"
      >
        + Add User
      </button>
    </div>

    <!-- User Table -->
    <div class="overflow-x-auto rounded-2xl shadow">
      <table class="min-w-full border border-gray-200 bg-white">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Name</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Email</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Role</th>
            <th class="px-4 py-2 text-sm font-medium text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="border-t hover:bg-gray-50">
            <td class="px-4 py-2">{{ user.name }}</td>
            <td class="px-4 py-2">{{ user.email }}</td>
            <td class="px-4 py-2">{{ user.role }}</td>
            <td class="px-4 py-2 text-center">
              <button
                @click="openEdit(user)"
                class="rounded-lg bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700"
              >
                Edit
              </button>
              <button
                @click="deleteUser(user.id)"
                class="ml-2 rounded-lg bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-lg">
        <h3 class="mb-4 text-xl font-bold">
          {{ isEdit ? 'Edit User' : 'Create User' }}
        </h3>

        <form @submit.prevent="saveUser" class="space-y-4">
          <div>
            <label class="mb-1 block text-sm">Name</label>
            <input
              v-model="currentUser.name"
              type="text"
              required
              class="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm">Email</label>
            <input
              v-model="currentUser.email"
              type="email"
              required
              class="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm">Role</label>
            <input
              v-model="currentUser.role"
              type="text"
              required
              class="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div class="flex justify-end space-x-2 pt-4">
            <button
              type="button"
              @click="showModal = false"
              class="rounded-lg border border-gray-300 px-4 py-2 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
