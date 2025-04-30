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

        const Database = (await import('better-sqlite3')).default;
        const db = new Database(gachaDbPath, { readonly: true });

        if (!server) {
            // Si no se especifica un servidor, devolver el ranking global
            const globalRankings = db.prepare(
                `SELECT user_id, max_score, rank 
                 FROM global_ranking 
                 ORDER BY rank ASC`
            ).all();

            return NextResponse.json({ globalRankings });
        }

        // Obtener puntaje y ranking del jugador actual desde la tabla ranking
        const playerData = db.prepare(
            `SELECT score, rank 
             FROM ranking 
             WHERE user_id = ? AND server_id = (SELECT server_id FROM servers WHERE server_name = ?)`
        ).get(userId, server);

        const playerScore = playerData?.score || 0;
        const playerRank = playerData?.rank || null;

        // Obtener ranking completo del servidor desde la tabla ranking
        const rankings = db.prepare(
            `SELECT r.user_id, r.score, r.rank 
             FROM ranking r
             JOIN servers s ON r.server_id = s.server_id
             WHERE s.server_name = ?
             ORDER BY r.rank ASC`
        ).all(server);

        return NextResponse.json({ playerScore, playerRank, rankings });
    } catch (error) {
        console.error('Error al calcular el ranking por servidor:', error);
        return NextResponse.json({ error: 'Error al calcular el ranking por servidor' }, { status: 500 });
    }
}