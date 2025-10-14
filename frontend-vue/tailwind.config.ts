import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        orange: '#FFA500', // ← custom orange
      },
    },
  },
  plugins: [],
} satisfies Config