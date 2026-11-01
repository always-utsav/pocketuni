/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Refined PocketUni Academic Design Direction
        ink: {
          DEFAULT: '#202C39',
          navy: '#202C39',
          dark: '#17202A',
          light: '#2D3D4E',
        },
        slate: {
          DEFAULT: '#536B7A',
          blue: '#536B7A',
          light: '#6E8A9C',
          subtle: '#E2E8EC',
        },
        terracotta: {
          DEFAULT: '#B56F4A',
          muted: '#B56F4A',
          hover: '#9E5F3D',
          light: '#F8EFEA',
        },
        stone: {
          DEFAULT: '#E8E2D8',
          warm: '#E8E2D8',
          border: '#D9D1C5',
          dark: '#BDB3A4',
        },
        paper: {
          DEFAULT: '#F7F6F2',
          card: '#FFFFFF',
          subtle: '#F1EFEA',
        },
        sage: {
          DEFAULT: '#668477',
          light: '#8FAAA0',
          bg: '#EAF0ED',
          border: '#D2DFD9',
        },
        // Mapped brand tokens preserving layout while applying the refined visual direction
        brand: {
          primary: '#202C39',       // Ink navy
          primaryLight: '#2D3D4E',
          secondary: '#536B7A',     // Slate blue
          secondaryLight: '#6E8A9C',
          accent: '#B56F4A',        // Muted terracotta accent
          accentHover: '#9E5F3D',
          softAccent: '#668477',    // Sage accent
          softAccentLight: '#EAF0ED',
          softAccentDark: '#4F685D',
          surface: '#F7F6F2',       // Paper background
          card: '#FFFFFF',
          border: '#E8E2D8',        // Warm stone border
          borderSubtle: '#F1EFEA',
          muted: '#536B7A',         // Slate blue muted text
          darkMuted: '#8E9EAA',
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
