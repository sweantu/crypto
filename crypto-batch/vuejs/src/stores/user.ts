import * as userApi from '@/api/user'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // Type the users ref as an array of User
  const users = ref<userApi.User[]>([])

  const fetch = async (): Promise<void> => {
    if (users.value.length === 0) {
      await getMany()
    }
  }

  // Type the getMany function
  const getMany = async (): Promise<void> => {
    const response = await userApi.getMany()
    users.value = response.items
  }

  // Type the create function
  const create = async (newUser: userApi.CreateUserData): Promise<void> => {
    await userApi.create(newUser)
    await getMany() // Refresh the user list after creation
  }

  return { users, getMany, create, fetch }
})
