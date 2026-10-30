/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class", // enable manual dark mode with a "dark" class
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",  // all your React components/pages
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

