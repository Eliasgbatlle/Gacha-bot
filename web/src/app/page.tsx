"use client";

import { useEffect, useState } from 'react';

interface GachaData {
    characters?: any[];
    users?: any[];
    personajes?: any[];
    top?: any[];
}

export default function HomePage() {
    const [data, setData] = useState<GachaData>({});
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch('/api/gacha')
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Error al obtener los datos');
                }
                return response.json();
            })
            .then((data) => {
                console.log('Datos recibidos de la API:', data);
                setData(data);
            })
            .catch((error) => setError(error.message));
    }, []);

    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

    return (
        <div>
            <h1>Datos de Gacha</h1>
            {data.characters && (
                <div>
                    <h2>Characters</h2>
                    <ul>
                        {data.characters.map((item, index) => (
                            <li key={index}>{JSON.stringify(item)}</li>
                        ))}
                    </ul>
                </div>
            )}
            {data.users && (
                <div>
                    <h2>Users</h2>
                    <ul>
                        {data.users.map((item, index) => (
                            <li key={index}>{JSON.stringify(item)}</li>
                        ))}
                    </ul>
                </div>
            )}
            {data.personajes && (
                <div>
                    <h2>Personajes</h2>
                    <ul>
                        {data.personajes.map((item, index) => (
                            <li key={index}>{JSON.stringify(item)}</li>
                        ))}
                    </ul>
                </div>
            )}
            {data.top && (
                <div>
                    <h2>Top</h2>
                    <ul>
                        {data.top.map((item, index) => (
                            <li key={index}>{JSON.stringify(item)}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
