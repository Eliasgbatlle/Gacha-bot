'use client';

import {
  HomeIcon,
  CogIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  ViewGridIcon,
  MenuIcon,
  XIcon,
} from '@heroicons/react/outline';
import { useSession, signOut } from 'next-auth/react';
import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

const navItems = [
  { path: '/', label: 'Inicio', icon: HomeIcon },
  { path: '/menu', label: 'Dashboard', icon: ViewGridIcon },
  { path: '/gacha', label: 'Gacha', icon: ChartBarIcon },
  { path: '/economia', label: 'Economía', icon: CurrencyDollarIcon },
  { path: '/ranking', label: 'Ranking', icon: UserGroupIcon },
  { path: '/configuracion', label: 'Configuración', icon: CogIcon },
];

export default function Sidebar() {
  const { data: session } = useSession();
  const router = useRouter();
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(true);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const isActive = (path: string) => pathname === path;

  // Cierra el dropdown si se colapsa el sidebar
  const toggleMenu = () => {
    setMenuOpen((prev) => {
      if (prev) setDropdownOpen(false);
      return !prev;
    });
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.dropdown') && dropdownOpen) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownOpen]);

  return (
    <aside
      className={`bg-gray-800 h-screen p-4 flex flex-col transition-all duration-300 ${
        menuOpen ? 'w-64' : 'w-20'
      }`}
    >
      {/* Encabezado */}
      <div className={`flex ${menuOpen ? 'justify-between' : 'justify-center'} items-center mb-6`}>
        {menuOpen && (
          <h1
            onClick={() => router.push('/')}
            className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-600 text-transparent bg-clip-text cursor-pointer whitespace-nowrap"
          >
            Gacha Bot
          </h1>
        )}
        <button onClick={toggleMenu} className="text-white">
          {menuOpen ? <XIcon className="w-6 h-6" /> : <MenuIcon className="w-6 h-6" />}
        </button>
      </div>

      {/* Navegación */}
      <nav className="flex flex-col gap-4">
        {navItems.map(({ path, label, icon: Icon }) => (
          <button
            key={path}
            onClick={() => router.push(path)}
            className={`group relative flex items-center ${
              menuOpen ? 'gap-3 justify-start' : 'justify-center'
            } px-2 py-2 rounded-md
            ${
              isActive(path)
                ? 'text-indigo-400 bg-gray-700'
                : 'text-gray-300 hover:text-indigo-400 hover:bg-gray-700'
            }`}
            disabled={isActive(path)}
          >
            <Icon className="w-5 h-5" />
            {menuOpen && <span className="text-sm">{label}</span>}
            {!menuOpen && (
              <span className="absolute left-full ml-2 whitespace-nowrap bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition">
                {label}
              </span>
            )}
          </button>
        ))}
      </nav>

      {/* Usuario */}
      <div
        className={`mt-auto flex items-center ${
          menuOpen ? 'gap-3 justify-start' : 'justify-center'
        } bg-gray-700 p-2 rounded-lg cursor-pointer relative`}
        onClick={() => setDropdownOpen(!dropdownOpen)}
      >
        <div className="w-10 h-10 flex-shrink-0 rounded-full overflow-hidden bg-gray-600">
          {session?.user?.image && (
            <img
              src={session.user.image}
              alt="Avatar"
              className="w-full h-full object-cover" // Asegura que la imagen mantenga sus proporciones
            />
          )}
        </div>
        {menuOpen && (
          <div>
            <p className="text-sm font-bold text-white">{session?.user?.name || 'Usuario'}</p>
            <p className="text-xs text-gray-400">{session?.user?.email || 'Correo no disponible'}</p>
          </div>
        )}
      </div>

      {/* Menú desplegable de usuario */}
      {dropdownOpen && menuOpen && (
        <div className="absolute bottom-20 left-4 w-56 bg-gray-700 rounded-md shadow-lg py-1 z-50">
          <button
            onClick={() => router.push('/settings')}
            className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left"
          >
            Configuración
          </button>
          <button
            onClick={() => signOut({ callbackUrl: '/' })}
            className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 w-full text-left"
          >
            Cerrar sesión
          </button>
        </div>
      )}
    </aside>
  );
}
