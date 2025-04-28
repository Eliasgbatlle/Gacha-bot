import { useEffect, useState } from 'react';

export default function Servers() {
    const [menuOpen, setMenuOpen] = useState(false);
    const [selectedServer, setSelectedServer] = useState('Seleccione servidor');
    const [servers, setServers] = useState<string[]>([]);

    useEffect(() => {
        async function fetchServers() {
            try {
                const response = await fetch('/api/gacha/servers');
                const data = await response.json();
                setServers(data.servers);
            } catch (error) {
                console.error('Error al obtener los servidores:', error);
            }
        }
        fetchServers();
    }, []);

    return (
        <div className="relative">
            <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="bg-gray-700 text-white font-medium h-10 w-70 py-2 px-4 rounded-lg shadow-md flex justify-between items-center hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
                <span className="truncate">{selectedServer}</span>
                <svg className="w-5 h-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            {menuOpen && (
                <div className="absolute top-full right-0 mt-2 w-70 bg-gray-700 rounded-md shadow-lg py-1 z-10">
                    {servers && servers.length > 0 ? (
                        servers.map((server) => (
                            <button
                                key={server}
                                onClick={() => {
                                    setSelectedServer(server);
                                    setMenuOpen(false);
                                }}
                                className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left"
                            >
                                {server}
                            </button>
                        ))
                    ) : (
                        <div className="px-4 py-2 text-sm text-gray-400">No hay servidores disponibles</div>
                    )}
                </div>
            )}
        </div>
    );
}