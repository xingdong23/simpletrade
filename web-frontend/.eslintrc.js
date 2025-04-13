module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/essential',
    // '@vue/standard' // Temporarily remove this to resolve conflict
  ],
  parserOptions: {
    parser: '@babel/eslint-parser', // Or maybe 'babel-eslint' is needed for older eslint?
    requireConfigFile: false // Needed if not using babel.config.js
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    // Add any custom rules or overrides here
    'vue/multi-word-component-names': 'off' // Disable rule requiring multi-word component names if desired
  }
} 