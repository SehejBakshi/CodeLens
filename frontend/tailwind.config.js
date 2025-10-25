/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "media", // auto-switch based on OS setting
  content: [
    "./app/**/*.{ts,tsx,js,jsx}",
    "./components/**/*.{ts,tsx,js,jsx}",
    "./lib/**/*.{ts,tsx,js,jsx}",
    "./pages/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        glass: "rgba(255,255,255,0.6)",
        glassDark: "rgba(7,10,15,0.55)",
      },
      keyframes: {
        floaty: {
          "0%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-6px)" },
          "100%": { transform: "translateY(0px)" },
        },
      },
      animation: {
        floaty: "floaty 3s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
