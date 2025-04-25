"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, Gem, Users, Trophy, Disc3 } from 'lucide-react';
import { useSession, signIn } from 'next-auth/react';


interface Character {
    id: number;
    name: string;
    image?: string;
    rarity?: string;
}

interface User {
    id: number;
    username: string;
    avatar?: string;
}

interface Personaje {
    id: number;
    name: string;
    votes: number;
    image?: string;
}

interface GachaData {
    characters?: Character[];
    users?: User[];
    personajes?: Personaje[];
    top?: Personaje[];
}

export default function HomePage() {
    const [data, setData] = useState<GachaData>({
        characters: [],
        users: [],
        personajes: [],
        top: []
    });
    const [error, setError] = useState<string | null>(null);
    const { data: session } = useSession();

    useEffect(() => {
        fetch('/api/gacha')
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Error al obtener los datos');
                }
                return response.json();
            })
            .then((apiData) => {
                // Limpieza de datos
                const cleanData = {
                    characters: (apiData.characters || []).filter((c: Character) => c?.name),
                    users: apiData.users || [],
                    personajes: apiData.personajes || [],
                    top: (apiData.top || []).filter((p: Personaje) => p?.name)
                };
                console.log('Datos recibidos de la API:', cleanData);
                setData(cleanData);
            })
            .catch((error) => setError(error.message));
    }, []);

    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

    return (
        <div className="pt-16 min-h-screen">
            {/* Hero Section */}
            <section className="relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
                
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="text-center"
                    >
                        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-indigo-400 to-purple-600 gradient-text">
                            Colecciona Personajes Épicos
                        </h1>
                        <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto mb-10">
                            Un bot de Discord donde puedes coleccionar personajes, competir con amigos y subir en el ranking.
                        </p>
                        
                        <div className="flex flex-col sm:flex-row justify-center gap-4">
                            <motion.a
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                href="#play-now"
                                className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-white font-bold text-lg transition-colors flex items-center justify-center gap-2"
                            >
                                Jugar Ahora <ChevronRight className="w-5 h-5" />
                            </motion.a>
                            
                            {!session && (
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => signIn("discord")}
                                    className="px-8 py-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-white font-bold text-lg transition-colors flex items-center justify-center gap-2"
                                >
                                    <Disc3 className="w-5 h-5" /> Conectar Discord
                                </motion.button>
                            )}
                        </div>
                    </motion.div>
                </div>
                
                {/* Floating characters */}
                {data.characters && data.characters?.length > 0 && (
                    <div className="absolute top-1/2 left-0 right-0 -translate-y-1/2 pointer-events-none">
                        {data.characters.slice(0, 5).map((character, index) => (
                            <motion.div
                                key={character?.id || index}
                                initial={{ opacity: 0, y: 50 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.2 }}
                                className={`absolute float-animation`}
                                style={{
                                    left: `${10 + index * 15}%`,
                                    animationDelay: `${index * 0.5}s`
                                }}
                            >
                                <div className="bg-indigo-500/20 p-4 rounded-full backdrop-blur-md border border-indigo-400/30">
                                    {character.image ? (
                                    <div className="w-16 h-16 md:w-24 md:h-24 rounded-full overflow-hidden border-2 border-indigo-400">
                                        <img 
                                        src={character.image} 
                                        alt={character.name}
                                        className="w-full h-full object-cover"
                                        />
                                    </div>
                                    ) : (
                                    <div className="w-16 h-16 md:w-24 md:h-24 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                                        {character.name.charAt(0)}
                                    </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </section>

            {/* Features Section */}
            <section className="py-20 bg-gradient-to-b from-gray-900/50 to-indigo-900/20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        transition={{ duration: 0.8 }}
                        viewport={{ once: true }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white">
                            ¿Qué puedes hacer con Gacha Bot?
                        </h2>
                        <p className="text-lg text-gray-400 max-w-3xl mx-auto">
                            Descubre todas las emocionantes características que te esperan
                        </p>
                    </motion.div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: <Gem className="w-10 h-10 text-yellow-400" />,
                                title: "Colecciona Personajes",
                                description: "Obtén personajes raros y completa tu colección"
                            },
                            {
                                icon: <Users className="w-10 h-10 text-blue-400" />,
                                title: "Compite con Amigos",
                                description: "Compara tu colección con otros jugadores"
                            },
                            {
                                icon: <Trophy className="w-10 h-10 text-purple-400" />,
                                title: "Sube en el Ranking",
                                description: "Lucha por estar en el top de jugadores"
                            }
                        ].map((feature, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="bg-gray-800/50 card-hover-effect rounded-xl p-8 border border-gray-700/50"
                            >
                                <div className="mb-6">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                                <p className="text-gray-400">{feature.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Characters Section */}
            {data.characters && data.characters?.length > 0 && (
                <section id="play-now" className="py-20">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <motion.div
                            initial={{ opacity: 0 }}
                            whileInView={{ opacity: 1 }}
                            transition={{ duration: 0.8 }}
                            viewport={{ once: true }}
                            className="text-center mb-16"
                        >
                            <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white">
                                Personajes Disponibles
                            </h2>
                            <p className="text-lg text-gray-400 max-w-3xl mx-auto">
                                Colecciona todos los personajes y completa tu álbum
                            </p>
                        </motion.div>
                        
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                            {data.characters.map((character, index) => (
                                <motion.div
                                    key={character?.id || index}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    whileInView={{ opacity: 1, scale: 1 }}
                                    whileHover={{ y: -10 }}
                                    transition={{ duration: 0.3, delay: index * 0.05 }}
                                    viewport={{ once: true }}
                                    className="bg-gray-800/50 card-hover-effect rounded-xl p-6 border border-gray-700/50 flex flex-col items-center"
                                >
                                        {character.image ? (
                                        <div className="w-16 h-16 md:w-24 md:h-24 rounded-full overflow-hidden border-2 border-indigo-400">
                                            <img 
                                            src={character.image} 
                                            alt={character.name}
                                            className="w-full h-full object-cover"
                                            />
                                        </div>
                                        ) : (
                                        <div className="w-16 h-16 md:w-24 md:h-24 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                                            {character.name.charAt(0)}
                                        </div>
                                        )}
                                    <h3 className="text-lg font-medium text-white mb-1">{character.name || 'Sin nombre'}</h3>
                                    <span className="text-sm text-indigo-400">{character.rarity || "Común"}</span>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>
            )}

            {/* Top Players Section */}
            {data.top && data.top.length > 0 && (
                <section className="py-20 bg-gradient-to-b from-indigo-900/20 to-gray-900/50">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <motion.div
                            initial={{ opacity: 0 }}
                            whileInView={{ opacity: 1 }}
                            transition={{ duration: 0.8 }}
                            viewport={{ once: true }}
                            className="text-center mb-16"
                        >
                            <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white">
                                Ranking de Jugadores
                            </h2>
                            <p className="text-lg text-gray-400 max-w-3xl mx-auto">
                                Los mejores jugadores de la comunidad
                            </p>
                        </motion.div>
                        
                        <div className="max-w-3xl mx-auto bg-gray-800/50 rounded-xl overflow-hidden border border-gray-700/50">
                            {data.top.map((player, index) => (
                                <motion.div
                                    key={player?.id || index}
                                    initial={{ opacity: 0, x: -20 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.5, delay: index * 0.1 }}
                                    viewport={{ once: true }}
                                    className={`flex items-center justify-between p-6 ${index % 2 === 0 ? 'bg-gray-800/30' : ''}`}
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="text-2xl font-bold text-indigo-400 w-8">{index + 1}</div>
                                        <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                                            {player.name.charAt(0) || '?'}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-medium text-white">{player.name || 'Jugador anónimo'}</h3>
                                            <p className="text-sm text-gray-400">{player.votes ?? 0} votos</p>
                                        </div>
                                    </div>
                                    {index < 3 && (
                                        <div className="w-6 h-6 flex items-center justify-center">
                                            {index === 0 && <Trophy className="w-5 h-5 text-yellow-400" />}
                                            {index === 1 && <Trophy className="w-5 h-5 text-gray-300" />}
                                            {index === 2 && <Trophy className="w-5 h-5 text-amber-600" />}
                                        </div>
                                    )}
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>
            )}

            {/* CTA Section */}
            <section className="py-20 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('/grid-dark.svg')] bg-center opacity-20"></div>
                
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        viewport={{ once: true }}
                        className="bg-gradient-to-r from-indigo-900/50 to-purple-900/50 rounded-2xl p-8 md:p-12 border border-indigo-500/30 text-center"
                    >
                        <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white">
                            ¿Listo para comenzar?
                        </h2>
                        <p className="text-lg text-gray-300 max-w-2xl mx-auto mb-8">
                            Únete a la comunidad de Gacha Bot y comienza tu aventura de colección hoy mismo.
                        </p>
                        
                        <motion.div
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="inline-block"
                        >
                            {session ? (
                                <a
                                    href="#play-now"
                                    className="px-8 py-4 bg-white hover:bg-gray-100 rounded-lg text-gray-900 font-bold text-lg transition-colors flex items-center justify-center gap-2 mx-auto"
                                >
                                    Jugar Ahora <ChevronRight className="w-5 h-5" />
                                </a>
                            ) : (
                                <button
                                    onClick={() => signIn("discord")}
                                    className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-white font-bold text-lg transition-colors flex items-center justify-center gap-2 mx-auto"
                                >
                                    <Disc3 className="w-5 h-5" /> Conectar con Discord
                                </button>
                            )}
                        </motion.div>
                    </motion.div>
                </div>
            </section>
        </div>
    );
}
