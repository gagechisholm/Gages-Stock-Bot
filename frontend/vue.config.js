module.exports = {
  pages: {
    index: {
      entry: "src/main.js",
      title: "StockNPC – Stock Market Bot for Discord",
    },
  },
  devServer: {
    proxy: "http://localhost:5000",
  },
  outputDir: "frontend/dist",
  publicPath: "/",
};
