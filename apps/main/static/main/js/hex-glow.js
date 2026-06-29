// hex-glow.js — Идеальные крупные гексы (с компенсацией наслоения)

document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('hexCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let W, H;
    let time = 0;
    
    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);
    
    // ===== НАСТРОЙКИ =====
    const BASE_SIZE = 40;       // Базовый размер гексов
    const LINE_WIDTH = 1.0;     // Толщина линии
    
    // КОМПЕНСАЦИЯ: Уменьшаем радиус ровно на половину толщины линии, 
    // чтобы соседние гексы не накладывались и не оставляли зазоров
    const HEX_SIZE = BASE_SIZE - (LINE_WIDTH / 2);
    
    const WIDTH_STEP = HEX_SIZE * Math.sqrt(3);
    const HEIGHT_STEP = HEX_SIZE * 1.5;
    
    let hexes = [];
    
    function createHexGrid() {
        hexes = [];
        
        // Рассчитываем кол-во гексов с запасом по краям
        const cols = Math.ceil(W / WIDTH_STEP) + 6;
        const rows = Math.ceil(H / HEIGHT_STEP) + 6;
        
        // Начинаем с отрицательных координат (выше и левее экрана)
        const startX = -WIDTH_STEP * 1;
        const startY = -HEIGHT_STEP * 1;
        
        for (let row = 0; row < rows; row++) {
            const offsetX = (row % 2 === 0) ? 0 : WIDTH_STEP / 2;
            for (let col = 0; col < cols; col++) {
                const cx = startX + col * WIDTH_STEP + offsetX;
                const cy = startY + row * HEIGHT_STEP * 1;
                
                // Добавляем гекс, он автоматически покроет экран
                hexes.push({ cx, cy });
            }
        }
    }
    
    // Получаем 6 точек для контура
    function getHexPoints(cx, cy, size) {
        const pts = [];
        for (let i = 0; i < 6; i++) {
            const angle = (Math.PI / 180) * (60 * i + 30);
            pts.push({ x: cx + size * Math.cos(angle), y: cy + size * Math.sin(angle) });
        }
        return pts;
    }
    
    // Цвета
    const BG_COLOR = '#181b1f';     
    const GRID_COLOR = '#2a2e35';   
    
    function drawScene() {
        ctx.clearRect(0, 0, W, H);
        
        // 1. Фон
        ctx.fillStyle = BG_COLOR;
        ctx.fillRect(0, 0, W, H);
        
        // 2. Сетка (замкнутые контуры с компенсацией)
        ctx.save();
        ctx.strokeStyle = GRID_COLOR;
        ctx.lineWidth = LINE_WIDTH; 
        ctx.beginPath();
        
        for (const hex of hexes) {
            const pts = getHexPoints(hex.cx, hex.cy, HEX_SIZE);
            ctx.moveTo(pts[0].x, pts[0].y);
            for (let i = 1; i < 6; i++) {
                ctx.lineTo(pts[i].x, pts[i].y);
            }
            ctx.closePath();
        }
        ctx.stroke();
        ctx.restore();
        
        // 3. Луч
        const waveX = (time * 70) % (W + 20) - 50;
        
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(waveX, H / 2, 50, H * 0.9, 0, 0, Math.PI * 2);
        ctx.clip();
        
        const grad = ctx.createLinearGradient(waveX - 50, 0, waveX + 50, 0);
        grad.addColorStop(0, 'rgba(43, 92, 171, 0.4)');
        grad.addColorStop(0.5, '#00ff80');
        grad.addColorStop(1, 'rgba(59, 130, 246, 0.4)');
        
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        for (const hex of hexes) {
            const pts = getHexPoints(hex.cx, hex.cy, HEX_SIZE);
            ctx.moveTo(pts[0].x, pts[0].y);
            for (let i = 1; i < 6; i++) {
                ctx.lineTo(pts[i].x, pts[i].y);
            }
            ctx.closePath();
        }
        ctx.stroke();
        
        ctx.restore();
    }
    
    // ===== ЗАПУСК =====
    createHexGrid();
    
    function loop(timestamp) {
        time = timestamp / 1000;
        drawScene();
        requestAnimationFrame(loop);
    }
    loop(0);
    
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            resize();
            createHexGrid();
        }, 1000);
    });
});