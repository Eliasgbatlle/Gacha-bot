/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
      remotePatterns: [
        {
          protocol: 'https',
          hostname: 'cdn.discordapp.com',
        },
        {
          protocol: 'https',
          hostname: 'cdn.myanimelist.net',
        },
      ],
      domains: ['img.icons8.com'], // Agregar el dominio permitido
    },
  };
  
  export default nextConfig;