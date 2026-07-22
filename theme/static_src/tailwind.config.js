module.exports = {
  content: [
    "/app/templates/**/*.html",
    "/app/**/templates/**/*.html",
    "/app/**/*.js",
  ],

  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif']
      },
      borderRadius: {
        xl2: "1rem",
      },
      boxShadow: {
        custom: "0 4px 10px var(--shadow-color)",
      },
    },
  },

  plugins: [require("daisyui")],

  daisyui: {
    themes: [
      {
        sun: {
          /* Brand */
          primary: "#2563EB",
          "primary-content": "#FFFFFF",

          secondary: "#64748B",
          accent: "#22C55E",

          neutral: "#1E293B",

          /* Backgrounds */
          "base-100": "#FFFFFF",   // cards
          "base-200": "#FFFFFF",   // main background
          "base-300": "#F1F4F9",   // table headers

          /* Text */
          "base-content": "#1E293B",

          /* States */
          info: "#0EA5E9",
          success: "#22C55E",
          warning: "#F59E0B",
          error: "#EF4444",

          /* Custom */
          "--base-hover": "#CADCFF",
          "--sidebar-active": "#E0EAFF",
          "--border-color": "#E2E8F0",
          "--title": "#1E293B",
          "--border-shadow": "#E3E3E3",
          "--shadow-color": "rgba(15,23,42,0.08)",
          "--blue-text": "#2A78D7",
          "--green-text": "#51B975",
          "--red-text": "rgb(209, 88, 88)",
          "--orange-text": "rgb(210, 150, 80)",
          "--desactivate": "#e4e4e4"
        },

        moon: {
          /* Brand */
          primary: "#3B82F6",
          "primary-content": "#FFFFFF",

          secondary: "#1E293B",
          accent: "#22C55E",

          neutral: "#0F172A",

          /* Backgrounds */
          "base-100": "#111827",   // cards
          "base-200": "#172033",   // main background ##172033
          "base-300": "#111827",   // headers/table

          /* Text */
          "base-content": "#F8FAFC",

          /* States */
          info: "#38BDF8",
          success: "#22C55E",
          warning: "#F59E0B",
          error: "#F87171",

          /* Custom */
          "--base-hover": "#1E293B",
          "--sidebar-active": "rgba(59,130,246,0.18)",
          "--border-color": "rgba(148,163,184,0.15)",
          "--title": "#677996",
          "--border-shadow": "#2F333B96",
          "--shadow-color": "rgba(255, 255, 255, 0.1)",
          "--blue-text": "#60a5fa",
          "--green-text": "#bbf7d0",
          "--red-text": "#fecaca",
          "--orange-text": "#fed7aa",
          "--desactivate": "#404a5e"
        },
      },
    ],
  },
}