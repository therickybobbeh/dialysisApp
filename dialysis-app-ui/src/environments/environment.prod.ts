declare global {
  interface Window {
    __env: any;
  }
}

export const environment = {
  production: true,
  apiUrl: window.__env?.apiUrl || 'http://pd-management-backend',
  enableDebug: window.__env?.enableDebug || false
};