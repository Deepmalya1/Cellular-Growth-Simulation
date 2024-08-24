const canvas = document.getElementById('simulationCanvas');
const ctx = canvas.getContext('2d');
const graphCanvas = document.getElementById('growthGraphCanvas');
const graphCtx = graphCanvas.getContext('2d');
const slider = document.getElementById('diseaseSlider');
const stats = document.getElementById('stats');
const simulatedTimeDisplay = document.getElementById('simulatedTime');
const stopButton = document.getElementById('stopButton');
const clearButton = document.getElementById('clearButton');

const WIDTH = canvas.width;
const HEIGHT = canvas.height;
const CELL_RADIUS = 10;
const DISEASE_RADIUS = 50;
const TIME_PER_SECOND = 86400; 
const REPRODUCTION_INTERVAL = 50;
const DISEASE_REPRODUCTION_INTERVAL = 75;
const DISEASE_MAX_STRENGTH = 10;
const DISEASE_SPREAD_RATE = 0.02;

const COLORS = {
    brain: 'blue',
    liver: 'red',
    normal: 'green',
    disease: 'black',
};

const NATURAL_DEATH_RATE = {
    brain: 0.001,
    liver: 0.002,
    normal: 0.003,
    disease: 0.005,
};

const CELL_LIFESPAN = {
    brain: 1800,
    liver: 1200,
    normal: 600,
    disease: 300,
};

const ORGAN_PARAMS = {
    brain: {size: CELL_RADIUS, growth_rate: 0.1},
    liver: {size: CELL_RADIUS * 2, growth_rate: 0.2},
    normal: {size: CELL_RADIUS, growth_rate: 0.05},
};

class Cell {
    constructor(cell_type, x, y) {
        this.cell_type = cell_type;
        this.x = x;
        this.y = y;
        this.reproduction_timer = cell_type === 'disease' ? DISEASE_REPRODUCTION_INTERVAL : REPRODUCTION_INTERVAL;
        this.color = COLORS[cell_type] || 'green';
        this.size = ORGAN_PARAMS[cell_type]?.size || CELL_RADIUS;
        this.growth_rate = ORGAN_PARAMS[cell_type]?.growth_rate || 0;
        this.age = 0;
        this.lifespan = CELL_LIFESPAN[cell_type] || 1000;
        this.is_alive = true;
    }

    update() {
        if (this.is_alive) {
            this.age++;
            if (Math.random() < NATURAL_DEATH_RATE[this.cell_type]) {
                this.is_alive = false;
            }
            if (this.age > this.lifespan) {
                this.is_alive = false;
            }
            this.reproduction_timer--;
        }
    }

    reproduce(cells) {
        if (this.reproduction_timer <= 0 && this.is_alive) {
            const direction = Math.random() * 2 * Math.PI;
            const newX = this.x + Math.cos(direction) * this.size * 2;
            const newY = this.y + Math.sin(direction) * this.size * 2;
            if (newX >= 0 && newX < WIDTH && newY >= 0 && newY < HEIGHT) {
                cells.push(new Cell(this.cell_type, newX, newY));
            }
            this.reproduction_timer = this.cell_type === 'disease' ? DISEASE_REPRODUCTION_INTERVAL : REPRODUCTION_INTERVAL;
        }
    }

    draw(ctx) {
        if (this.is_alive) {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    }

    checkInfection(cells, diseaseStrength) {
        if (this.cell_type === 'disease') {
            for (let cell of cells) {
                if (cell.is_alive && cell !== this) {
                    const distance = Math.hypot(cell.x - this.x, cell.y - this.y);
                    if (distance <= DISEASE_RADIUS && Math.random() < (diseaseStrength / DISEASE_MAX_STRENGTH) * DISEASE_SPREAD_RATE) {
                        cell.is_alive = false;
                    }
                }
            }
        }
    }
}

let cells = [];
let current_cell_type = 'normal';
let disease_strength = parseInt(slider.value, 10);
let simulation_speed = TIME_PER_SECOND;
let start_time = Date.now();
let last_update_time = Date.now(); 
let simulationRunning = true;

slider.addEventListener('input', () => {
    disease_strength = parseInt(slider.value, 10);
});

canvas.addEventListener('click', (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    if (current_cell_type === 'disease') {
        for (let i = 0; i < disease_strength; i++) {
            cells.push(new Cell('disease', x, y));
        }
    } else {
        cells.push(new Cell(current_cell_type, x, y));
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'b') {
        current_cell_type = 'brain';
    } else if (event.key === 'l') {
        current_cell_type = 'liver';
    } else if (event.key === 'n') {
        current_cell_type = 'normal';
    } else if (event.key === 'd') {
        current_cell_type = 'disease';
    } else if (event.key === 'ArrowUp') {
        disease_strength = Math.min(disease_strength + 1, DISEASE_MAX_STRENGTH);
    } else if (event.key === 'ArrowDown') {
        disease_strength = Math.max(disease_strength - 1, 1);
    } else if (event.key === 'ArrowLeft') {
        simulation_speed = Math.max(simulation_speed - TIME_PER_SECOND, TIME_PER_SECOND);
    } else if (event.key === 'ArrowRight') {
        simulation_speed += TIME_PER_SECOND;
    }
});

stopButton.addEventListener('click', () => {
    simulationRunning = !simulationRunning;
    stopButton.textContent = simulationRunning ? 'Stop Simulation' : 'Start Simulation';
    if (simulationRunning) {
        last_update_time = Date.now();
        requestAnimationFrame(update);
    }
});

clearButton.addEventListener('click', () => {
    cells = []; 
    ctx.clearRect(0, 0, WIDTH, HEIGHT); 
    graphCtx.clearRect(0, 0, graphCanvas.width, graphCanvas.height); 
    stats.innerHTML = 'Brain cells: 0<br>Liver cells: 0<br>Normal cells: 0<br>Disease cells: 0';
    simulatedTimeDisplay.innerHTML = ''; 
});

function update() {
    if (!simulationRunning) return;

    let current_time = Date.now();
    let real_elapsed_seconds = (current_time - last_update_time) / 1000;
    let simulated_elapsed_seconds = real_elapsed_seconds * (simulation_speed / TIME_PER_SECOND);


    let days = Math.floor(simulated_elapsed_seconds / (24 * 3600));
    let hours = Math.floor((simulated_elapsed_seconds % (24 * 3600)) / 3600);
    let minutes = Math.floor((simulated_elapsed_seconds % 3600) / 60);
    let seconds = Math.floor(simulated_elapsed_seconds % 60);

  
    cells.forEach(cell => {
        cell.update();
        cell.reproduce(cells);
        cell.checkInfection(cells, disease_strength);
    });

   
    cells = cells.filter(cell => cell.is_alive);

   
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    cells.forEach(cell => cell.draw(ctx));

    // Update stats
    const cellCounts = { brain: 0, liver: 0, normal: 0, disease: 0 };
    cells.forEach(cell => cellCounts[cell.cell_type]++);
    stats.innerHTML = `
        Brain cells: ${cellCounts.brain}<br>
        Liver cells: ${cellCounts.liver}<br>
        Normal cells: ${cellCounts.normal}<br>
        Disease cells: ${cellCounts.disease}
    `;

    simulatedTimeDisplay.innerHTML =  ``;

    
    drawGrowthGraph(cellCounts);

    last_update_time = current_time; 
    requestAnimationFrame(update);
}

function drawGrowthGraph(cellCounts) {
    graphCtx.clearRect(0, 0, graphCanvas.width, graphCanvas.height);

   
    const graphWidth = graphCanvas.width;
    const graphHeight = graphCanvas.height;
    const barWidth = graphWidth / 4;
    const maxCount = Math.max(cellCounts.brain, cellCounts.liver, cellCounts.normal, cellCounts.disease);
    const scale = graphHeight / maxCount;

    const colors = {
        brain: 'blue',
        liver: 'red',
        normal: 'green',
        disease: 'black',
    };

    let x = 0;
    for (let type of ['brain', 'liver', 'normal', 'disease']) {
        graphCtx.fillStyle = colors[type];
        graphCtx.fillRect(x, graphHeight - cellCounts[type] * scale, barWidth, cellCounts[type] * scale);
        x += barWidth;
    }
}

requestAnimationFrame(update);
