import { NextResponse } from 'next/server';
import path from 'path';
import Database from 'better-sqlite3';

// Ruta a la base de datos
const dbPath = path.join(process.cwd(), '../../gacha_data.db');

export async function GET() {
    try {
        const db = new Database(dbPath, { readonly: true });
        const rows = db.prepare('SELECT * FROM gacha_table').all();
        db.close();
        return NextResponse.json(rows);
    } catch (error) {
        return NextResponse.json({ error: 'Error al consultar la base de datos', details: error.message }, { status: 500 });
    }
}