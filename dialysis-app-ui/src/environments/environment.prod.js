(function(window) {
  window.__env = window.__env || {};
  
  // API URL with fallback
  const apiUrl = '${API_URL}' !== '${' + 'API_URL}' ? '${API_URL}' : 'http://pd-management-backend';
  window.__env.apiUrl = apiUrl;
  
  // Whether or not to enable debug mode
  window.__env.enableDebug = false;

  console.log('Environment configuration loaded with API URL:', window.__env.apiUrl);
})(this);