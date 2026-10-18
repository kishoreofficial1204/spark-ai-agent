/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        page: "#F8FAFF",
        surface: "#FFFFFF",
        primary: "#356DF3",
        violet: "#8057E8",
        ink: "#18243A",
        muted: "#64748B",
        border: "#E4EAF3",
      },
      fontFamily: {
        sans: ["Inter", "Plus Jakarta Sans", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
