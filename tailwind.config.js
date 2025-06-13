/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html', // Adjusted path for Django
    './**/templates/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [], // Keep this empty, we will load daisyui from CSS
}