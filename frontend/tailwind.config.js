/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Poppins"', 'system-ui', 'sans-serif'],
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: { pink: '#ff3f6c', orange: '#ff7a45', plum: '#282c3f', mist: '#fff5f2', teal: '#03a685', gold: '#ffb100' },
      },
      boxShadow: {
        card: '0 2px 14px rgba(40,44,63,.09)',
        lift: '0 12px 30px rgba(255,63,108,.22)',
      },
    },
  },
  plugins: [],
}
