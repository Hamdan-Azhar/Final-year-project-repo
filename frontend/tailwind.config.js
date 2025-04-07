/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        customDark: 'rgba(18, 20, 23, 1)',
        'dark-bg': '#121217',
        'dark-header': '#131120',
        'dark-card': '#1c1c1e',
        'card-selected': '#2c2c2e',
        'header-gradient-start': '#504686',
        'header-gradient-end': '#131120',
        'footer-bg': '#131120',
        primaryDark: "#131120",
        cardDark: "#1c1e2e",
        buttonDark: "#3b3e56",
        gray: {
          700: "#3f3f46",
          800: "#27272a",
          900: "#18181b",
        },
        primary: '#121212',
        secondary: '#1a1a1a',
        buttonGray: '#292929',
        tableBorder: '#292929',
        blueHover: '#007BFF'
      },
      fontFamily: {
        inter: ['"Inter"', 'sans-serif'], // Inter font ko yahan define karo
      },
    },

  },
  plugins: [],
};
