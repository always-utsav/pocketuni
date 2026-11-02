/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Authoritative PocketUni Institutional Palette
        midnight: {
          DEFAULT: '#14252B',
          dark: '#0E1B20',
          light: '#1B3139',
        },
        forest: {
          DEFAULT: '#176B68',
          dark: '#115250',
          light: '#208581',
        },
        porcelain: {
          DEFAULT: '#F5F3EE',
          card: '#FFFFFF',
          subtle: '#ECE9E1',
        },
        sand: {
          DEFAULT: '#E7DFD2',
          border: '#D9CFBF',
          dark: '#C8BEAD',
        },
        copper: {
          DEFAULT: '#B96D47',
          hover: '#9C5A37',
          light: '#F8EFEA',
        },
        sage: {
          DEFAULT: '#8A9B87',
          light: '#A5B5A2',
          bg: '#EEF2ED',
          border: '#D2DDD0',
        },
        charcoal: {
          DEFAULT: '#273238',
          light: '#3C4950',
          subtle: '#52626B',
        },
        // Backward-compatible color mapping for existing views
        ink: {
          DEFAULT: '#14252B',
          navy: '#14252B',
          dark: '#0E1B20',
          light: '#273238',
        },
        slate: {
          DEFAULT: '#176B68',
          blue: '#176B68',
          light: '#208581',
          subtle: '#E7DFD2',
        },
        terracotta: {
          DEFAULT: '#B96D47',
          muted: '#B96D47',
          hover: '#9C5A37',
          light: '#F8EFEA',
        },
        stone: {
          DEFAULT: '#E7DFD2',
          warm: '#E7DFD2',
          border: '#D9CFBF',
          dark: '#C8BEAD',
        },
        paper: {
          DEFAULT: '#F5F3EE',
          card: '#FFFFFF',
          subtle: '#ECE9E1',
        },
        // Mapped brand tokens
        brand: {
          primary: '#14252B',       // Deep Midnight
          primaryLight: '#273238',  // Charcoal
          secondary: '#176B68',     // Forest Teal
          secondaryLight: '#208581',
          accent: '#B96D47',        // Burnt Copper
          accentHover: '#9C5A37',
          softAccent: '#8A9B87',    // Soft Sage
          softAccentLight: '#EEF2ED',
          softAccentDark: '#6D7E6B',
          surface: '#F5F3EE',       // Porcelain
          card: '#FFFFFF',
          border: '#E7DFD2',        // Warm Sand
          borderSubtle: '#ECE9E1',
          muted: '#273238',         // Charcoal
          darkMuted: '#52626B',
        }
      },
      fontFamily: {
        heading: ['Sora', 'General Sans', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'Manrope', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(32, 44, 57, 0.05)',
        'card': '0 2px 8px -1px rgba(32, 44, 57, 0.06), 0 1px 3px -1px rgba(32, 44, 57, 0.04)',
        'float': '0 12px 32px -4px rgba(32, 44, 57, 0.12)',
        'popover': '0 10px 25px -3px rgba(32, 44, 57, 0.1), 0 4px 6px -2px rgba(32, 44, 57, 0.05)',
      },
    },
  },
  plugins: [],
}
