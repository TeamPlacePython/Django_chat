/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
    "../templates/**/*.html",
    "../**/templates/**/*.html",
    "../**/forms.py",
  ],
  theme: {
    extend: {
      colors: {
        navbar: 'oklch(95.81% 0 0)',
        text_navbar: 'oklch(37.91% 0 0)',
        hover_navbar: 'oklch(83.28% 0 0)',
        defilepsie_red: 'oklch(51.98% 0.1931 23.14)',
        defilepsie_red_secondary: 'oklch(45% 0.1931 23.14)',
        defilepsie_blue: 'oklch(50.67% 0.137 248.91)',
        defilepsie_blue_secondary: 'oklch(45% 0.137 248.91)',
        chat_box: 'oklch(71.37% 0.0192 261.32)',
      },
    },
  },
  plugins: [],
}
