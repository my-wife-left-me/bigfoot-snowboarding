import { createRouter, createWebHistory } from 'vue-router'
import SnowboardCatalog from '../views/SnowboardCatalog.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            redirect: '/catalog'
        },
        {
            path: '/catalog',
            name: 'catalog',
            component: SnowboardCatalog
        }
    ]
})

export default router

