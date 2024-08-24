import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)
CELL_RADIUS = 10
TIME_PER_SECOND = 86400  # 24 hours in seconds
REPRODUCTION_INTERVAL = 50  # Time in frames for reproduction
DISEASE_REPRODUCTION_INTERVAL = 75  # Reproduction interval for disease cells
DISEASE_MAX_STRENGTH = 10
DISEASE_RADIUS = 50  # Radius within which the disease affects cells
DISEASE_SPREAD_RATE = 0.02  # Chance that a disease will spread each update
NATURAL_DEATH_RATE = {
    'brain': 0.001,  # Chance of natural death per update
    'liver': 0.002,
    'normal': 0.003,
    'disease': 0.005
}
CELL_LIFESPAN = {
    'brain': 1800,  # Lifespan in frames
    'liver': 1200,
    'normal': 600,
    'disease': 300
}

# Colors
COLORS = {
    'brain': (0, 0, 255),
    'liver': (255, 0, 0),
    'normal': (0, 255, 0),
    'disease': (0, 0, 0),
}

# Organ-specific parameters
ORGAN_PARAMS = {
    'brain': {'size': CELL_RADIUS, 'growth_rate': 0.1},
    'liver': {'size': CELL_RADIUS * 2, 'growth_rate': 0.2},
    'normal': {'size': CELL_RADIUS, 'growth_rate': 0.05},
}

class Cell:
    def __init__(self, cell_type, x, y):
        self.cell_type = cell_type
        self.x = x
        self.y = y
        self.reproduction_timer = REPRODUCTION_INTERVAL if cell_type != 'disease' else DISEASE_REPRODUCTION_INTERVAL
        self.color = COLORS.get(cell_type, (0, 255, 0))  # Default to normal cell color
        self.size = ORGAN_PARAMS.get(cell_type, {'size': CELL_RADIUS})['size']
        self.is_disease = cell_type == 'disease'
        self.growth_rate = ORGAN_PARAMS.get(cell_type, {'growth_rate': 0})['growth_rate']
        self.age = 0  # Track the age of the cell
        self.lifespan = CELL_LIFESPAN.get(cell_type, 1000)  # Default lifespan in frames
        self.is_alive = True  # Track if the cell is alive

    def update(self):
        if self.is_alive:
            self.age += 1
            if random.random() < NATURAL_DEATH_RATE.get(self.cell_type, 0):
                self.is_alive = False
            if self.age > self.lifespan:
                self.is_alive = False
            self.reproduction_timer -= 1  # Decrease the reproduction timer

    def reproduce(self, cells):
        if self.reproduction_timer <= 0 and self.is_alive:
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            new_x = self.x + direction[0] * CELL_RADIUS * 2
            new_y = self.y + direction[1] * CELL_RADIUS * 2
            if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT:
                cells.append(Cell(self.cell_type, new_x, new_y))
            self.reproduction_timer = REPRODUCTION_INTERVAL if self.cell_type != 'disease' else DISEASE_REPRODUCTION_INTERVAL  # Reset timer

    def draw(self, screen):
        if self.is_alive:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

    def check_infection(self, cells, disease_strength):
        if self.is_disease:
            for cell in cells:
                if cell.is_alive and cell != self:
                    distance = ((cell.x - self.x) ** 2 + (cell.y - self.y) ** 2) ** 0.5
                    if distance <= DISEASE_RADIUS:
                        # Check if the cell is infected based on the disease strength
                        if random.random() < (disease_strength / DISEASE_MAX_STRENGTH) * DISEASE_SPREAD_RATE:
                            cell.is_alive = False  # Kill the cell

def draw_slider(screen, x, y, width, height, value, max_value):
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))
    pygame.draw.rect(screen, (100, 150, 255), (x, y, (value / max_value) * width, height))
    pygame.draw.rect(screen, (0, 0, 0), (x + (value / max_value) * width - 10, y - 5, 20, height + 10))

def main():
    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cell Simulation")
    
    clock = pygame.time.Clock()
    cells = []
    current_cell_type = 'normal'
    disease_strength = 1
    simulation_speed = TIME_PER_SECOND  # 24 hours per second
    start_time = time.time()  # Real start time of the simulation

    slider_x, slider_y = 10, HEIGHT - 80
    slider_width, slider_height = 200, 20
    slider_dragging = False

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if slider_x <= x <= slider_x + slider_width and slider_y <= y <= slider_y + slider_height:
                    slider_dragging = True
                    disease_strength = int(((x - slider_x) / slider_width) * DISEASE_MAX_STRENGTH) + 1
                elif current_cell_type == 'disease':
                    for _ in range(disease_strength):
                        cells.append(Cell('disease', x, y))
                else:
                    cells.append(Cell(current_cell_type, x, y))
            elif event.type == pygame.MOUSEBUTTONUP:
                if slider_dragging:
                    slider_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if slider_dragging:
                    x, y = event.pos
                    disease_strength = int(((x - slider_x) / slider_width) * DISEASE_MAX_STRENGTH) + 1
                    disease_strength = max(1, min(disease_strength, DISEASE_MAX_STRENGTH))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    current_cell_type = 'brain'
                elif event.key == pygame.K_l:
                    current_cell_type = 'liver'
                elif event.key == pygame.K_n:
                    current_cell_type = 'normal'
                elif event.key == pygame.K_d:
                    current_cell_type = 'disease'
                elif event.key == pygame.K_UP:
                    if disease_strength < DISEASE_MAX_STRENGTH:
                        disease_strength += 1
                elif event.key == pygame.K_DOWN:
                    if disease_strength > 1:
                        disease_strength -= 1
                elif event.key == pygame.K_LEFT:
                    if simulation_speed > TIME_PER_SECOND:
                        simulation_speed -= TIME_PER_SECOND
                elif event.key == pygame.K_RIGHT:
                    simulation_speed += TIME_PER_SECOND

        # Calculate the elapsed time
        current_time = time.time()
        real_elapsed_seconds = current_time - start_time
        simulated_elapsed_seconds = real_elapsed_seconds * (simulation_speed / TIME_PER_SECOND)

        # Convert simulated elapsed time to days, hours, minutes, seconds
        days = simulated_elapsed_seconds // (24 * 3600)
        hours = (simulated_elapsed_seconds % (24 * 3600)) // 3600
        minutes = (simulated_elapsed_seconds % 3600) // 60
        seconds = simulated_elapsed_seconds % 60

        # Update cells and handle infections
        for cell in cells:
            cell.update()
            cell.reproduce(cells)
            cell.check_infection(cells, disease_strength)

        # Remove dead cells
        cells = [cell for cell in cells if cell.is_alive]

        # Draw cells
        for cell in cells:
            cell.draw(screen)

        # Draw cell type counts
        cell_counts = {'brain': 0, 'liver': 0, 'normal': 0, 'disease': 0}
        for cell in cells:
            cell_counts[cell.cell_type] += 1

        font = pygame.font.Font(None, 36)
        for i, (cell_type, count) in enumerate(cell_counts.items()):
            text = f"{cell_type.capitalize()} cells: {count}"
            text_surface = font.render(text, True, COLORS[cell_type])
            screen.blit(text_surface, (10, 30 + i * 40))

        # Draw the disease strength slider
        draw_slider(screen, slider_x, slider_y, slider_width, slider_height, disease_strength, DISEASE_MAX_STRENGTH)

        # Draw simulated time
        time_text = f"Simulated Time: {int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        time_surface = font.render(time_text, True, (0, 0, 0))
        screen.blit(time_surface, (WIDTH - 400, HEIGHT - 40))

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
