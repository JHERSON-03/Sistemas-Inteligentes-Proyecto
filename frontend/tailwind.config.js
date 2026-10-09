/** Paleta institucional del I.E.P. Louis Pasteur (Laredo): fondo blanco con el azul marino y el dorado del escudo */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#F4F6FB',
        card: '#FFFFFF',
        'card-2': '#EDF1F8',
        line: '#D6DEEC',
        ink: '#16244A',
        muted: '#5A6A8A',
        // Azul marino exacto del escudo: botones, pestaña activa y enlaces
        navy: '#284078',
        primary: '#284078',
        'primary-hover': '#1E3262',
        'primary-ink': '#FFFFFF',
        'primary-soft': '#1E3262',
        // Dorado exacto del escudo: bordes, acentos y botón destacado
        accent: '#A8A028',
        'accent-hover': '#958E20',
        // Azul institucional para el Tutor IA
        tutor: '#3B5BA5',
        'tutor-soft': '#284078',
        success: '#0F9F6E',
        streak: '#E8590C',
        // Dorado oscuro para los puntos: se lee bien sobre blanco
        gold: '#8A7E12',
        historia: '#D97706',
        ciencia: '#16A34A',
        matematica: '#2563EB',
        comunicacion: '#DB2777',
      },
      fontFamily: {
        sans: ['Nunito Sans', 'Nunito', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '16px',
      },
      boxShadow: {
        soft: '0 8px 24px -12px rgba(22,36,74,0.18)',
      },
    },
  },
  plugins: [],
}
