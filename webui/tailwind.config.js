/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bt-dark': '#191b23',
        'bt-mid': '#232536',
        'bt-light': '#2b3147',
        'bt-accent': '#ffb32b',
        'bt-accent-light': '#ffd966'
      }
    },
  },
  plugins: [],
}
