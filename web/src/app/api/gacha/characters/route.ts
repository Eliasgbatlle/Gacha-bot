import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/utils/authOptions';
import { NextResponse } from 'next/server';
import path from 'path';

const gachaDbPath = path.resolve(process.cwd(), '../gacha_data.db');

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const server = searchParams.get('server');

    if (!server) {
        return NextResponse.json({ error: 'Servidor no especificado' }, { status: 400 });
    }

    try {
        const Database = (await import('better-sqlite3')).default;
        const db = new Database(gachaDbPath, { readonly: true });

        const session = await getServerSession(authOptions);
        if (!session || !session.user) {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }

        const userId = session.user.id;

        const count = db.prepare(
            `SELECT COUNT(*) as count 
             FROM characters 
             WHERE server_id = (SELECT server_id FROM servers WHERE server_name = ?) 
             AND owner_id = ?`
        ).get(server, userId)?.count || 0;

        return NextResponse.json({ count });
    } catch (error) {
        console.error('Error al obtener los personajes:', error);
        return NextResponse.json({ error: 'Error al obtener los personajes' }, { status: 500 });
    }
}