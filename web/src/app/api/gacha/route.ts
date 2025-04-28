import { NextResponse } from 'next/server';
import path from 'path';

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const userId = searchParams.get('userId');
        const serverId = searchParams.get('serverId');

        const Database = (await import('better-sqlite3')).default;

        if (userId && serverId) {
            // Lógica para /menu/page.tsx usando gacha_data.db
            const gachaDbPath = path.resolve(process.cwd(), '../gacha_data.db');
            const gachaDb = new Database(gachaDbPath, { readonly: true });

            const user = gachaDb
                .prepare('SELECT nombre, nivel, experiencia FROM users WHERE user_id = ? AND server_id = ?')
                .get(userId, serverId);
            const characters = gachaDb
                .prepare('SELECT name, rarity, image_url FROM characters WHERE owner_id = ? AND server_id = ?')
                .all(userId, serverId);

            gachaDb.close();

            return NextResponse.json({ user, characters });
        } else {
            // Lógica para /page.tsx usando personajes.db
            const personajesDbPath = path.resolve(process.cwd(), '../personajes.db');
            const Database = (await import('better-sqlite3')).default;

            const personajesDb = new Database(personajesDbPath, { readonly: true });

            const personajes = personajesDb
                .prepare('SELECT id, nombre AS name, imagen AS image, rareza AS rarity, genero AS genre, serie AS series, precio AS price FROM personajes')
                .all();

            personajesDb.close();

            return NextResponse.json({ personajes });
        }
    } catch (error) {
        console.error('Error al consultar las bases de datos:', error);
        const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
        return NextResponse.json({ error: 'Error al consultar las bases de datos', details: errorMessage }, { status: 500 });
    }
}