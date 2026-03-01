/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html"],
  safelist: [
    { pattern: /bg-(green|blue|yellow|orange|red)-(100|500)/ },
    { pattern: /text-(green|blue|yellow|orange|red)-800/ },
  ],
  theme: { extend: {} },
  plugins: [],
}
