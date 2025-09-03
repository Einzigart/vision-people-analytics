// ESLint flat config for React + Vite + TypeScript + Vitest
import js from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import reactPlugin from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import vitestPlugin from 'eslint-plugin-vitest'

export default [
  { ignores: ['dist', 'node_modules'] },
  ...tseslint.config(
    {
      files: ['**/*.{ts,tsx}'],
      languageOptions: {
        ecmaVersion: 2023,
        sourceType: 'module',
        parser: tseslint.parser,
        parserOptions: {
          ecmaFeatures: { jsx: true },
        },
        globals: { ...globals.browser, ...globals.es2021 },
      },
      settings: { react: { version: 'detect' } },
      plugins: {
        '@typescript-eslint': tseslint.plugin,
        react: reactPlugin,
        'react-hooks': reactHooks,
        vitest: vitestPlugin,
      },
      rules: {
        ...js.configs.recommended.rules,
        ...tseslint.configs.recommended.rules,
        // Prefer TS-specific unused-vars rule
        'no-unused-vars': 'off',
        // React 17+ JSX transform
        'react/react-in-jsx-scope': 'off',
        // Hooks rules
        'react-hooks/rules-of-hooks': 'error',
        'react-hooks/exhaustive-deps': 'warn',
        // Common TS rules
        '@typescript-eslint/no-unused-vars': [
          'warn',
          { argsIgnorePattern: '^_', varsIgnorePattern: '^React$' },
        ],
      },
    },
    // Vitest test files env
    {
      files: ['**/*.test.{ts,tsx}'],
      languageOptions: {
        globals: { ...globals.browser, ...vitestPlugin.environments.env.globals },
      },
      rules: {},
    }
  ),
]
