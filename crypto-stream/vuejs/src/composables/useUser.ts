import * as userApi from '@/api/user'
import { ref } from 'vue'

export function useUser() {
  // Type the users ref as an array of User
  const users = ref<userApi.User[]>([])

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

  return { users, getMany, create }
}
