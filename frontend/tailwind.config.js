/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0B0F17',
          surface: '#131B2A',
          card: '#1A2438',
          border: '#27354F',
          gold: '#E5A93C',
          amber: '#F59E0B',
          cyan: '#06B6D4',
          emerald: '#10B981',
          rose: '#F43F5E'
        }
      }
    },
  },
  plugins: [],
}
