/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,ts}'],
  theme: {
    extend: {
      screens: {
        'xs': { 'max': '599px' },
        'sm': { 'min': '600px', 'max': '959px' },
        'md': { 'min': '960px', 'max': '1279px' },
        'lg': { 'min': '1280px', 'max': '1919px' },
        'xl': { 'min': '1920px', 'max': '5000px' },
        'lt-sm': { 'max': '599px' },
        'lt-md': { 'max': '959px' },
        'lt-lg': { 'max': '1279px' },
        'lt-xl': { 'max': '1919px' },
        'gt-xs': { 'min': '600px' },
        'gt-sm': { 'min': '960px' },
        'gt-md': { 'min': '1280px' },
        'gt-lg': { 'min': '1920px' }
      },
      flex: {
        'icon': '1 1 36px'
      },
      gridTemplateColumns: {
        'infodialog': '200px minmax(200px, 1fr)'
      }
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
};
