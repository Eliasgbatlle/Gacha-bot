const { createCanvas, loadImage } = require('canvas');

async function generarCarta(personaje) {
  const width = 350;
  const height = 500;
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');

  try {
    const fondo = await loadImage(personaje.fondo);
    ctx.drawImage(fondo, 0, 0, width, height);

    // Degradado inferior
    const grad = ctx.createLinearGradient(0, height, 0, height * 0.65);
    grad.addColorStop(0, "rgba(0, 0, 0, 0.85)");
    grad.addColorStop(1, "transparent");
    ctx.fillStyle = grad;
    ctx.fillRect(0, height * 0.65, width, height * 0.35);

    // Rareza
    ctx.font = "bold 36px Arial Black";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = getRarezaGradient(ctx, personaje.rareza, width);
    ctx.fillText(personaje.rareza, width / 2, height * 0.88);

    // Nombre
    ctx.font = "bold 18px Arial";
    ctx.fillStyle = "white";
    ctx.fillText(personaje.nombre, width / 2, height * 0.94);

    // Marco
    if (personaje.marco) {
      const marco = await loadImage(personaje.marco);
      ctx.drawImage(marco, 0, 0, width, height);
    }

    return canvas.toBuffer("image/png");
  } catch (error) {
    console.error("Error generando carta:", error);
    throw error;
  }
}

function getRarezaGradient(ctx, rareza, width) {
  const grad = ctx.createLinearGradient(0, 0, width, 0);
  switch (rareza.toUpperCase()) {
    case 'SSS':
      grad.addColorStop(0, "red");
      grad.addColorStop(0.2, "orange");
      grad.addColorStop(0.4, "yellow");
      grad.addColorStop(0.6, "lime");
      grad.addColorStop(0.8, "cyan");
      grad.addColorStop(1, "violet");
      break;
    case 'SS':
      grad.addColorStop(0, "gold");
      grad.addColorStop(1, "white");
      break;
    case 'S':
      grad.addColorStop(0, "silver");
      grad.addColorStop(1, "#aaa");
      break;
    default:
      grad.addColorStop(0, "#666");
      grad.addColorStop(1, "#444");
  }
  return grad;
}

module.exports = { generarCarta };
