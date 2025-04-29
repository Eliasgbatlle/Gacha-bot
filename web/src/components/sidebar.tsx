import { useSession, signOut } from 'next-auth/react';
import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { HomeIcon, CogIcon, ChartBarIcon, CurrencyDollarIcon, UserGroupIcon, ViewGridIcon } from '@heroicons/react/outline';

export default function Sidebar() {
    const { data: session } = useSession();
    const [menuOpen, setMenuOpen] = useState(false);
    const router = useRouter();
    const pathname = usePathname();

    // Agregar lógica para deshabilitar y cambiar el color del botón dependiendo de la página actual
    const isActive = (path: string) => pathname === path;

    return (
        <aside className="w-64 bg-gray-800 p-6 flex flex-col gap-6">
            <div className="flex items-center gap-4">
                <h1
                    onClick={() => router.push('/')}
                    className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-600 gradient-text cursor-pointer"
                >
                    Gacha Bot
                </h1>
            </div>
            <nav className="flex flex-col gap-4">
                <button
                    onClick={() => router.push('/')}
                    className={`text-left flex items-center gap-2 ${isActive('/') ? 'text-indigo-400 cursor-default' : 'text-gray-300 hover:text-indigo-400'}`}
                    disabled={isActive('/')}
                >
                    <HomeIcon className="w-5 h-5" />
                    inicio
               </button>
                <button
                    onClick={() => router.push('/menu')}
                    className={`text-left flex items-center gap-2 ${isActive('/menu') ? 'text-indigo-400 cursor-default' : 'text-gray-300 hover:text-indigo-400'}`}
                    disabled={isActive('/menu')}
                >
                    <ViewGridIcon className="w-5 h-5" />
                    Dashboard
                </button>
                <button
                    className={`text-left flex items-center gap-2 ${isActive('/gacha') ? 'text-indigo-400 cursor-default' : 'text-gray-300 hover:text-indigo-400'}`}
                    disabled={isActive('/gacha')}
                >
                    <ChartBarIcon className="w-5 h-5" /> Gacha
                </button>
                <button
                    className={`text-left flex items-center gap-2 ${isActive('/economia') ? 'text-indigo-400 cursor-default' : 'text-gray-300 hover:text-indigo-400'}`}
                    disabled={isActive('/economia')}
                >
                    <CurrencyDollarIcon className="w-5 h-5" /> Economía
                </button>
                <button
                    className={`text-left flex items-center gap-2 ${isActive('/ranking') ? 'text-indigo-400 cursor-default' : 'text-gray-300 hover:text-indigo-400'}`}
                    disabled={isActive('/ranking')}
                >
                    <UserGroupIcon className="w-5 h-5" /> Ranking
                </button>
                <button
                    className={`text-left flex items-center gap-2 ${isActive('/configuracion') ? 'text-indigo-400 cursor-default' : 'text-gray-300 hover:text-indigo-400'}`}
                    disabled={isActive('/configuracion')}
                >
                    <CogIcon className="w-5 h-5" /> Configuración
                </button>
            </nav>
            <div className="mt-auto flex items-center gap-4 bg-gray-700 p-4 rounded-lg cursor-pointer relative" onClick={() => setMenuOpen(!menuOpen)}>
                {session?.user?.image && (
                    <img
                        src={session.user.image}
                        alt="User Avatar"
                        className="w-10 h-10 rounded-full"
                    />
                )}
                <div>
                    <p className="text-sm font-bold text-white">{session?.user?.name || 'Usuario'}</p>
                    <p className="text-xs text-gray-400">{session?.user?.email || 'Correo no disponible'}</p>
                </div>
                {menuOpen && (
                    <div className="absolute bottom-full right-0 mb-2 w-54.5 bg-gray-700 rounded-md shadow-lg py-1 z-10 transition-transform transform scale-95 origin-bottom-right" style={{ animation: 'fadeIn 0.2s ease-out forwards' }}>
                        <button
                            onClick={() => router.push('/settings')}
                            className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left flex items-center gap-2"
                        >
                            <span className="icon-settings"></span> Configuración
                        </button>
                        <button
                            onClick={() => signOut({ callbackUrl: '/' })}
                            className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left flex items-center gap-2"
                        >
                            <span className="icon-logout"></span> Cerrar sesión
                        </button>
                    </div>
                )}
            </div>
        </aside>
    );
}