import { NextResponse } from 'next/server';
import path from 'path';

const gachaDbPath = path.resolve(process.cwd(), '../gacha_data.db');

export async function POST(request: Request) {
    try {
        const { server_name } = await request.json();

        if (!server_name) {
            return NextResponse.json({ error: 'El nombre del servidor no fue proporcionado.' }, { status: 400 });
        }

        const Database = (await import('better-sqlite3')).default;
        const db = new Database(gachaDbPath, { readonly: true });

        const serverData = db.prepare(
            `SELECT server_id FROM servers WHERE server_name = ?`
        ).get(server_name);

        if (!serverData) {
            return NextResponse.json({ error: 'No se encontró un servidor con el nombre proporcionado.' }, { status: 404 });
        }

        return NextResponse.json({ server_id: serverData.server_id });
    } catch (error) {
        console.error('Error al obtener el ID del servidor:', error);
        return NextResponse.json({ error: 'Error al obtener el ID del servidor.' }, { status: 500 });
    }
}