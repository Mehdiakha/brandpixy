/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'brand': {
          'purple': '#6439FF',
          'blue': '#4F75FF',
          'cyan': '#00CCDD',
          'sky': '#7CF5FF',
        },
        'dark': {
          'bg': '#0f172a',
          'surface': '#1e293b',
          'border': '#334155',
        }
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #6439FF, #4F75FF, #00CCDD)',
        'gradient-brand-rev': 'linear-gradient(135deg, #00CCDD, #4F75FF, #6439FF)',
        'gradient-dark': 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'slide-up': 'slide-up 0.5s ease-out',
        'fade-in-up': 'fade-in-up 0.6s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(100, 57, 255, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(79, 117, 255, 0.6)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'slide-up': {
          'from': { transform: 'translateY(20px)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
        'fade-in-up': {
          'from': { transform: 'translateY(30px)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
    },
  },
  plugins: [],
}
