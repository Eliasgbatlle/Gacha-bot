"use client";

import { motion } from "framer-motion";
import { signIn, signOut, useSession } from "next-auth/react";
import { DiscordLogoIcon } from "@radix-ui/react-icons";
import Image from 'next/image';

export default function Navbar() {
  const { data: session } = useSession();

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
            <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-600 gradient-text">
              Gacha Bot
            </h1>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            {session ? (
              <div className="flex items-center gap-4">
                <Image 
                  src={session.user?.image || ""} 
                  alt="User Avatar"
                  className="w-8 h-8 rounded-full"
                />
                <button
                  onClick={() => signOut()}
                  className="px-4 py-2 rounded-md bg-red-600 hover:bg-red-700 text-white font-medium transition-colors"
                >
                  Cerrar sesión
                </button>
              </div>
            ) : (
              <button
                onClick={() => signIn("discord")}
                className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white font-medium transition-colors flex items-center gap-2"
              >
                <DiscordLogoIcon className="w-5 h-5" />
                Iniciar con Discord
              </button>
            )}
          </motion.div>
        </div>
      </div>
    </nav>
  );
}