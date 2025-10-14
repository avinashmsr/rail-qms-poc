import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

// Eager imports for core pages (adjust paths to project)
import Dashboard from '@/views/Dashboard.vue'
import Pads from '@/views/Pads.vue'

// Lazy imports for AI pages (helps with bundle size)
const Predict = () => import('@/views/ai/Predict.vue')
const XAI     = () => import('@/views/ai/XAI.vue')
const Reviews = () => import('@/views/ai/Reviews.vue')
const Models  = () => import('@/views/ai/Models.vue')
const Vision  = () => import('@/views/ai/Vision.vue')

const routes: RouteRecordRaw[] = [
  { path: '/',              name: 'Dashboard', component: Dashboard },
  { path: '/pads',          name: 'Pads',      component: Pads },

  // ✅ AI pages
  { path: '/ai/predict',    name: 'Predict',   component: Predict },
  { path: '/ai/xai',        name: 'XAI',       component: XAI },
  { path: '/ai/reviews',    name: 'Reviews',   component: Reviews },
  { path: '/ai/models',     name: 'Models',    component: Models },
  { path: '/ai/vision',     name: 'Vision',    component: Vision },

  // Optional catch-all -> dashboard (or a NotFound page)
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router