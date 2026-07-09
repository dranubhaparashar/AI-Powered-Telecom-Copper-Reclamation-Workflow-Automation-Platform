export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {
    fontFamily: { sans: ["Inter", "ui-sans-serif", "system-ui"] },
    colors: { ink: "#09090B", panel: "#111114", panel2: "#18181B", line: "#27272A", accent: "#FF6F20" }
  } },
  plugins: []
};
