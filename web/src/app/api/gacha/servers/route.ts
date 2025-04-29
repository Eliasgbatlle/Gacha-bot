import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/utils/authOptions';
import path from 'path';

const gachaDbPath = path.resolve(process.cwd(), '../gacha_data.db');

export async function GET() {
    try {
        const session = await getServerSession(authOptions);
        if (!session || !session.user) {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }

        const userId = session.user.id; // Asegúrate de que el ID del usuario esté disponible en la sesión
        console.log('User ID from session:', userId);

        const Database = (await import('better-sqlite3')).default;
        const db = new Database(gachaDbPath, { readonly: true });

        const servers = db.prepare(
            `SELECT DISTINCT s.server_name 
             FROM users u
             JOIN servers s ON u.server_id = s.server_id
             WHERE u.user_id = ?`
        ).all(userId);

        return NextResponse.json({ servers: servers.map((row: { server_name: string }) => row.server_name) });
    } catch (error) {
        console.error('Error al obtener los servidores:', error);
        return NextResponse.json({ error: 'Error al obtener los servidores' }, { status: 500 });
    }
}