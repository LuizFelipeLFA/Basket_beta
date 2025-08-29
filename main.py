import random
import sys
from pathlib import Path

import pygame

# -----------------------------
# Configurações gerais
# -----------------------------

WIDTH, HEIGHT = 960, 540
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (220, 60, 60)
YELLOW= (230, 200, 60)
GREEN = (60, 200, 100)
BG_GRAY = (200, 200, 200)

BAR_RECT = pygame.Rect(220, 480, 520, 20)
BAR_SPEED = 0.85
MAX_TENTATIVAS = 3

# Zonas da barra (normalizado 0..1)

ZONE_LEFT_RED_END      = 0.25
ZONE_LEFT_YELLOW_END   = 0.40
ZONE_GREEN_END         = 0.60
ZONE_RIGHT_YELLOW_END  = 0.75

# Animação / mensagens
SHOOT_SPEED = 1.6
MESSAGE_DURATION = 1.2
ARC_HEIGHT = 160

# -----------------------------
# Pastas e carregamento
# -----------------------------

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "assets" / "images"

def load_img_scaled(name, scale=None, size=None):
    path = IMG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {path}")
    img = pygame.image.load(str(path)).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    elif scale:
        w, h = img.get_size()
        img = pygame.transform.scale(img, (int(w*scale), int(h*scale)))
    return img

# -----------------------------
# Inicialização
# -----------------------------

pygame.init()
pygame.display.set_caption("Basket Beta (Demo)")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
font_big = pygame.font.SysFont(None, 56)

# -----------------------------
# Carregar sprites
# -----------------------------

bg               = load_img_scaled("cenario.jpg", size=(WIDTH, HEIGHT))
sprite_idle      = load_img_scaled("Sprite_idle.png", 0.35)
sprite_arremesso = load_img_scaled("Sprite_Arremecando.png", 0.35)
sprite_acertou   = load_img_scaled("Sprite_Acertou.png", 0.35)

bola_img         = load_img_scaled("bola.png", 0.15)
cesta_vazia      = load_img_scaled("cesta_vazia.png", 0.25)
cesta_com_bola   = load_img_scaled("cesta_com_bola.png", 0.25)

# -----------------------------
# Posições
# -----------------------------

player_pos = pygame.Vector2(80, HEIGHT - sprite_idle.get_height() - 30)
cesta_pos  = pygame.Vector2(WIDTH - cesta_vazia.get_width() - 90, 120)

ball_rest_offset = pygame.Vector2(sprite_idle.get_width() * 0.55,
                                  sprite_idle.get_height() * 0.4)

def ball_start_pos():
    return player_pos + ball_rest_offset

def ball_end_pos():
    return pygame.Vector2(cesta_pos.x + cesta_vazia.get_width() * 0.50,
                          cesta_pos.y + cesta_vazia.get_height() * 0.45)

def arc_point(p0, p1, t, height=ARC_HEIGHT):
    p = p0.lerp(p1, t)
    arc = -4 * height * (t * (t - 1))
    return pygame.Vector2(p.x, p.y - arc)

# -----------------------------
# Estado do jogo
# -----------------------------

state = "MENU"
tentativas = MAX_TENTATIVAS
score = 0

bar_value = 0.0
bar_dir = 1

shooting = False
shoot_t = 0.0
shot_success = False
shot_zone = "red"

current_sprite = sprite_idle
current_cesta = cesta_vazia

result_message = None
message_timer = 0.0
pending_gameover = False

# -----------------------------
# Funções de zona
# -----------------------------

def zona_result(v):
    if v <= ZONE_LEFT_RED_END: return "red"
    if v <= ZONE_LEFT_YELLOW_END: return "yellow"
    if v <= ZONE_GREEN_END: return "green"
    if v <= ZONE_RIGHT_YELLOW_END: return "yellow"
    return "red"

def resolve_shot(v):
    z = zona_result(v)
    if z == "green":
        return True, z
    if z == "yellow":
        return random.choice([True, False]), z
    return False, z

def target_for_zone(zone, success):
    """Retorna o ponto final da bola baseado na zona/resultado"""
    p0 = ball_start_pos()
    p_cesta = ball_end_pos()

    if zone == "green" and success:
        return p_cesta
    elif zone == "yellow":
        if success:
            return p_cesta
        else:
            # "quase": borda da cesta (um pouco pro lado)
            return p_cesta + pygame.Vector2(-40, 0)
    else:  # red sempre erra
        return p0 + pygame.Vector2(random.randint(40, 120), -40)

# -----------------------------
# Barra de força
# -----------------------------

def draw_bar():
    x, y, w, h = BAR_RECT
    pygame.draw.rect(screen, RED,    (x, y, w*0.25, h))
    pygame.draw.rect(screen, YELLOW, (x+w*0.25, y, w*0.15, h))
    pygame.draw.rect(screen, GREEN,  (x+w*0.40, y, w*0.20, h))
    pygame.draw.rect(screen, YELLOW, (x+w*0.60, y, w*0.15, h))
    pygame.draw.rect(screen, RED,    (x+w*0.75, y, w*0.25, h))
    pygame.draw.rect(screen, BLACK, BAR_RECT, 2)
    mx = x + int(bar_value * w)
    pygame.draw.rect(screen, BLACK, (mx-2, y-6, 4, h+12))

# -----------------------------
# Loop principal
# -----------------------------

running = True
ball_target = None

while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "MENU":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = "PLAY"
                tentativas = MAX_TENTATIVAS
                score = 0
                bar_value = 0.0
                bar_dir = 1
                shooting = False
                current_sprite = sprite_idle
                current_cesta = cesta_vazia
                result_message = None
                message_timer = 0.0
                pending_gameover = False

        elif state == "PLAY":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and (not shooting) and message_timer <= 0:
                shot_success, shot_zone = resolve_shot(bar_value)
                shooting = True
                shoot_t = 0.0
                current_sprite = sprite_arremesso
                ball_target = target_for_zone(shot_zone, shot_success)
                result_message = None

        elif state == "GAMEOVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                state = "MENU"

    if state == "PLAY":
        if (not shooting) and message_timer <= 0:
            bar_value += BAR_SPEED * dt * bar_dir
            if bar_value >= 1.0:
                bar_value, bar_dir = 1.0, -1
            elif bar_value <= 0.0:
                bar_value, bar_dir = 0.0, 1

        if shooting:
            shoot_t += SHOOT_SPEED * dt
            if shoot_t >= 1.0:
                shooting = False
                if shot_success:
                    score += 1
                    current_sprite = sprite_acertou
                    current_cesta = cesta_com_bola
                    result_message = "Acertou!"
                    pending_gameover = False
                else:
                    tentativas -= 1
                    current_sprite = sprite_idle
                    current_cesta = cesta_vazia
                    result_message = "Errou!"
                    pending_gameover = (tentativas <= 0)

                message_timer = MESSAGE_DURATION
                bar_value = 0.0
                bar_dir = 1

        if message_timer > 0:
            message_timer -= dt
            if message_timer <= 0:
                if pending_gameover:
                    state = "GAMEOVER"
                    result_message = None
                else:
                    result_message = None
                    current_cesta = cesta_vazia
                    current_sprite = sprite_idle
                    message_timer = 0.0

    # -----------------------------
    # Desenho
    # -----------------------------

    screen.blit(bg, (0, 0))
    screen.blit(current_cesta, cesta_pos)
    screen.blit(current_sprite, player_pos)

    # Bola só aparece em arremessos ou na mensagem de acerto

    if shooting:
        # durante a animação sempre desenha a bola
        p0 = ball_start_pos()
        p1 = ball_target
        pos = arc_point(p0, p1, min(shoot_t, 1.0))
        screen.blit(bola_img, (pos.x - bola_img.get_width() / 2, pos.y - bola_img.get_height() / 2))

    elif (message_timer > 0):
        # Só mostra bola parada se for erro
        if result_message == "Errou!":
            p_end = ball_target
            screen.blit(bola_img, (p_end.x - bola_img.get_width() / 2, p_end.y - bola_img.get_height() / 2))

    if state == "PLAY":
        draw_bar()
        hud = font.render(f"Pontos: {score}   Tentativas: {tentativas}", True, BLACK)
        screen.blit(hud, (20, 20))

    if result_message:
        txt = font_big.render(result_message, True, BLACK)
        screen.blit(txt, (WIDTH/2 - txt.get_width()/2, 70))

    if state == "MENU":
        title = font_big.render("Basket Beta", True, BLACK)
        tip   = font.render("Pressione ESPAÇO para começar", True, BLACK)
        screen.blit(title, (WIDTH/2 - title.get_width()/2, 150))
        screen.blit(tip,   (WIDTH/2 - tip.get_width()/2,   220))

    if state == "GAMEOVER":
        over = font_big.render("Fim de jogo!", True, BLACK)
        tip  = font.render("Pressione R para reiniciar", True, BLACK)
        final = font.render(f"Pontos: {score}", True, BLACK)
        screen.blit(over, (WIDTH/2 - over.get_width()/2, 150))
        screen.blit(tip,  (WIDTH/2 - tip.get_width()/2, 220))
        screen.blit(final, (WIDTH/2 - final.get_width()/2, 260))

    pygame.display.flip()

pygame.quit()
