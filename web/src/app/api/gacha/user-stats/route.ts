import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/utils/authOptions';
import { NextResponse } from 'next/server';
import path from 'path';

const gachaDbPath = path.resolve(process.cwd(), '../gacha_data.db');

export async function GET(request: Request) {
    try {
        const session = await getServerSession(authOptions);
        if (!session || !session.user) {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }

        const userId = session.user.id;
        const searchParams = new URL(request.url).searchParams;
        const server = searchParams.get('server');

        if (!server) {
            return NextResponse.json({ error: 'Servidor no especificado' }, { status: 400 });
        }

        const Database = (await import('better-sqlite3')).default;
        const db = new Database(gachaDbPath, { readonly: true });

        const userStats = db.prepare(
            `SELECT u.coins, u.reputation 
             FROM users u
             JOIN servers s ON u.server_id = s.server_id
             WHERE u.user_id = ? AND s.server_name = ?`
        ).get(userId, server);

        if (!userStats) {
            console.warn(`No se encontraron estadísticas para el usuario ${userId} en el servidor ${server}`);
            return NextResponse.json({ coins: 0, reputation: 0, rankingScore: 0 });
        }

        const rankingScore = db.prepare(
            `SELECT 
                (SELECT SUM(value) FROM characters WHERE owner_id = u.user_id AND server_id = s.server_id) + 
                u.coins + 
                ABS(u.reputation) AS score
             FROM users u
             JOIN servers s ON u.server_id = s.server_id
             WHERE u.user_id = ? AND s.server_name = ?`
        ).get(userId, server)?.score || 0;

        return NextResponse.json({ coins: userStats.coins, reputation: userStats.reputation, rankingScore });
    } catch (error) {
        console.error('Error al obtener las estadísticas del usuario:', error);
        return NextResponse.json({ error: 'Error al obtener las estadísticas del usuario' }, { status: 500 });
    }
}