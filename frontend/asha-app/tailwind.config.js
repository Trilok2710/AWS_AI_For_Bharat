/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1E3A8A",
        emergency: "#B91C1C",
        urgent: "#B45309",
        routine: "#166534",
        background: "#F3F4F6",
        textPrimary: "#111827",
        textSecondary: "#6B7280",
      },
    },
  },
  plugins: [],
}
