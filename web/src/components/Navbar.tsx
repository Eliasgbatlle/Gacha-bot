"use client";

import { motion } from "framer-motion";
import { signIn, signOut, useSession } from "next-auth/react";
import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function Navbar() {
    const { data: session } = useSession();
    const pathname = usePathname();
    const router = useRouter();
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as HTMLElement | null;
            if (target && !target.closest('.relative')) {
                setMenuOpen(false);
            }
        };

        document.addEventListener('click', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, []);

    if (pathname === '/menu') return null; // Oculta el Navbar en la página del menú

    return (
        <nav className="w-full fixed top-0 z-50 backdrop-blur-md bg-black/50 border-b border-indigo-500/20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5 }}
                        className="flex-shrink-0 flex items-center"
                    >
                        <h1
                            onClick={() => router.push('/')} // Redirige al inicio al hacer clic
                            className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-600 gradient-text cursor-pointer"
                        >
                            Gacha Bot
                        </h1>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5 }}
                        className="relative"
                    >
                        {session ? (
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => router.push('/servers')} // Redirige a servidores
                                    className="px-4 py-2 text-white font-medium transition-colors"
                                >
                                    Servidores
                                </button>
                                {session && (
                                    <button
                                        onClick={() => router.push('/menu')} // Redirige al dashboard
                                        className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white font-medium transition-colors"
                                    >
                                        Dashboard
                                    </button>
                                )}
                                {session.user?.image && (
                                    <div className="relative">
                                        <Image
                                            src={session.user.image}
                                            alt="User Avatar"
                                            width={40}
                                            height={40}
                                            className="w-8 h-8 rounded-full cursor-pointer"
                                            onClick={() => setMenuOpen(!menuOpen)}
                                        />
                                        {menuOpen && (
                                            <div className="absolute top-full right-0 mt-5 w-64 bg-gray-700 rounded-md shadow-lg py-2 z-10 transition-transform transform scale-95 origin-top-right" style={{ animation: 'fadeInDown 0.2s ease-out forwards' }}>
                                                <div className="px-4 py-2 border-b border-gray-600">
                                                    <p className="text-sm font-bold text-white">{session.user.name}</p>
                                                    <p className="text-xs text-gray-400">{session.user.email}</p>
                                                </div>
                                                <button
                                                    onClick={() => router.push('/settings')} // Redirige a configuración
                                                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left flex items-center gap-2"
                                                >
                                                    <span className="icon-settings"></span> Configuración
                                                </button>
                                                <button
                                                    onClick={() => signOut()}
                                                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left flex items-center gap-2"
                                                >
                                                    <span className="icon-logout"></span> Cerrar sesión
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <button
                                onClick={() => signIn("discord")}
                                className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white font-medium transition-colors flex items-center gap-2"
                            >
                                Iniciar con Discord
                            </button>
                        )}
                    </motion.div>
                </div>
            </div>

            <style jsx>{`
                                            @keyframes fadeInDown {
                                                from {
                                                    opacity: 0;
                                                    transform: translateY(-10px) scale(0.95);
                                                }
                                                to {
                                                    opacity: 1;
                                                    transform: translateY(0) scale(1);
                                                }
                                            }
                                        `}</style>
        </nav>
    );
}