/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef8ff",
          100: "#d8eeff",
          200: "#b9e1ff",
          300: "#89cfff",
          400: "#52b3ff",
          500: "#2a92ff",
          600: "#1372f5",
          700: "#0c5be1",
          800: "#104ab6",
          900: "#13408f",
          950: "#102857",
        },
        rough: {
          lower: "#10b981",    // Emerald green for lower approximation / certain
          boundary: "#f59e0b", // Amber for boundary region / incomplete
          upper: "#6366f1",    // Indigo for upper approximation / possible
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
