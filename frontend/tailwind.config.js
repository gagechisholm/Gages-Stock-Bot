module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: "#5865F2",
        "brand-hover": "#4752C4",
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", '"Inter"', '"Segoe UI"', "sans-serif"],
      },
    },
  },
  plugins: [],
};
