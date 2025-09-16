<!-- components/DataTable.vue -->
<script setup lang="ts">
import { computed, ref } from 'vue'

const search = ref('')
const page = ref(1)
const perPage = 5

const data = ref([
  { id: 1, name: 'Alice', role: 'Admin' },
  { id: 2, name: 'Bob', role: 'User' },
  { id: 3, name: 'Charlie', role: 'User' },
  { id: 4, name: 'David', role: 'Admin' },
  { id: 5, name: 'Eve', role: 'User' },
  { id: 6, name: 'Frank', role: 'User' },
])

const filtered = computed(() =>
  data.value.filter((item) => item.name.toLowerCase().includes(search.value.toLowerCase())),
)

const paginated = computed(() =>
  filtered.value.slice((page.value - 1) * perPage, page.value * perPage),
)

const totalPages = computed(() => Math.ceil(filtered.value.length / perPage))
</script>

<template>
  <div class="rounded-2xl bg-white p-4 shadow">
    <div class="mb-4 flex justify-between">
      <input
        v-model="search"
        type="text"
        placeholder="Search..."
        class="rounded-lg border px-3 py-2"
      />
    </div>

    <table class="w-full border">
      <thead class="bg-gray-100">
        <tr>
          <th class="p-2 text-left">ID</th>
          <th class="p-2 text-left">Name</th>
          <th class="p-2 text-left">Role</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in paginated" :key="row.id" class="border-t">
          <td class="p-2">{{ row.id }}</td>
          <td class="p-2">{{ row.name }}</td>
          <td class="p-2">{{ row.role }}</td>
        </tr>
      </tbody>
    </table>

    <div class="mt-4 flex justify-center space-x-2">
      <button
        @click="page--"
        :disabled="page === 1"
        class="rounded border px-3 py-1 disabled:opacity-50"
      >
        Prev
      </button>
      <span>Page {{ page }} / {{ totalPages }}</span>
      <button
        @click="page++"
        :disabled="page === totalPages"
        class="rounded border px-3 py-1 disabled:opacity-50"
      >
        Next
      </button>
    </div>
  </div>
</template>
