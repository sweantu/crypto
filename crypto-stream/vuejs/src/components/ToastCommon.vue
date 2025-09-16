<!-- components/Toast.vue -->
<script setup lang="ts">
import { ref } from 'vue'
const message = ref('')
const show = ref(false)

function notify(msg: string) {
  message.value = msg
  show.value = true
  setTimeout(() => (show.value = false), 3000)
}

defineExpose({ notify })
</script>

<template>
  <transition name="fade">
    <div
      v-if="show"
      class="fixed right-4 bottom-4 rounded-lg bg-green-600 px-4 py-2 text-white shadow-lg"
    >
      {{ message }}
    </div>
  </transition>
</template>
