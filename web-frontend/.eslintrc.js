module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/essential',
    '@vue/standard'
  ],
  parserOptions: {
    parser: '@babel/eslint-parser', // Or just 'babel-eslint' depending on version/setup
    requireConfigFile: false // Needed if not using babel.config.js
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    // Add any custom rules or overrides here
    'vue/multi-word-component-names': 'off' // Disable rule requiring multi-word component names if desired
  }
} 