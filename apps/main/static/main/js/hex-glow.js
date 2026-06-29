// hex-glow.js — Абсолютный приоритет клика (исправлен pointer-events)

document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('hexCanvas');
    if (!canvas) return;
    
    // ===== ВАЖНО: Разрешаем кликать по холсту =====
    canvas.style.pointerEvents = 'auto';
    
    const ctx = canvas.getContext('2d');
    let W, H;
    let time = 0;
    
    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);
    
    // ===== НАСТРОЙКИ ГЕКСОВ =====
    const BASE_SIZE = 40;       
    const LINE_WIDTH = 1.0;     
    const HEX_SIZE = BASE_SIZE - (LINE_WIDTH / 2);
    const WIDTH_STEP = HEX_SIZE * Math.sqrt(3);
    const HEIGHT_STEP = HEX_SIZE * 1.5;
    
    let hexes = [];
    
    function createHexGrid() {
        hexes = [];
        const cols = Math.ceil(W / WIDTH_STEP) + 6;
        const rows = Math.ceil(H / HEIGHT_STEP) + 6;
        const startX = -WIDTH_STEP * 1;
        const startY = -HEIGHT_STEP * 1;
        
        for (let row = 0; row < rows; row++) {
            const offsetX = (row % 2 === 0) ? 0 : WIDTH_STEP / 2;
            for (let col = 0; col < cols; col++) {
                const cx = startX + col * WIDTH_STEP + offsetX;
                const cy = startY + row * HEIGHT_STEP * 1;
                hexes.push({ cx, cy });
            }
        }
    }
    
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
    
    // ===== ЛОГИКА РАДИАЛЬНОГО ЛУЧА =====
    let centerX = 0;
    let centerY = 0;
    let currentRadius = 0;
    let intensity = 0;
    let isActive = false;
    let timer = 0; 
    
    const MAX_RADIUS = 600;      
    const SPEED = 400;           
    const MIN_WAIT = 1.5;        
    const MAX_WAIT = 4.0;        
    
    // Мгновенный старт с любой точки
    function startPulseFrom(x, y) {
        isActive = false;          // Мгновенно убиваем предыдущую анимацию
        centerX = x;
        centerY = y;
        currentRadius = 20;
        intensity = 1.0;
        isActive = true;           // Запускаем новую ровно здесь
    }
    
    // Автоматический старт в случайном месте (фоновый режим)
    function startRandomPulse() {
        if (isActive) return; // Не мешаем активной анимации клика
        startPulseFrom(Math.random() * W, Math.random() * H);
    }
    
    // ===== ПРЯМОЙ ОБРАБОТЧИК КЛИКА =====
    // Вешаем обработчик на весь документ, чтобы поймать клик 100%
    document.addEventListener('click', function(e) {
        // Получаем координаты мыши относительно холста
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Если клик был внутри холста, запускаем анимацию
        if (mouseX >= 0 && mouseX <= W && mouseY >= 0 && mouseY <= H) {
            timer = 0; // Сбрасываем таймер ожидания
            startPulseFrom(mouseX, mouseY);
        }
    });
    
    // ===== РИСОВАНИЕ =====
    function drawScene() {
        ctx.clearRect(0, 0, W, H);
        
        ctx.fillStyle = BG_COLOR;
        ctx.fillRect(0, 0, W, H);
        
        ctx.save();
        ctx.strokeStyle = GRID_COLOR;
        ctx.lineWidth = LINE_WIDTH; 
        ctx.beginPath();
        for (const hex of hexes) {
            const pts = getHexPoints(hex.cx, hex.cy, HEX_SIZE);
            ctx.moveTo(pts[0].x, pts[0].y);
            for (let i = 1; i < 6; i++) ctx.lineTo(pts[i].x, pts[i].y);
            ctx.closePath();
        }
        ctx.stroke();
        ctx.restore();
        
        const deltaTime = 1 / 60;
        
        if (isActive) {
            currentRadius += SPEED * deltaTime;
            const progress = currentRadius / MAX_RADIUS;
            intensity = Math.max(0, 1 - progress * 1.2);
            
            if (currentRadius > MAX_RADIUS || intensity < 0.01) {
                isActive = false;
                timer = MIN_WAIT + Math.random() * (MAX_WAIT - MIN_WAIT);
            }
        } else {
            timer -= deltaTime;
            if (timer <= 0) {
                startRandomPulse();
            }
        }
        
        if (isActive && intensity > 0.01) {
            ctx.save();
            
            ctx.beginPath();
            ctx.arc(centerX, centerY, currentRadius, 0, Math.PI * 2);
            ctx.clip();
            
            const grad = ctx.createRadialGradient(
                centerX, centerY, 0,
                centerX, centerY, currentRadius
            );
            grad.addColorStop(0, `rgba(0, 255, 128, ${0.8 * intensity})`);
            grad.addColorStop(0.3, `rgba(59, 130, 246, ${0.6 * intensity})`);
            grad.addColorStop(0.7, `rgba(0, 255, 128, ${0.3 * intensity})`);
            grad.addColorStop(1, `rgba(59, 130, 246, 0)`);
            
            ctx.strokeStyle = grad;
            ctx.lineWidth = 2.2 * intensity;
            ctx.shadowColor = `rgba(0, 255, 128, ${0.3 * intensity})`;
            ctx.shadowBlur = 15;
            
            ctx.beginPath();
            for (const hex of hexes) {
                const pts = getHexPoints(hex.cx, hex.cy, HEX_SIZE);
                ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i < 6; i++) ctx.lineTo(pts[i].x, pts[i].y);
                ctx.closePath();
            }
            ctx.stroke();
            
            ctx.restore();
        }
    }
    
    createHexGrid();
    startRandomPulse(); // Первая вспышка при загрузке
    
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