import { NextResponse } from 'next/server';
import path from 'path';

const gachaDbPath = path.resolve(process.cwd(), '../gacha_data.db');

export async function GET() {
    try {
        const Database = (await import('better-sqlite3')).default;
        const db = new Database(gachaDbPath, { readonly: true });

        const servers = db.prepare('SELECT DISTINCT server_id FROM users').all();
        return NextResponse.json({ servers: servers.map((row: { server_id: string }) => `Servidor ${row.server_id}`) });
    } catch (error) {
        console.error('Error al obtener los servidores:', error);
        return NextResponse.json({ error: 'Error al obtener los servidores' }, { status: 500 });
    }
}