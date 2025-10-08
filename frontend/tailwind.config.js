/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,ts,js,tsx,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#0ea5e9" }
      }
    }
  },
  plugins: [],
}