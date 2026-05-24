/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Vazirmatn", "Tahoma", "Arial", "sans-serif"] },
      colors: { ink: "#161616", paper: "#f7f5ef", saffron: "#f4b740", teal: "#11756d", berry: "#a53153" },
      boxShadow: { soft: "0 18px 60px rgba(22, 22, 22, 0.09)" }
    }
  },
  plugins: []
};
