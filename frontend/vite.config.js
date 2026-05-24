import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/products": "http://localhost:8001",
      "/categories": "http://localhost:8001",
      "/carts": "http://localhost:8001",
      "/orders": "http://localhost:8001",
      "/register": "http://localhost:8001",
      "/login": "http://localhost:8001",
      "/logout": "http://localhost:8001",
      "/profile": "http://localhost:8001",
      "/password_reset": "http://localhost:8001",
      "/set_new_password": "http://localhost:8001",
      "/media": "http://localhost:8001"
    }
  }
});
