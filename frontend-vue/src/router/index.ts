import Predict from '@/views/ai/Predict.vue'
import XAI from '@/views/ai/XAI.vue'
import Reviews from '@/views/ai/Reviews.vue'
import Models from '@/views/ai/Models.vue'
import Vision from '@/views/ai/Vision.vue'

export default [
  { path: '/ai/predict', name: 'Predict', component: Predict },
  { path: '/ai/xai',     name: 'XAI',     component: XAI },
  { path: '/ai/reviews', name: 'Reviews', component: Reviews },
  { path: '/ai/models',  name: 'Models',  component: Models },
  { path: '/ai/vision',  name: 'Vision',  component: Vision },
]