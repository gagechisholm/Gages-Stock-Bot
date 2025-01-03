module.exports = {
  devServer: {
    proxy: "http://localhost:5000",
  },
  outputDir: "frontend/dist", // Ensures the build output goes to 'frontend/dist'
  publicPath: "/", // Adjust if deploying to a subpath
};
