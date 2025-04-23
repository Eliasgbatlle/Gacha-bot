import { NextResponse } from 'next/server';
import path from 'path';
import sqlite3 from 'sqlite3';

// Ruta a la base de datos
const dbPath = path.join(process.cwd(), '../../gacha_data.db');

export async function GET() {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err: Error | null) => {
            if (err) {
                reject(NextResponse.json({ error: 'Error al conectar con la base de datos' }, { status: 500 }));
            }
        });

        db.all('SELECT * FROM gacha_table', (err: Error | null, rows: any[]) => {
            if (err) {
                reject(NextResponse.json({ error: 'Error al consultar la base de datos' }, { status: 500 }));
            } else {
                resolve(NextResponse.json(rows));
            }
            db.close();
        });
    });
}