<!-- src/components/LoginForm.vue -->
<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  email: '',
  password: '',
})

const login = () => {
  console.log('Login:', form)
  // replace with API call
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-100">
    <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow">
      <h2 class="mb-6 text-center text-2xl font-bold">Login</h2>
      <form @submit.prevent="login" class="space-y-4">
        <!-- Email -->
        <div>
          <label class="mb-1 block text-sm font-medium">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full rounded-xl border px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="you@example.com"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="mb-1 block text-sm font-medium">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full rounded-xl border px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="••••••••"
          />
        </div>

        <!-- Button -->
        <button
          type="submit"
          class="w-full rounded-xl bg-blue-600 py-2 font-semibold text-white transition hover:bg-blue-700"
        >
          Sign in
        </button>
      </form>
    </div>
  </div>
</template>
