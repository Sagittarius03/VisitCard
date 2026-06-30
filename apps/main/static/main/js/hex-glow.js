// hex-glow.js — Полный контроль над Alpha (убраны скрытые коэффициенты)

document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('hexCanvas');
    if (!canvas) return;
    
    // =====================================================
    //  НАСТРОЙКИ (Цвета в формате [R, G, B] + Альфы)
    // =====================================================
    const CONFIG = {
        // Размеры и сетка
        hexSize: 20,            
        baseLineWidth: 1,       // Толщина фоновой сетки
        
        // Анимация
        maxRadius: 1000,        // Дальность расхождения
        speed: 400,             // Скорость расширения
        minWait: 1.5,           
        maxWait: 4.0,           
        
        // ===== ЦВЕТА ФОНА И СЕТКИ =====
        bgColor: [243, 243, 243], 
        gridColor: [217, 217, 217], 
        
        // ===== НЕОН (ГАЛО / ТЕНЬ) =====
        glowColor: [140, 0, 255],  
        glowAlpha: 1,            // Прозрачность гало
        glowLineWidth: 2,          
        glowBlur: 1,               
        
        // ===== ЯДРО (ОСНОВНАЯ ЛИНИЯ) =====
        coreColor: [140, 255, 0],  
        coreAlpha: 0.8,            // Прозрачность ядра (увеличил для примера)
        coreLineWidth: 10,          
    };
    // =====================================================

    // Разрешаем кликать
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
    
    // ===== ГЕОМЕТРИЯ ГЕКСОВ =====
    const BASE_SIZE = CONFIG.hexSize;
    const HEX_SIZE = BASE_SIZE - (CONFIG.baseLineWidth / 2);
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
    
    // ===== ЛОГИКА ИМПУЛЬСА =====
    let centerX = 0;
    let centerY = 0;
    let currentRadius = 0;
    let intensity = 0;
    let isActive = false;
    let timer = 0; 
    
    function startPulseFrom(x, y) {
        isActive = false;          
        centerX = x;
        centerY = y;
        currentRadius = 10;
        intensity = 1.0;
        isActive = true;           
    }
    
    function startRandomPulse() {
        if (isActive) return;
        startPulseFrom(Math.random() * W, Math.random() * H);
    }
    
    document.addEventListener('click', function(e) {
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        if (mouseX >= 0 && mouseX <= W && mouseY >= 0 && mouseY <= H) {
            timer = 0;
            startPulseFrom(mouseX, mouseY);
        }
    });
    
    // ===== ОТРИСОВКА =====
    function drawScene() {
        // 1. Фон
        ctx.clearRect(0, 0, W, H);
        ctx.fillStyle = `rgb(${CONFIG.bgColor[0]}, ${CONFIG.bgColor[1]}, ${CONFIG.bgColor[2]})`;
        ctx.fillRect(0, 0, W, H);
        
        const deltaTime = 1 / 60;
        
        if (isActive) {
            currentRadius += CONFIG.speed * deltaTime;
            const progress = currentRadius / CONFIG.maxRadius;
            intensity = Math.max(0, 1 - Math.pow(progress, 1.2));
            
            if (currentRadius > CONFIG.maxRadius || intensity < 0.01) {
                isActive = false;
                timer = CONFIG.minWait + Math.random() * (CONFIG.maxWait - CONFIG.minWait);
            }
        } else {
            timer -= deltaTime;
            if (timer <= 0) startRandomPulse();
        }
        
        // Извлекаем цвета
        const gridR = CONFIG.gridColor[0], gridG = CONFIG.gridColor[1], gridB = CONFIG.gridColor[2];
        const glowR = CONFIG.glowColor[0], glowG = CONFIG.glowColor[1], glowB = CONFIG.glowColor[2];
        const coreR = CONFIG.coreColor[0], coreG = CONFIG.coreColor[1], coreB = CONFIG.coreColor[2];
        
        for (const hex of hexes) {
            const pts = getHexPoints(hex.cx, hex.cy, HEX_SIZE);
            
            const dx = hex.cx - centerX;
            const dy = hex.cy - centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            let alpha = 0;
            let brightness = 0;
            
            if (isActive && dist < currentRadius) {
                const distanceFactor = 1 - (dist / currentRadius);
                brightness = intensity * Math.pow(distanceFactor, 1.5);
                alpha = Math.min(1, brightness * 1.2);
            }
            
            // ФОНОВАЯ СЕТКА
            ctx.save();
            ctx.strokeStyle = `rgb(${gridR}, ${gridG}, ${gridB})`;
            ctx.lineWidth = CONFIG.baseLineWidth;
            ctx.beginPath();
            ctx.moveTo(pts[0].x, pts[0].y);
            for (let i = 1; i < 6; i++) ctx.lineTo(pts[i].x, pts[i].y);
            ctx.closePath();
            ctx.stroke();
            ctx.restore();
            
            // СВЕЧЕНИЕ
            if (alpha > 0.01) {
                // Слой 1: Гало
                ctx.save();
                ctx.shadowColor = `rgba(${glowR}, ${glowG}, ${glowB}, ${CONFIG.glowAlpha * alpha})`; // 0.8 убрано!
                ctx.shadowBlur = CONFIG.glowBlur;
                ctx.strokeStyle = `rgba(${glowR}, ${glowG}, ${glowB}, ${CONFIG.glowAlpha * alpha})`; // 0.8 убрано!
                ctx.lineWidth = CONFIG.glowLineWidth * brightness;
                ctx.beginPath();
                ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i < 6; i++) ctx.lineTo(pts[i].x, pts[i].y);
                ctx.closePath();
                ctx.stroke();
                ctx.restore();
                
                // Слой 2: Ядро
                ctx.save();
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
                // Здесь тоже применяется строго coreAlpha без домножений
                ctx.strokeStyle = `rgba(${coreR}, ${coreG}, ${coreB}, ${CONFIG.coreAlpha * alpha})`;
                ctx.lineWidth = CONFIG.coreLineWidth * brightness;
                ctx.beginPath();
                ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i < 6; i++) ctx.lineTo(pts[i].x, pts[i].y);
                ctx.closePath();
                ctx.stroke();
                ctx.restore();
            }
        }
    }
    
    createHexGrid();
    startRandomPulse();
    
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