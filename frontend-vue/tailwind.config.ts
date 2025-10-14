import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        maroon: '#800000', // ← custom maroon
      },
    },
  },
  plugins: [],
} satisfies Config