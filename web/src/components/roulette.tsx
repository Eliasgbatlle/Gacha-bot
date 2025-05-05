'use client';

import React, { useRef, useState, useEffect } from 'react';

const probabilidades = {
  SSS: 0.0001,
  SS: 0.001,
  S: 0.01,
  A: 0.07,
  B: 0.13,
  C: 0.18,
  D: 0.28,
  E: 0.3299,
};

const clases = Object.entries(probabilidades);

function generarItems(cantidad: number = 300, premio: string) {
  const items = [];

  while (items.length < cantidad) {
    const rand = Math.random();
    let suma = 0;
    for (const [rareza, prob] of clases) {
      suma += prob;
      if (rand <= suma) {
        items.push({ rareza });
        break;
      }
    }
  }

  // Insertar el premio en el centro visual (por ejemplo, posición 150)
  const centro = Math.floor(cantidad / 2);
  items[centro] = { rareza: premio };

  return items;
}

type RouletteProps = {
  setShowRoulette: React.Dispatch<React.SetStateAction<boolean>>;
  handleGirar: () => Promise<void>; // Agregar handleGirar como prop
};

export default function Roulette({ setShowRoulette, handleGirar }: RouletteProps) {
  const [premio, setPremio] = useState<string | null>(null); // Estado para manejar el valor de premio
  const [isPremioReady, setIsPremioReady] = useState(false); // Estado para verificar si premio está listo
  const [items, setItems] = useState(() => generarItems(300, 'A'));
  const rouletteRef = useRef<HTMLDivElement>(null);
  const [showButtons, setShowButtons] = useState(false);
  const [isHandlingRoulette, setIsHandlingRoulette] = useState(false);
  const hasSpun = useRef(false); // Evita doble ejecución

  useEffect(() => {
    const fetchPersonaje = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/discord/get-personaje', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) {
          throw new Error('Error al obtener el personaje');
        }
        const personaje = await response.json();
        console.log('Personaje obtenido:', personaje);

        // Actualizar el estado de premio con la rareza obtenida
        if (personaje && personaje.rareza) {
          setPremio(personaje.rareza);
          setIsPremioReady(true); // Marcar que premio está listo
        }
      } catch (error) {
        console.error('Error al obtener el personaje:', error);
      }
    };

    fetchPersonaje();
  }, []);

  useEffect(() => {
    if (isPremioReady && !hasSpun.current) {
      hasSpun.current = true;
      handleRoulette();
    }
  }, [isPremioReady]); // Ejecutar handleRoulette solo cuando premio esté listo

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && showButtons) {
        setShowRoulette(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [showButtons]);

  const fetchPremio = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/discord/get-personaje', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error('Error al obtener el personaje');
      }
      const personaje = await response.json();
      console.log('Personaje obtenido:', personaje);

      // Actualizar el estado de premio con la rareza obtenida
      if (personaje && personaje.rareza) {
        setPremio(personaje.rareza);
        setIsPremioReady(true); // Marcar que premio está listo
      }
    } catch (error) {
      console.error('Error al obtener el personaje:', error);
    }
  };

  const handleRoulette = async () => {
    await fetchPremio(); // Llamar al endpoint para obtener un nuevo premio

    if (!premio) {
      console.error('El valor de premio aún no está disponible.');
      return;
    }

    if (isHandlingRoulette) return;
    setIsHandlingRoulette(true);

    const nuevosItems = generarItems(300, premio);
    setItems(nuevosItems);

    const roulette = rouletteRef.current;
    if (roulette) {
      roulette.style.transition = 'none';
      roulette.style.transform = 'translateX(0)';
    }

    setTimeout(() => {
      spinRoulette();
    }, 500);

    setTimeout(() => {
      setShowButtons(true);
      setIsHandlingRoulette(false);
    }, 7000);
  };

  const spinRoulette = () => {
    const roulette = rouletteRef.current;
    if (!roulette) return;

    const itemEl = roulette.querySelector('.item') as HTMLDivElement;
    if (!itemEl) return;

    const itemWidth = itemEl.offsetWidth + 20;
    const containerWidth = 800;
    const centerOffset = containerWidth / 2 - itemWidth / 2;

    const centro = Math.floor(items.length / 2);
    const moveX = centro * itemWidth - centerOffset;

    roulette.style.transition = 'transform 6s cubic-bezier(0.1, 0.9, 0.3, 1)';
    roulette.style.transform = `translateX(-${moveX}px)`;
  };

  const getColor = (rareza: string) => {
    switch (rareza) {
      case 'SSS':
        return 'linear-gradient(45deg, red, gold)';
      case 'SS':
        return 'gold';
      case 'S':
        return 'orange';
      case 'A':
        return '#6a0dad';
      case 'B':
        return '#1e90ff';
      case 'C':
        return '#32cd32';
      case 'D':
        return '#8b4513';
      default:
        return '#999';
    }
  };

  const handleButtonClick = async () => {
    setShowButtons(false);

    // Ejecutar handleGirar para cambiar el valor del endpoint
    const girarPromise = handleGirar(); // No esperamos aquí para que el delay interno continúe

    // Ejecutar handleRoulette inmediatamente después de que el endpoint cambie
    await handleRoulette();

    // Esperar a que handleGirar termine (incluido su delay interno)
    await girarPromise;
  };

  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'transparent',
        position: 'relative',
        fontFamily: 'sans-serif',
      }}
    >
      {/* Aguja */}
      <div
        style={{
          position: 'absolute',
          width: '4px',
          height: '100px',
          backgroundColor: 'orange',
          top: '45.5%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 10,
          borderRadius: '2px',
          boxShadow: '0 0 10px white',
        }}
      ></div>

      {/* Carrusel */}
      <div
        style={{
          overflow: 'hidden',
          width: '800px',
          borderRadius: '10px',
          background: 'linear-gradient(to left, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.5) 10%, rgba(0, 0, 0, 0.5) 90%, rgba(0, 0, 0, 0))',
          WebkitMaskImage:
            'linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%)',
        }}
      >
        <div style={{ display: 'flex' }} ref={rouletteRef}>
          {items.map((item, i) => (
            <div
              key={i}
              className="item"
              style={{
                width: '80px',
                height: '80px',
                margin: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '8px',
                color: 'white',
                fontWeight: 'bold',
                background: getColor(item.rareza),
                flexShrink: 0,
                textAlign: 'center',
              }}
            >
              {item.rareza}
            </div>
          ))}
        </div>
      </div>

      {/* Botones */}
      <div
        style={{
          marginTop: '20px',
          display: 'flex',
          gap: '10px',
          visibility: showButtons ? 'visible' : 'hidden',
        }}
      >
        {/* Eliminado el botón "Volver a girar" */}
        {/* <button
          onClick={handleButtonClick}
          style={{
            backgroundColor: '#6b21a8',
            color: 'white',
            padding: '10px 20px',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          Volver a girar
        </button> */}
        <button
          onClick={() => setShowRoulette(false)}
          style={{
            backgroundColor: '#dc2626',
            color: 'white',
            padding: '10px 20px',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          Cerrar
        </button>
      </div>
    </div>
  );
}
