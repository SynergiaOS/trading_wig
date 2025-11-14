/**
 * Backend Service
 * Handles communication with backend API for health checks and stats
 */

const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface BackendHealth {
  status: 'healthy' | 'degraded' | 'down';
  timestamp?: string;
  uptime?: number;
  version?: string;
}

export interface BackendStats {
  totalRequests?: number;
  averageResponseTime?: number;
  lastUpdate?: string;
  dataSource?: string;
}

export async function checkBackendHealth(): Promise<BackendHealth | null> {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    if (!response.ok) {
      return { status: 'down' };
    }

    const data = await response.json();
    return {
      status: data.status === 'ok' || data.status === 'healthy' ? 'healthy' : 'degraded',
      timestamp: data.timestamp,
      uptime: data.uptime,
      version: data.version,
    };
  } catch (error) {
    console.error('Backend health check failed:', error);
    return { status: 'down' };
  }
}

export async function getBackendStats(): Promise<BackendStats | null> {
  try {
    const response = await fetch(`${BACKEND_URL}/stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Backend stats fetch failed:', error);
    return null;
  }
}

