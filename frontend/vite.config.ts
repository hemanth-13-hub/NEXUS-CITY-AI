import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, process.cwd(), 'VITE_');
  const apiUrl = environment.VITE_API_URL?.trim();
  if (mode === 'production') {
    if (!apiUrl) {
      throw new Error('Set VITE_API_URL before building the frontend.');
    }
    if (new URL(apiUrl).protocol !== 'https:') {
      throw new Error('Production VITE_API_URL must use HTTPS.');
    }
  }

  return {
    plugins: [
      react(),
      VitePWA({
        registerType: 'autoUpdate',
        manifest: {
          name: 'NEXUS CITY AI',
          short_name: 'NEXUS CITY',
          description: 'Civic infrastructure reporting and monitoring',
          theme_color: '#07111f',
          background_color: '#07111f',
          display: 'standalone',
          scope: '/',
          start_url: '/',
          icons: [
            { src: '/pwa-192.svg', sizes: '192x192', type: 'image/svg+xml', purpose: 'any' },
            { src: '/pwa-512.svg', sizes: '512x512', type: 'image/svg+xml', purpose: 'any maskable' },
          ],
        },
        workbox: {
          navigateFallback: 'index.html',
          navigateFallbackDenylist: [/^\/api\//, /^\/uploads\//],
          globPatterns: ['**/*.{js,css,html,svg,woff2}'],
          runtimeCaching: [],
        },
      }),
    ],
    server: { host: '127.0.0.1' },
  };
});
