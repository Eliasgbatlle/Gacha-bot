"use client";

import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/sidebar';
import Servers from '@/components/Servers';

export default function Dashboard() {
    const { data: session } = useSession();
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

    return (
        <div className="min-h-screen bg-gray-900 text-white flex">
            <Sidebar />

            {/* Main Content */}
            <main className="flex-1 p-6">
                <header className="flex justify-between items-center mb-6">
                    <h2 className="text-3xl font-bold">Bienvenido al Dashboard</h2>
                </header>

                {/* Sections */}
                <section className="mb-6">
                    <h3 className="text-xl font-bold mb-4">Estadísticas</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h4 className="text-lg font-bold">Personajes Coleccionados</h4>
                            <p className="text-2xl font-bold text-indigo-400">45</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h4 className="text-lg font-bold">Dinero Acumulado</h4>
                            <p className="text-2xl font-bold text-indigo-400">$12,345</p>
                        </div>
                        <div className="bg-gray-800 p-4 rounded-lg">
                            <h4 className="text-lg font-bold">Ranking Global</h4>
                            <p className="text-2xl font-bold text-indigo-400">#23</p>
                        </div>
                    </div>
                </section>

                <section className="mb-6">
                    <h3 className="text-xl font-bold mb-4">Acciones Rápidas</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <button className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-lg">Realizar Gacha</button>
                        <button className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-lg">Reclamar Recompensa Diaria</button>
                        <button className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-lg">Ver Ranking</button>
                        <button className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-lg">Gestionar Economía</button>
                    </div>
                </section>

                <section>
                    <h3 className="text-xl font-bold mb-4">Últimos Eventos</h3>
                    <div className="bg-gray-800 p-4 rounded-lg">
                        <p className="text-gray-400">No hay eventos recientes.</p>
                    </div>
                </section>
            </main>

            <div className="absolute top-6 right-6">
                <Servers />
            </div>

            <style jsx>{`
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
                            `}</style>
        </div>
    );
}