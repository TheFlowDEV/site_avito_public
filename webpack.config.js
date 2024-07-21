const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  context: __dirname,
  mode:'development',
  target:'web',
  entry: {"index":path.resolve(__dirname,"static","index"),
          "add_adv":path.resolve(__dirname,"static","add_adv","add_adv"),
          "chat":path.resolve(__dirname,"static","chat"), 
          "adverstiments":path.resolve(__dirname,"static","adverstiments"),
          "profile":path.resolve(__dirname,"static","profile",'profile'),
          'register_oauth':path.resolve(__dirname,'static','register_oauth')
        },

  output: {
    path: path.resolve(__dirname, "static/webpack_bundles/"),
    publicPath: "auto", // necessary for CDNs/S3/blob storages
    filename: "[name].js",
  },
  plugins: [
    new BundleTracker({ path: __dirname, filename: "webpack-stats.json" })
    ],
    module:{
    rules:[
        {
    test: /\.(scss)$/,
    use: [
        {
      loader: 'style-loader'
    }, 
    {
      loader: 'css-loader', // translates CSS into CommonJS modules
    }, 
    {
      loader: 'postcss-loader', // Run post css actions
      options: {
        postcssOptions:{
        plugins: function () { // post css plugins, can be exported to postcss.config.js
          return [
            require('precss'),
            require('autoprefixer')
          ];
        }
        }
      }
    }, 
      {
        loader: 'sass-loader' // compiles Sass to CSS
      }]
    },
    {
      test:"/\.(?:js|mjs|cjs)$/",
      use:[
        {loader:"babel-loader"}
      ]
    }
  ],

}
};