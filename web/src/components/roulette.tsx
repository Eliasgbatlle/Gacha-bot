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

function generarItems(cantidad: number = 300) {
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

  return items;
}

type RouletteProps = {
  setShowRoulette: React.Dispatch<React.SetStateAction<boolean>>;
};

export default function Roulette({ setShowRoulette }: RouletteProps) {
  const [items, setItems] = useState(() => generarItems(300));
  const rouletteRef = useRef<HTMLDivElement>(null);
  const [showRoulette, setShowRouletteState] = useState(true);
  const [showButtons, setShowButtons] = useState(false);

  useEffect(() => {
    // Ejecutar el giro automáticamente al montar el componente
    handleRoulette();
  }, []);

  if (!showRoulette) {
    return null; // No renderizar nada si showRoulette es false
  }

  const handleRoulette = async () => {
    setShowRouletteState(true);

    // Generar nuevas rarezas solo cuando hay un giro
    setItems(generarItems(300));

    setTimeout(() => {
      spinRoulette();
    }, 500); // 1 segundo de espera

    const rouletteDuration = 6000; // Duración de la animación en milisegundos

    setTimeout(() => {
      setShowButtons(true);
    }, rouletteDuration + 1000); // 1 segundo de espera + duración del giro
  };

  let isSpinning = false;

  const spinRoulette = () => {
    isSpinning = true;
    const roulette = rouletteRef.current;
    if (!roulette) return;

    const itemEl = roulette.querySelector('.item') as HTMLDivElement;
    if (!itemEl) return;

    const itemWidth = itemEl.offsetWidth + 20;
    const containerWidth = 800;
    const centerOffset = containerWidth / 2 - itemWidth / 2;

    const stopAt = Math.floor(Math.random() * items.length);
    const moveX = stopAt * itemWidth - centerOffset;

    roulette.style.transition = 'transform 6s cubic-bezier(0.1, 0.9, 0.3, 1)';
    roulette.style.transform = `translateX(-${moveX}px)`;

    setTimeout(() => {
      roulette.style.transition = 'none';
      roulette.style.transform = `translateX(-${moveX}px)`;
      isSpinning = false;
    }, 6000);
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

  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'transparent', // Fondo completamente transparente
        position: 'relative',
        fontFamily: 'sans-serif',
      }}
    >
      {/* Aguja central */}
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
          maskImage:
          'linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%)',
          WebkitMaskSize: '100% 100%',
          maskSize: '100% 100%',
          WebkitMaskRepeat: 'no-repeat',
          maskRepeat: 'no-repeat',
        }}
      >
        <div style={{ display: 'flex'}} ref={rouletteRef}>
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
          visibility: showButtons ? 'visible' : 'hidden', // Hacer invisibles los botones cuando no estén habilitados
          pointerEvents: showButtons ? 'auto' : 'none', // Bloquear interacción cuando no estén habilitados
        }}
      >
        <button
          onClick={() => {
            setShowButtons(false);
            handleRoulette();
          }}
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
        </button>
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
