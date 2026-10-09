/** Paleta institucional del I.E.P. Louis Pasteur (Laredo): azul marino y dorado del escudo */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0B1633',
        card: '#13234A',
        'card-2': '#1A2E5E',
        line: '#2A4176',
        ink: '#F2F4FA',
        muted: '#A3B1D1',
        // Azul marino exacto del escudo
        navy: '#284078',
        // Dorado del escudo (#A8A028), un poco más luminoso para leerse bien sobre fondo oscuro
        primary: '#C8B83A',
        'primary-hover': '#B3A42E',
        'primary-ink': '#0B1633',
        'primary-soft': '#E8DE97',
        // Azul institucional claro para el Tutor IA
        tutor: '#6F8FD6',
        'tutor-soft': '#C9D6F5',
        success: '#34D399',
        streak: '#FB923C',
        gold: '#E6CF4F',
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
