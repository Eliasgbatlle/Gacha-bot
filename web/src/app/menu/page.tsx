"use client";

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { authOptions } from '@/app/utils/authOptions';
import Servers from '@/components/Servers';
import Roulette from '@/components/roulette';

type GlobalRanking = {
    rank: number;
    name: string;
    score?: number; // Agrega más propiedades según sea necesario
};

function formatNumberWithDots(number: number | null | undefined): string {
    if (number == null) return "0";
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

export default function game() {
    const { data: session } = useSession();
    const [selectedServer, setSelectedServer] = useState<string | null>(null);
    const [personajesColeccionados, setPersonajesColeccionados] = useState<number>(0);
    const [dineroAcumulado, setDineroAcumulado] = useState<number>(0);
    const [reputacion, setReputacion] = useState<number>(0);
    const [rankingScore, setRankingScore] = useState<number>(0);
    const [rankingPosition, setRankingPosition] = useState<number | null>(null);
    const [globalRanking, setGlobalRanking] = useState<GlobalRanking[]>([]);
    const [showRoulette, setShowRoulette] = useState(false);

    useEffect(() => {
        async function fetchPersonajes() {
            if (!selectedServer) return;

            try {
                const response = await fetch(`/api/gacha/characters?server=${selectedServer}`);
                const data = await response.json();
                setPersonajesColeccionados(data.count);
            } catch (error) {
                console.error('Error al obtener los personajes:', error);
            }
        }

        fetchPersonajes();
    }, [selectedServer]);

    useEffect(() => {
        async function fetchUserStats() {
            if (!selectedServer) return;

            try {
                const response = await fetch(`/api/gacha/user-stats?server=${selectedServer}`);
                const data = await response.json();
                console.log('Datos recibidos de /api/gacha/user-stats:', data);
                setDineroAcumulado(data.coins);
                setReputacion(data.reputation);
            } catch (error) {
                console.error('Error al obtener las estadísticas del usuario:', error);
            }
        }

        fetchUserStats();
    }, [selectedServer]);

    useEffect(() => {
        async function fetchRanking() {
            if (!selectedServer) return;

            try {
                const response = await fetch(`/api/gacha/server-ranking?server=${selectedServer}`);
                const data = await response.json();
                setRankingScore(data.playerScore);
                setRankingPosition(data.playerRank);
            } catch (error) {
                console.error('Error al obtener el ranking:', error);
            }
        }

        fetchRanking();
    }, [selectedServer]);

    useEffect(() => {
        async function fetchGlobalRanking() {
            try {
                const response = await fetch('/api/gacha/server-ranking');
                if (!response.ok) {
                    throw new Error('Error al obtener el ranking global');
                }
                const data = await response.json();
                setGlobalRanking(data.globalRankings || []);
            } catch (error) {
                console.error('Error al obtener el ranking global:', error);
            }
        }

        fetchGlobalRanking();
    }, []);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as HTMLElement | null;
            if (target && !target.closest('.relative')) {
                // setMenuOpen(false);
            }
        };
        

        document.addEventListener('click', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, []);

    useEffect(() => {
        const video = document.getElementById('background-video') as HTMLVideoElement | null;
        if (!video) return;

        video.addEventListener('ended', () => {
            video.currentTime = 0;
            video.play();
        });

        return () => {
            video.removeEventListener('ended', () => {
                video.currentTime = 0;
                video.play();
            });
        };
    }, []);

    const handleGirar = async () => {
        if (!selectedServer) {
            alert('Por favor, selecciona un servidor primero.');
            return;
        }

        if (!session || !session.user) {
            alert('No se pudo obtener la sesión del usuario. Por favor, inicia sesión.');
            return;
        }

        if (dineroAcumulado < 500) {
            alert('❌ No tienes suficientes monedas para tirar un roll. Necesitas 500 monedas.');
            return;
        }

        try {
            // Obtener el server_id desde el nuevo endpoint
            const serverIdResponse = await fetch("/api/discord/get-server-id", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ server_name: selectedServer }),
            });

            if (!serverIdResponse.ok) {
                throw new Error("Error al obtener el ID del servidor");
            }

            const { server_id } = await serverIdResponse.json();

            // Llamar a handleRoulette antes de verificar la respuesta
            await handleRoulette();

            const response = await fetch("http://127.0.0.1:8000/api/discord/girar", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-User-ID": session.user.id, // ID del usuario desde la sesión
                    "X-User-Name": session.user.name || "Usuario", // Nombre del usuario desde la sesión
                },
                body: JSON.stringify({
                    server_id: server_id, // Usar el server_id obtenido
                    source: 'web', // Indicar que la solicitud proviene de la web
                }),
            });

            if (!response.ok) {
                throw new Error("Error al ejecutar el comando girar");
            }

            const result = await response.json();
            if (result.message) {
                alert(`Resultado: ${result.message}`);
            } else {
                alert("No se recibió un mensaje válido del servidor.");
            }
        } catch (error) {
            console.error("Error al ejecutar girar:", error);
            alert("Hubo un error al ejecutar el comando girar.");
        }
    };

    const handleRecompensaDiaria = async () => {
        if (!selectedServer) {
            alert('Por favor, selecciona un servidor primero.');
            return;
        }

        if (!session || !session.user) {
            alert('No se pudo obtener la sesión del usuario. Por favor, inicia sesión.');
            return;
        }

        try {
            // Obtener el server_id desde el nuevo endpoint
            const serverIdResponse = await fetch("/api/discord/get-server-id", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ server_name: selectedServer }),
            });

            if (!serverIdResponse.ok) {
                throw new Error("Error al obtener el ID del servidor");
            }

            const { server_id } = await serverIdResponse.json();

            const response = await fetch('http://127.0.0.1:8000/api/recompensa-diaria', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: session.user.id, // Corrected parameter name
                    server_id: server_id, // Usar el server_id obtenido
                }),
            });

            const result = await response.json();
            if (result.error) {
                alert(result.message);
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Error al reclamar la recompensa diaria:', error);
            alert('Hubo un error al reclamar la recompensa diaria.');
        }
    };

    const handleRoulette = async () => {
        setShowRoulette(true);

        // Eliminar el cierre automático después de un tiempo
    };

    return (
        <div>
            <video loop autoPlay muted className="absolute top-0 left-0 w-full h-full object-cover z-0" id="background-video">
                <source src="https://res.cloudinary.com/dhjjcwtlk/video/upload/v1746249100/A_dramatic_anime_scene_where_a_female_samurai_stands_still_while_her_long_white_hair_flows_with_the_wind._Her_red_eyes_glow_subtly._The_background_flickers_with_mystical_blue_lights_and_faint_mist_moves_through_the_hmkoli.mp4" type="video/mp4" />
                Tu navegador no soporta la reproducción de videos.
            </video>

            {/* Main Content */}
            <main className="flex-1 p-6">
                <header className="flex justify-between items-center mb-6 absolute bottom-20 left-1/2 transform -translate-x-1/2">
                    <h2 className="text-3xl font-bold">Bienvenido al Dashboard</h2>
                </header>

                {/* Sections */}
                <section className="absolute bottom-4 left-4 z-20 mb-6 bg-transparent">
                    <div className="flex flex-col gap-4 items-start bg-transparent">
                        <div className="p-4 rounded-lg ranking-container">
                            <h4 className="text-sm font-bold">Ranking Servidor</h4>
                            <p className="text-lg font-bold text-indigo-400">{rankingPosition !== null ? `#${rankingPosition}` : 'N/A'}</p>
                        </div>
                        <div className="p-4 rounded-lg ranking-container">
                            <h4 className="text-sm font-bold">Ranking Global</h4>
                            <p className="text-lg font-bold text-indigo-400">{globalRanking && globalRanking.length > 0 ? `#${globalRanking[0].rank}` : 'N/A'}</p>
                        </div>
                    </div>
                </section>

                {/* Main Buttons */}
                <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 flex space-x-4 z-20">
                    <button onClick={handleGirar} className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg shadow-lg transform transition-transform duration-300 hover:scale-110">
                        Girar
                    </button>
                    <button onClick={handleRecompensaDiaria} className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg shadow-lg transform transition-transform duration-300 hover:scale-110">
                        Recompensa Diaria
                    </button>
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg shadow-lg transform transition-transform duration-300 hover:scale-110">
                        Ver Ranking
                    </button>
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg shadow-lg transform transition-transform duration-300 hover:scale-110">
                        Gestionar Economía
                    </button>
                </div>
            </main>

            {/* Top Bar */}
            <div className="top-bar">
                <div className="currency">
                    💵 <span>{formatNumberWithDots(dineroAcumulado)}</span>
                </div>
                <div className={`currency text-2xl font-bold ${reputacion < 0 ? 'text-red-500' : 'text-green-500'}`}>
                    ⚖️ <span>{formatNumberWithDots(reputacion)}</span>
                </div>
                <div className="currency">
                    👥 <span>{formatNumberWithDots(personajesColeccionados)}</span>
                </div>
            </div>

            {/* Servers Component */}
            <div className="absolute top-4 right-4">
                <Servers onSelectServer={(server: string) => setSelectedServer(server)} />
            </div>

            {showRoulette && (
                <div
                    className={`fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 animate-fade-in ${showRoulette ? 'backdrop-blur-md' : ''}`}
                    style={{ backgroundColor: 'transparent' }}
                >
                    <Roulette setShowRoulette={setShowRoulette} handleGirar={handleGirar} />
                </div>
            )}

            {/* 
            <section>
                <h3 className="text-xl font-bold mb-4">Últimos Eventos</h3>
                <div className="bg-gray-800 p-4 rounded-lg">
                    <p className="text-gray-400">No hay eventos recientes.</p>
                </div>
            </section>
            */}

            <style jsx>{`
                @keyframes fade-in {
                    from {
                        opacity: 0;
                        transform: scale(0.9);
                    }
                    to {
                        opacity: 1;
                        transform: scale(1);
                    }
                }

                .animate-fade-in {
                    animation: fade-in 0.5s ease-out;
                }

                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: scale(1);
                    }
                }
                .top-bar {
                    position: absolute;
                    top: 15px;
                    left: 50%;
                    transform: translateX(-50%);
                    display: flex;
                    gap: 20px;
                    background: rgba(0, 0, 0, 0.8);
                    padding: 8px 20px;
                    border-radius: 10px;
                    color: white;
                    font-size: 14px;
                    font-family: 'Segoe UI', sans-serif;
                }

                .currency {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-weight: bold;
                    font-family: "Segoe UI", sans-serif;
                    font-size: 16px;
                }

                .ranking-container {
                    width: 70px;
                    height: 70px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    margin-left: 0; /* Align to the left */
                    text-align: center; /* Center the text */
                    background: rgba(0, 0, 0, 0.8);
                }
            `}</style>
        </div>
    );
}