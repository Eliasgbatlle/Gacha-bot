"use client";

import { useEffect, useState } from 'react';

export default function HomePage() {
    const [data, setData] = useState<any[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch('/api/gacha')
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Error al obtener los datos');
                }
                return response.json();
            })
            .then((data) => setData(data))
            .catch((error) => setError(error.message));
    }, []);

    return (
        <div>
            <h1>Datos de Gacha</h1>
            {error ? (
                <p style={{ color: 'red' }}>{error}</p>
            ) : (
                <ul>
                    {data.map((item, index) => (
                        <li key={index}>{JSON.stringify(item)}</li>
                    ))}
                </ul>
            )}
        </div>
    );
}
