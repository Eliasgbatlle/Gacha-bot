import React from 'react';
import { useSession, signIn, signOut } from "next-auth/react";

export default function Home() {
  const { data: session } = useSession();

  return (
    <main>
      {session ? (
        <>
          <p>Bienvenido, {session.user?.name}</p>
          <button onClick={() => signOut()}>Cerrar sesión</button>
        </>
      ) : (
        <button onClick={() => signIn("discord")}>Iniciar sesión con Discord</button>
      )}
    </main>
  );
}
