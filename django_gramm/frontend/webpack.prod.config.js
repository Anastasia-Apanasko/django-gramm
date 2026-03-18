const path = require('path');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');

module.exports = {
    mode: 'production',
    entry: './src/index.js',
    output: {
        path: path.resolve(__dirname, '../static/frontend/'),
        filename: 'bundle.js',
        publicPath: '/static/frontend/',
    },

    plugins: [
        new CleanWebpackPlugin(),
    ],
};
