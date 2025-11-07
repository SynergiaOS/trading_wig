// Production configuration
export const PRODUCTION_CONFIG = {
  API_URL: process.env.VITE_API_URL || 'http://localhost:8000',
  DATA_SOURCE: process.env.VITE_DATA_SOURCE || 'api',
  REFRESH_INTERVAL: parseInt(process.env.VITE_REFRESH_INTERVAL || '30000', 10),
};

