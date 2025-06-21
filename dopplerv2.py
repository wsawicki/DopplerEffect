import pygame
import pygame_gui

pygame.init()
WIDTH, HEIGHT = 1600, 900
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Efekt Dopplera")

manager = pygame_gui.UIManager((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FREQ_SOURCE = 432
SPEED_OF_SOUND = 340
PIXELS_PER_METER = 35

WAVE_INTERVAL = 0.3
WAVE_FADE_RATE = 150
WAVE_MAX_RADIUS = 1200

slider_source = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(50, 30, 300, 30), 0, (-15, 15), manager)
label_source = pygame_gui.elements.UILabel(pygame.Rect(50, 0, 300, 25), "Prędkość źródła [m/s]: 0", manager)

slider_obs = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(50, 100, 300, 30), 0, (-15, 15), manager)
label_obs = pygame_gui.elements.UILabel(pygame.Rect(50, 70, 300, 25), "Prędkość obserwatora [m/s]: 0", manager)

freq_label = pygame_gui.elements.UILabel(pygame.Rect(50, 140, 300, 30), "", manager)

button_start = pygame_gui.elements.UIButton(pygame.Rect(400, 30, 300, 30), "Start symulacji", manager)
button_reset = pygame_gui.elements.UIButton(pygame.Rect(400, 80, 300, 30), "Reset symulacji", manager)
button_update = pygame_gui.elements.UIButton(pygame.Rect(400, 130, 300, 30), "Aktualizuj prędkości", manager)
button_pause_resume = pygame_gui.elements.UIButton(pygame.Rect(400, 180, 300, 30), "Pauzuj symulację", manager)

start_x_source = 200 
start_x_obs = 1300
x_source = start_x_source
x_obs = start_x_obs
y_offset = HEIGHT // 2 + 100

v_source = 0.0
v_obs = 0.0
running_simulation = False
paused_simulation = False

freq_data = []
max_points = 500

wave_timer = 0 
waves = []

WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)


def doppler(f_emit, x_s, v_s, x_o, v_o):
    if x_o < x_s:
        vo_toward = v_o
        vs_away = -v_s
    else:
        vo_toward = -v_o
        vs_away = v_s

    numerator = SPEED_OF_SOUND + vo_toward
    denominator = SPEED_OF_SOUND - vs_away
    if denominator == 0:
        denominator = 0.01

    return f_emit * numerator / denominator


def draw_chart(surface, data, pos_x, pos_y, width, height):
    pygame.draw.rect(surface, GRAY, (pos_x, pos_y, width, height), 1)
    min_freq = FREQ_SOURCE - 40
    max_freq = FREQ_SOURCE + 40

    for f in range(min_freq, max_freq + 1, 5):
        y = pos_y + height - (f - min_freq) * height / (max_freq - min_freq)
        pygame.draw.line(surface, GRAY, (pos_x, y), (pos_x + width, y), 1)
        label = pygame.font.SysFont(None, 20).render(str(f), True, BLACK)
        surface.blit(label, (pos_x - 35, y - 7))

    for i in range(0, max_points + 1, 100):
        x = pos_x + i * width / max_points
        pygame.draw.line(surface, GRAY, (x, pos_y), (x, pos_y + height), 1)
        label = pygame.font.SysFont(None, 20).render(str(i), True, BLACK)
        surface.blit(label, (x - 10, pos_y + height + 5))

    if len(data) < 2:
        return

    scale_x = width / max_points
    scale_y = height / (max_freq - min_freq)

    for i in range(1, len(data)):
        x1 = pos_x + (i - 1) * scale_x
        y1 = pos_y + height - (data[i - 1] - min_freq) * scale_y
        x2 = pos_x + i * scale_x
        y2 = pos_y + height - (data[i] - min_freq) * scale_y
        pygame.draw.line(surface, BLACK, (x1, y1), (x2, y2), 2)

running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    wave_timer += time_delta

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button_start: 
                v_source = slider_source.get_current_value()
                v_obs = slider_obs.get_current_value()
                running_simulation = True
                paused_simulation = False
                button_pause_resume.set_text("Pauzuj symulację")
            elif event.ui_element == button_reset:
                x_source = start_x_source
                x_obs = start_x_obs
                v_source = 0
                v_obs = 0
                running_simulation = False
                paused_simulation = False
                freq_data.clear()
                waves.clear()
                wave_timer = 0
                button_pause_resume.set_text("Pauzuj symulację")
            elif event.ui_element == button_update:
                v_source = slider_source.get_current_value()
                v_obs = slider_obs.get_current_value()
            elif event.ui_element == button_pause_resume:
                if running_simulation:
                    paused_simulation = not paused_simulation
                    button_pause_resume.set_text("Wznów symulację" if paused_simulation else "Pauzuj symulację")
        manager.process_events(event)

    manager.update(time_delta)

    label_source.set_text(f"Prędkość źródła [m/s]: {slider_source.get_current_value():.1f}")
    label_obs.set_text(f"Prędkość obserwatora [m/s]: {slider_obs.get_current_value():.1f}")

    freq_obs = doppler(FREQ_SOURCE, x_source, v_source, x_obs, v_obs)
    freq_label.set_text(f"Obserwowana częstotliwość: {freq_obs:.1f} Hz")


    if running_simulation and not paused_simulation:
        x_source += v_source * time_delta * PIXELS_PER_METER
        x_obs += v_obs * time_delta * PIXELS_PER_METER

        if x_source <= 0 or x_source >= WIDTH:
            v_source *= -1
        if x_obs <= 0 or x_obs >= WIDTH:
            v_obs *= -1

        freq_data.append(freq_obs)
        if len(freq_data) > max_points:
            freq_data.pop(0)

        if wave_timer >= WAVE_INTERVAL:
            waves.append({'x': x_source, 'y': y_offset, 'radius': 0, 'alpha': 255})
            wave_timer = 0

    for wave in waves:
        wave_expand_rate = max(abs(v_source) * PIXELS_PER_METER + 30, SPEED_OF_SOUND * 1.5)
        wave['radius'] += wave_expand_rate * time_delta
        wave['alpha'] -= WAVE_FADE_RATE * time_delta

    waves = [w for w in waves if w['alpha'] > 0 and w['radius'] < WAVE_MAX_RADIUS]

    WINDOW.fill(WHITE)

    for wave in waves:
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = max(0, min(255, int(wave['alpha'])))
        pygame.draw.circle(surf, (100, 100, 255, alpha), (int(wave['x']), int(wave['y'])), int(wave['radius']), 2)
        WINDOW.blit(surf, (0, 0))

    pygame.draw.circle(WINDOW, RED, (int(x_source), y_offset), 20)
    pygame.draw.circle(WINDOW, BLUE, (int(x_obs), y_offset), 20)

    draw_chart(WINDOW, freq_data, 1050, 30, 500, 300)

    manager.draw_ui(WINDOW)
    pygame.display.update()

pygame.quit()
