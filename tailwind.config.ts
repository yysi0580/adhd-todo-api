import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F6F5F2",
        sidebar: "#FCFCFA",
        surface: "#FFFFFF",
        surfaceSubtle: "#F4F3EF",
        input: "#FAFAF8",
        border: "#DBDAD1",
        textPrimary: "#131312",
        textSecondary: "#63615C",
        textMuted: "#9E9C91",
        primary: "#244D42",
        primarySoft: "#D6E3DC",
        navy: "#1A1D24",
        blue: "#2B466F",
        amber: "#AD6B14",
        green: "#296B45",
        redMuted: "#853331",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        sm: "5px",
        card: "6px",
        panel: "6px",
      },
      boxShadow: {
        subtle: "0 1px 2px rgba(19, 19, 18, 0.05)",
      },
    },
  },
  plugins: [],
} satisfies Config;
