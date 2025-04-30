import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
    try {
        const { serverId, comando } = await req.json();

        const response = await fetch(`https://discord.com/api/v10/channels/${serverId}/messages`, {
            method: "POST",
            headers: {
                "Authorization": `Bot ${process.env.DISCORD_TOKEN}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                content: comando,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Error al enviar el comando al bot de Discord:", errorData);
            return new Response(JSON.stringify({ error: "Error al enviar el comando al bot de Discord" }), { status: 500 });
        }

        return new Response(JSON.stringify({ message: "Comando ejecutado correctamente" }), { status: 200 });
    } catch (error) {
        console.error("Error interno al procesar el comando:", error);
        return new Response(JSON.stringify({ error: "Error interno del servidor" }), { status: 500 });
    }
}