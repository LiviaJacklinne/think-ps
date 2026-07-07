import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0f766e",
          dark: "#115e59",
          soft: "#ccfbf1",
        },
      },
      boxShadow: {
        panel: "0 14px 32px rgba(15, 23, 42, 0.06)",
        toast: "0 14px 32px rgba(15, 23, 42, 0.18)",
      },
    },
  },
  plugins: [],
};

export default config;
