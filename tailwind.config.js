/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./resources/**/*.blade.php",
        "./resources/**/*.js",
        "./resources/**/*.vue",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#e53e3e',
                    dark: '#c53030',
                    light: '#fc8181',
                }
            },
            fontFamily: {
                sans: ['Noto Sans KR', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
