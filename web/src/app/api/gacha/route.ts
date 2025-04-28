import { NextResponse } from 'next/server';
import path from 'path';

// Rutas a las bases de datos
const gachaDbPath = path.resolve(process.cwd(), '../gacha_data.db');
const personajesDbPath = path.resolve(process.cwd(), '../personajes.db');

export async function GET() {
    try {
        const Database = (await import('better-sqlite3')).default;

        // Conectar a gacha_data.db
        const gachaDb = new Database(gachaDbPath, { readonly: true });
        const characters = gachaDb.prepare('SELECT * FROM characters').all();
        const users = gachaDb.prepare('SELECT * FROM users').all();
        gachaDb.close();

        // Conectar a personajes.db
        const personajesDb = new Database(personajesDbPath, { readonly: true });
        const personajes = personajesDb.prepare('SELECT id, nombre, genero, imagen, serie, rareza, precio FROM personajes').all();
        const top = personajesDb.prepare('SELECT * FROM top').all();
        personajesDb.close();

        return NextResponse.json({ characters, users, personajes, top });
    } catch (error) {
        console.error('Error al consultar las bases de datos:', error);
        const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
        return NextResponse.json({ error: 'Error al consultar las bases de datos', details: errorMessage }, { status: 500 });
    }
}