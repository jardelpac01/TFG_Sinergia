/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        display: ['Poppins', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
      },
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e5ff",
          200: "#bcd0ff",
          300: "#8eb0ff",
          400: "#5985fc",
          500: "#3560f5",
          600: "#2141e2",
          700: "#1c33b6",
          800: "#1c2e90",
          900: "#1c2b72"
        }
      }
    }
  },
  plugins: []
}
