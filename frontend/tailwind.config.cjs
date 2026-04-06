/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        moss: '#2E4036',
        clay: '#CC5833',
        cream: '#F2F0E9',
        charcoal: '#1A1A1A'
      },
      fontFamily: {
        sans: ['"OpenDyslexic"', 'sans-serif'],
        display: ['"OpenDyslexic"', 'sans-serif'],
        serif: ['"OpenDyslexic"', 'sans-serif'],
        mono: ['"OpenDyslexic Mono"', '"OpenDyslexic"', 'monospace'],
        inter: ['"OpenDyslexic"', 'sans-serif'],
        playfair: ['"OpenDyslexic"', 'sans-serif']
      },
      transitionTimingFunction: {
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)'
      }
    }
  },
  plugins: []
};

