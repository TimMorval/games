import pygame
import sys
import random
import math

pygame.init()

# --- Configuration du plateau ---
NB_CASES = 63   # Cases numérotées de 1 à 63
NB_COLS = 9     # Organisation sur 9 colonnes.
CELL_SIZE = 60

# Calculs pour le plateau
BOARD_WIDTH = (NB_COLS + 1) * CELL_SIZE  # La première colonne pour "Départ"
NB_ROWS = ((NB_CASES - 1) // NB_COLS) + 1
BOARD_HEIGHT = NB_ROWS * CELL_SIZE

# Zone de logs à droite
LOG_WIDTH = 300
LOG_HEIGHT = BOARD_HEIGHT

# Taille totale de la fenêtre
WINDOW_WIDTH = BOARD_WIDTH + LOG_WIDTH
WINDOW_HEIGHT = max(BOARD_HEIGHT, LOG_HEIGHT)

# --- Couleurs ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTGREY = (211, 211, 211)
LIGHTBLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
PINK = (255, 182, 193)
LIGHTGREEN = (144, 238, 144)
VIOLET = (238, 130, 238)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
DARKGREY = (169, 169, 169)

# --- Fonts de base ---
# Nous utiliserons des fonctions pour ajuster la taille selon l'espace disponible.


def render_fitted_text(text, max_width, initial_size, color):
    """Retourne une surface avec le texte rendu dans une police réduite si besoin."""
    size = initial_size
    font = pygame.font.SysFont("Arial", size)
    while font.size(text)[0] > max_width and size > 8:
        size -= 1
        font = pygame.font.SysFont("Arial", size)
    return font.render(text, True, color)


def render_wrapped_text(text, font, color, max_width):
    """Retourne une liste de surfaces pour chaque ligne, le texte étant coupé pour tenir dans max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return [font.render(line, True, color) for line in lines]


# --- Initialisation de la fenêtre ---
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Jeu de l'Oie (Pygame)")

clock = pygame.time.Clock()

# --- Définition des cases spéciales ---
SPECIAL_CASES = {
    6: ("PONT", 12),
    9: ("OIE", None),
    18: ("OIE", None),
    27: ("OIE", None),
    36: ("OIE", None),
    45: ("OIE", None),
    54: ("OIE", None),
    19: ("HOTEL", None),
    31: ("PUITS", 20),
    42: ("LABYRINTHE", 30),
    52: ("PRISON", None),
    58: ("TETE DE MORT", 0),
    63: ("FINAL", None)
}

# --- États du jeu ---
game_state = "START"  # "START" ou "PLAYING"
players = []          # Liste des dictionnaires joueurs
current_player_idx = 0
logs = []             # Historique des logs
game_over = False
log_scroll_offset = 0  # Pour le scroll vertical des logs

# --- Utilitaires pour l'écran de démarrage ---


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = DARKGREY
        self.text = text
        self.txt_surface = pygame.font.SysFont(
            "Arial", 18).render(text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = ORANGE if self.active else DARKGREY
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = DARKGREY
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = pygame.font.SysFont(
                "Arial", 18).render(self.text, True, BLACK)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = pygame.font.SysFont(
            "Arial", 18).render(text, True, WHITE)
        self.color = DARKGREY

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        txt_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, txt_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


# Création d'une liste d'InputBox pour saisir les noms (2 minimum)
input_boxes = [
    InputBox(50, 100, 200, 32),
    InputBox(50, 150, 200, 32)
]
add_button = Button(270, 100, 120, 32, "Ajouter joueur")
start_button = Button(50, 220, 150, 40, "Commencer")


def draw_start_screen():
    screen.fill(WHITE)
    title = pygame.font.SysFont("Arial", 24).render(
        "Jeu de l'Oie - Ajout des joueurs", True, BLACK)
    screen.blit(title, (50, 30))
    for box in input_boxes:
        box.update()
        box.draw(screen)
    add_button.draw(screen)
    start_button.draw(screen)
    instr = pygame.font.SysFont("Arial", 14).render(
        "Minimum 2 joueurs", True, BLACK)
    screen.blit(instr, (50, 280))

# --- Fonctions de log et affichage du plateau ---


def add_log(message):
    global logs
    logs.append(message)
    if len(logs) > 100:
        logs = logs[-100:]


def draw_board():
    board_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    board_surface.fill(WHITE)

    # Case départ (case 0)
    pygame.draw.rect(board_surface, LIGHTGREY, (0, 0, CELL_SIZE, CELL_SIZE))
    depart_surf = render_fitted_text("Départ", CELL_SIZE - 10, 14, BLACK)
    depart_rect = depart_surf.get_rect(center=(CELL_SIZE/2, CELL_SIZE/2))
    board_surface.blit(depart_surf, depart_rect)

    # Cases 1 à NB_CASES
    for num in range(1, NB_CASES+1):
        row = (num - 1) // NB_COLS
        col = ((num - 1) % NB_COLS) + 1
        x = col * CELL_SIZE
        y = row * CELL_SIZE

        fill_color = LIGHTGREY
        special_text = ""
        if num in SPECIAL_CASES:
            typ, _ = SPECIAL_CASES[num]
            if typ == "OIE":
                fill_color = LIGHTBLUE
            elif typ == "PONT":
                fill_color = ORANGE
            elif typ == "HOTEL":
                fill_color = PINK
            elif typ == "PUITS":
                fill_color = LIGHTGREEN
            elif typ == "LABYRINTHE":
                fill_color = VIOLET
            elif typ == "PRISON":
                fill_color = RED
            elif typ == "TETE DE MORT":
                fill_color = BLACK
            elif typ == "FINAL":
                fill_color = GOLD
            special_text = typ

        pygame.draw.rect(board_surface, fill_color,
                         (x, y, CELL_SIZE, CELL_SIZE))
        # Numéro de la case
        num_surf = render_fitted_text(
            str(num), CELL_SIZE - 10, 14, WHITE if fill_color == BLACK else BLACK)
        num_rect = num_surf.get_rect(center=(x + CELL_SIZE/2, y + CELL_SIZE/4))
        board_surface.blit(num_surf, num_rect)
        # Texte spécial
        if special_text:
            spec_surf = render_fitted_text(
                special_text, CELL_SIZE - 10, 14, WHITE if fill_color == BLACK else BLACK)
            spec_rect = spec_surf.get_rect(
                center=(x + CELL_SIZE/2, y + CELL_SIZE*0.75))
            board_surface.blit(spec_surf, spec_rect)

    draw_players(board_surface)
    screen.blit(board_surface, (0, 0))


def draw_players(surface):
    groups = {}
    for player in players:
        if player["pos"] == 0:
            key = (0, 0)
        else:
            row = (player["pos"] - 1) // NB_COLS
            col = ((player["pos"] - 1) % NB_COLS) + 1
            key = (row, col)
        groups.setdefault(key, []).append(player)

    token_width = 20
    token_height = 20
    gap_x = 5
    gap_y = 5

    for (row, col), group in groups.items():
        n = len(group)
        cell_x = col * CELL_SIZE
        cell_y = row * CELL_SIZE
        cell_center_x = cell_x + CELL_SIZE/2
        cell_center_y = cell_y + CELL_SIZE/2

        n_rows = math.ceil(n / 2)
        total_height = n_rows * token_height + (n_rows - 1) * gap_y
        start_y = cell_center_y - total_height / 2

        for i, player in enumerate(group):
            row_index = i // 2
            tokens_in_row = 2 if (i // 2 < n_rows - 1 or n % 2 == 0) else 1
            total_width = tokens_in_row * \
                token_width + (tokens_in_row - 1) * gap_x
            start_x = cell_center_x - total_width / 2
            pos_in_row = i % 2
            x = start_x + pos_in_row * (token_width + gap_x)
            y = start_y + row_index * (token_height + gap_y)
            pygame.draw.ellipse(
                surface, CYAN, (x, y, token_width, token_height))
            initial = render_fitted_text(
                player["name"][0], token_width, 14, BLACK)
            init_rect = initial.get_rect(
                center=(x + token_width/2, y + token_height/2))
            surface.blit(initial, init_rect)


def draw_logs():
    # Création d'une surface pour les logs
    log_surface = pygame.Surface((LOG_WIDTH, LOG_HEIGHT))
    log_surface.fill(WHITE)

    title = pygame.font.SysFont("Arial", 18).render("Logs", True, BLACK)
    log_surface.blit(title, (10, 10))

    start_y = 40 + log_scroll_offset  # Appliquer le décalage du scroll
    line_height = 18
    # Pour chaque log, on peut "enrouler" le texte si besoin
    log_font = pygame.font.SysFont("Arial", 14)
    for message in logs:
        # On découpe le message en lignes pour tenir dans LOG_WIDTH-20
        lines = render_wrapped_text(message, log_font, BLACK, LOG_WIDTH - 20)
        for line_surf in lines:
            log_surface.blit(line_surf, (10, start_y))
            start_y += line_height
    screen.blit(log_surface, (BOARD_WIDTH, 0))


def roll_dice():
    global current_player_idx, game_over
    p = players[current_player_idx]

    if p["skip"] > 0:
        add_log(f"{p['name']} doit passer ce tour.")
        p["skip"] -= 1
        next_player()
        return

    if p["prison"]:
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        add_log(f"{p['name']} (en prison) lance : {d1} et {d2}")
        if d1 == d2:
            add_log(f"{p['name']} a fait un double et est libéré de prison !")
            p["prison"] = False
            move_player(p, d1 + d2)
        else:
            add_log(f"{p['name']} n'a pas fait de double et reste en prison.")
        next_player()
        return

    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2
    add_log(f"{p['name']} lance : {d1} et {d2} (total = {total})")

    if p["first_turn"]:
        if (d1, d2) in [(6, 3), (3, 6)]:
            add_log(f"{p['name']} a fait 6+3, il va directement en case 26.")
            p["pos"] = 26
            p["first_turn"] = False
            check_win(p)
            next_player()
            return
        elif (d1, d2) in [(4, 5), (5, 4)]:
            add_log(f"{p['name']} a fait 4+5, il va directement en case 53.")
            p["pos"] = 53
            p["first_turn"] = False
            check_win(p)
            next_player()
            return

    move_player(p, total)
    check_win(p)
    next_player()


def move_player(p, steps):
    old_pos = p["pos"]
    new_pos = p["pos"] + steps
    if new_pos > NB_CASES:
        surplus = new_pos - NB_CASES
        new_pos = NB_CASES - surplus
        add_log(
            f"{p['name']} a dépassé la case finale et recule de {surplus} case(s).")
    p["pos"] = new_pos
    p["first_turn"] = False

    if new_pos in SPECIAL_CASES:
        typ, target = SPECIAL_CASES[new_pos]
        if typ == "OIE":
            add_log(
                f"{p['name']} tombe sur une OIE et avance de {steps} case(s) supplémentaires !")
            p["pos"] += steps
        elif typ == "PONT":
            add_log(
                f"{p['name']} est sur un PONT, il passe directement en case {target}.")
            p["pos"] = target
        elif typ == "HOTEL":
            add_log(f"{p['name']} est à l'HOTEL et va passer 2 tours.")
            p["skip"] = 2
        elif typ == "PUITS":
            add_log(
                f"{p['name']} tombe dans le PUITS et retourne en case {target}.")
            p["pos"] = target
        elif typ == "LABYRINTHE":
            add_log(
                f"{p['name']} est dans le LABYRINTHE et recule de 12 cases pour aller en case {target}.")
            p["pos"] = target
        elif typ == "PRISON":
            add_log(
                f"{p['name']} est en PRISON. Il devra faire un double pour en sortir.")
            p["prison"] = True
        elif typ == "TETE DE MORT":
            add_log(
                f"Oh non ! {p['name']} tombe sur la TÊTE DE MORT et retourne au départ.")
            p["pos"] = target
        elif typ == "FINAL":
            pass
    check_collision(p, old_pos)


def check_collision(current, old_pos):
    for p in players:
        if p is not current and p["pos"] == current["pos"]:
            add_log(
                f"{current['name']} atterrit sur {p['name']}. Les pions s'échangent !")
            p["pos"] = old_pos


def check_win(p):
    global game_over
    if p["pos"] == NB_CASES:
        add_log(f"Félicitations ! {p['name']} a gagné la partie !")
        game_over = True


def next_player():
    global current_player_idx
    current_player_idx = (current_player_idx + 1) % len(players)


# --- Boucle principale ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Gestion de l'écran de démarrage
        if game_state == "START":
            for box in input_boxes:
                box.handle_event(event)
            if add_button.is_clicked(event):
                new_y = input_boxes[-1].rect.y + 50
                input_boxes.append(InputBox(50, new_y, 200, 32))
            if start_button.is_clicked(event):
                names = [box.text.strip()
                         for box in input_boxes if box.text.strip() != ""]
                if len(names) < 2:
                    add_log("Erreur : Minimum 2 joueurs requis.")
                else:
                    players = [{"name": name, "pos": 0, "skip": 0,
                                "prison": False, "first_turn": True} for name in names]
                    game_state = "PLAYING"
                    add_log("Appuyez sur une touche pour lancer les dés.")
        # Gestion du défilement de la zone de logs avec la molette
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Molette haut
                log_scroll_offset += 20
            elif event.button == 5:  # Molette bas
                log_scroll_offset -= 20

        if game_state == "PLAYING" and not game_over:
            if event.type == pygame.KEYDOWN:
                roll_dice()

    if game_state == "START":
        draw_start_screen()
    elif game_state == "PLAYING":
        screen.fill(WHITE)
        draw_board()
        draw_logs()

    pygame.display.flip()
    clock.tick(30)
