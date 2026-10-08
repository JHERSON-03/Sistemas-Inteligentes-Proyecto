/** Paleta "Nocturnal Scholar" exportada del design system de Stitch */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0F1220',
        card: '#1A1F36',
        'card-2': '#20264A',
        line: '#2A3050',
        ink: '#F1F3FA',
        muted: '#9AA3C0',
        primary: '#4F7CFF',
        tutor: '#8B7BFF',
        success: '#34D399',
        streak: '#FB923C',
        gold: '#FBBF24',
        historia: '#F59E0B',
        ciencia: '#22C55E',
        matematica: '#4F7CFF',
        comunicacion: '#EC4899',
      },
      fontFamily: {
        sans: ['Nunito Sans', 'Nunito', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '16px',
      },
      boxShadow: {
        soft: '0 8px 24px -12px rgba(0,0,0,0.6)',
      },
    },
  },
  plugins: [],
}
