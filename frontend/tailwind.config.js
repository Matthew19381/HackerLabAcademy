/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#0d1117",
          surface: "#161b22",
          border: "#30363d",
          green: "#39d353",
          cyan: "#58a6ff",
          red: "#f85149",
          yellow: "#e3b341",
          purple: "#bc8cff",
        },
      },
    },
  },
  plugins: [],
}
