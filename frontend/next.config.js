/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
      return [
        {
          source: "/patient-dashboard",
          destination: "/app/pages/patient-dashboard",
        },
      ];
    },
  };
  
  module.exports = nextConfig;
  