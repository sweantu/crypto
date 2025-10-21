import AdminSidebar from '@/components/AdminSidebar.vue'
import AuditLog from '@/components/AuditLog.vue'
import DataTable from '@/components/DataTable.vue'
import ToastCommon from '@/components/ToastCommon.vue'
import AboutPage from '@/views/AboutPage.vue'
import DashboardPage from '@/views/DashboardPage.vue'
import HomePage from '@/views/HomePage.vue'
import LoginPage from '@/views/LoginPage.vue'
import UserListPage from '@/views/UserListPage.vue'
import UserPage from '@/views/UserPage.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/about', component: AboutPage },
    { path: '/users', component: UserPage },
    { path: '/login', component: LoginPage },
    { path: '/user-list', component: UserListPage },
    { path: '/sidebar', component: AdminSidebar },
    { path: '/dashboard', component: DashboardPage },
    { path: '/datatable', component: DataTable },
    { path: '/toast', component: ToastCommon },
    { path: '/auditlog', component: AuditLog },
  ],
})

export default router
