<!-- components/AdminSidebar.vue -->
<template>
  <div class="flex h-screen w-64 flex-col bg-gray-800 text-white">
    <div class="border-b border-gray-700 p-4 text-xl font-bold">Admin Panel</div>
    <nav class="flex-1 space-y-2 p-2">
      <a href="#" class="flex items-center rounded-lg px-3 py-2 hover:bg-gray-700">
        <span>📊 Dashboard</span>
      </a>
      <a href="#" class="flex items-center rounded-lg px-3 py-2 hover:bg-gray-700">
        <span>👥 Users</span>
      </a>
      <a href="#" class="flex items-center rounded-lg px-3 py-2 hover:bg-gray-700">
        <span>⚙️ Settings</span>
      </a>
    </nav>
  </div>
</template>
