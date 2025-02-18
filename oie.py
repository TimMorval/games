import tkinter as tk
from tkinter import messagebox
import random
import math

# Configuration du plateau
NB_CASES = 63   # Cases numérotées de 1 à 63 (la logique reste inchangée)
NB_COLS = 9     # Pour les cases 1 à 63, organisées sur 9 colonnes.
CELL_SIZE = 60

# La largeur du canvas tient compte de la case départ (colonne 0) + les NB_COLS
CANVAS_WIDTH = (NB_COLS + 1) * CELL_SIZE
NB_ROWS = ((NB_CASES - 1) // NB_COLS) + 1
CANVAS_HEIGHT = NB_ROWS * CELL_SIZE

# Définition des cases spéciales (pour les cases 1 à 63)
# Les valeurs de type seront affichées en petit en dessous du numéro.
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


class GooseGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jeu de l'Oie")
        self.players = []  # Liste des joueurs (dictionnaires)
        self.current_player = 0
        self.turn_number = {}
        self.setup_start_screen()

    def setup_start_screen(self):
        self.start_frame = tk.Frame(self)
        self.start_frame.pack(padx=10, pady=10)

        tk.Label(self.start_frame,
                 text="Jeu de l'Oie - Entrez les noms des joueurs").pack(pady=5)

        # Cadre pour les champs de saisie
        self.players_frame = tk.Frame(self.start_frame)
        self.players_frame.pack(pady=5)

        # Liste des entrées pour les noms des joueurs
        self.player_entries = []
        # Ajouter initialement deux joueurs
        for _ in range(2):
            self.add_player_entry()

        # Bouton pour ajouter d'autres joueurs
        tk.Button(self.start_frame, text="Ajouter un joueur",
                  command=self.add_player_entry).pack(pady=5)
        tk.Button(self.start_frame, text="Commencer le jeu",
                  command=self.start_game).pack(pady=10)

    def add_player_entry(self):
        entry = tk.Entry(self.players_frame)
        entry.pack(pady=2)
        self.player_entries.append(entry)

    def start_game(self):
        # Récupération des noms et initialisation des joueurs
        self.players = []
        for entry in self.player_entries:
            name = entry.get().strip()
            if name == "":
                messagebox.showerror(
                    "Erreur", "Veuillez entrer un nom pour chaque joueur.")
                return
            self.players.append({
                "name": name,
                "pos": 0,         # Tous commencent sur la case départ (0)
                "skip": 0,        # Nombre de tours à passer (ex: hôtel)
                "prison": False,  # Indique s'il est en prison
                "first_turn": True  # Pour la règle spéciale du premier tour
            })
            self.turn_number[name] = 1

        # Vérifier qu'il y a au moins 2 joueurs
        if len(self.players) < 2:
            messagebox.showerror(
                "Erreur", "Veuillez ajouter au moins deux joueurs.")
            return

        self.start_frame.destroy()
        self.setup_game_screen()

    def setup_game_screen(self):
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH,
                                height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)
        self.draw_board()

        self.info_label = tk.Label(self, text="")
        self.info_label.pack(pady=5)
        self.update_info()

        self.dice_button = tk.Button(
            self, text="Lancer les dés", command=self.roll_dice)
        self.dice_button.pack(pady=5)

    def draw_board(self):
        self.canvas.delete("all")
        # Dessiner la case départ (0) à gauche de la case 1
        x1 = 0
        y1 = 0
        x2 = CELL_SIZE
        y2 = CELL_SIZE
        self.canvas.create_rectangle(
            x1, y1, x2, y2, fill="lightgrey", outline="black")
        # Affichage de "Départ" dans la case départ
        self.canvas.create_text(
            x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, text="Départ", fill="black")

        # Dessiner les cases 1 à NB_CASES.
        for num in range(1, NB_CASES+1):
            row = (num - 1) // NB_COLS
            col = ((num - 1) % NB_COLS) + 1  # Décalage pour la case départ
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            fill_color = "lightgrey"
            special_text = ""
            if num in SPECIAL_CASES:
                typ, _ = SPECIAL_CASES[num]
                if typ == "OIE":
                    fill_color = "lightblue"
                elif typ == "PONT":
                    fill_color = "orange"
                elif typ == "HOTEL":
                    fill_color = "pink"
                elif typ == "PUITS":
                    fill_color = "lightgreen"
                elif typ == "LABYRINTHE":
                    fill_color = "violet"
                elif typ == "PRISON":
                    fill_color = "red"
                elif typ == "TETE DE MORT":
                    fill_color = "black"
                elif typ == "FINAL":
                    fill_color = "gold"
                # Le texte spécial en petit (en dessous du numéro)
                special_text = typ

            # Dessiner la case
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=fill_color, outline="black")
            # Afficher le numéro en haut (par exemple, en haut du centre)
            self.canvas.create_text(
                x1 + CELL_SIZE/2, y1 + CELL_SIZE/3, text=str(num), font=("Arial", int(CELL_SIZE/4)), fill="white" if fill_color == "black" else "black")
            # Si la case est spéciale, afficher en petit le texte en dessous du numéro
            if special_text:
                self.canvas.create_text(
                    x1 + CELL_SIZE/2, y1 + CELL_SIZE*0.75, text=special_text, font=("Arial", int(CELL_SIZE/8)), fill="white" if fill_color == "black" else "black")

        self.draw_players()

    def draw_players(self):
        # Regrouper les joueurs par case (clé : (row, col))
        groups = {}
        for player in self.players:
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

        for (row, col), players_list in groups.items():
            n = len(players_list)
            cell_x = col * CELL_SIZE
            cell_y = row * CELL_SIZE
            cell_center_x = cell_x + CELL_SIZE / 2
            cell_center_y = cell_y + CELL_SIZE / 2

            n_rows = math.ceil(n / 2)
            total_height = n_rows * token_height + (n_rows - 1) * gap_y
            start_y = cell_center_y - total_height / 2

            for i, player in enumerate(players_list):
                row_index = i // 2
                tokens_in_row = 2 if (i // 2 < n_rows - 1 or n % 2 == 0) else 1
                total_width = tokens_in_row * \
                    token_width + (tokens_in_row - 1) * gap_x
                start_x = cell_center_x - total_width / 2
                pos_in_row = i % 2
                x = start_x + pos_in_row * (token_width + gap_x)
                y = start_y + row_index * (token_height + gap_y)
                self.canvas.create_oval(
                    x, y, x + token_width, y + token_height, fill="cyan")
                self.canvas.create_text(
                    x + token_width/2, y + token_height/2, text=player["name"][0], fill="black")

    def update_info(self):
        p = self.players[self.current_player]
        status = f"C'est au tour de {p['name']} (case {p['pos']})"
        if p["skip"] > 0:
            status += f" [saute {p['skip']} tour(s)]"
        if p["prison"]:
            status += " [en prison]"
        self.info_label.config(text=status)

    def roll_dice(self):
        p = self.players[self.current_player]
        if p["skip"] > 0:
            messagebox.showinfo(
                "Information", f"{p['name']} doit passer ce tour.")
            p["skip"] -= 1
            self.next_player()
            return

        if p["prison"]:
            d1, d2 = random.randint(1, 6), random.randint(1, 6)
            messagebox.showinfo(
                "Dés", f"{p['name']} (en prison) lance les dés : {d1} et {d2}")
            if d1 == d2:
                messagebox.showinfo(
                    "Libération", f"{p['name']} a fait un double et est libéré de prison !")
                p["prison"] = False
                self.move_player(p, d1+d2)
            else:
                messagebox.showinfo(
                    "En prison", f"{p['name']} n'a pas fait de double et reste en prison.")
            self.next_player()
            return

        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        total = d1 + d2
        messagebox.showinfo(
            "Dés", f"{p['name']} lance les dés : {d1} et {d2} (total = {total})")

        if p["first_turn"]:
            if (d1, d2) in [(6, 3), (3, 6)]:
                messagebox.showinfo(
                    "Règle spéciale", f"{p['name']} a fait 6+3 au premier tour, il va directement en case 26.")
                p["pos"] = 26
                p["first_turn"] = False
                self.draw_board()
                self.check_win(p)
                self.next_player()
                return
            elif (d1, d2) in [(4, 5), (5, 4)]:
                messagebox.showinfo(
                    "Règle spéciale", f"{p['name']} a fait 4+5 au premier tour, il va directement en case 53.")
                p["pos"] = 53
                p["first_turn"] = False
                self.draw_board()
                self.check_win(p)
                self.next_player()
                return

        self.move_player(p, total)
        self.draw_board()
        self.check_win(p)
        self.next_player()

    def move_player(self, p, steps):
        old_pos = p["pos"]
        new_pos = p["pos"] + steps
        if new_pos > NB_CASES:
            surplus = new_pos - NB_CASES
            new_pos = NB_CASES - surplus
            messagebox.showinfo(
                "Dépassement", f"{p['name']} a dépassé la case finale et recule de {surplus} case(s).")
        p["pos"] = new_pos
        p["first_turn"] = False
        if new_pos in SPECIAL_CASES:
            typ, target = SPECIAL_CASES[new_pos]
            if typ == "OIE":
                messagebox.showinfo(
                    "Oie", f"{p['name']} est tombé sur une OIE et avance de {steps} case(s) supplémentaires !")
                p["pos"] += steps
            elif typ == "PONT":
                messagebox.showinfo(
                    "Pont", f"{p['name']} est sur un PONT, il passe directement en case {target}.")
                p["pos"] = target
            elif typ == "HOTEL":
                messagebox.showinfo(
                    "Hôtel", f"{p['name']} est à l'HOTEL et va passer 2 tours.")
                p["skip"] = 2
            elif typ == "PUITS":
                messagebox.showinfo(
                    "Puits", f"{p['name']} est tombé dans le PUITS et retourne en case {target}.")
                p["pos"] = target
            elif typ == "LABYRINTHE":
                messagebox.showinfo(
                    "Labyrinthe", f"{p['name']} est dans le LABYRINTHE et recule de 12 cases pour aller en case {target}.")
                p["pos"] = target
            elif typ == "PRISON":
                messagebox.showinfo(
                    "Prison", f"{p['name']} est en PRISON. Il devra faire un double pour en sortir.")
                p["prison"] = True
            elif typ == "TETE DE MORT":
                messagebox.showinfo(
                    "Tête de mort", f"Oh non ! {p['name']} est tombé sur la TÊTE DE MORT et retourne au départ.")
                p["pos"] = target
            elif typ == "FINAL":
                pass
        self.check_collision(p, old_pos)

    def check_collision(self, current, old_pos):
        for p in self.players:
            if p is not current and p["pos"] == current["pos"]:
                messagebox.showinfo(
                    "Collision", f"{current['name']} atterrit sur {p['name']}. Les pions s'échangent !")
                p["pos"] = old_pos

    def check_win(self, p):
        if p["pos"] == NB_CASES:
            messagebox.showinfo(
                "Victoire", f"Félicitations ! {p['name']} a gagné la partie !")
            self.dice_button.config(state=tk.DISABLED)

    def next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.update_info()

    def update_info(self):
        p = self.players[self.current_player]
        status = f"C'est au tour de {p['name']} (case {p['pos']})"
        if p["skip"] > 0:
            status += f" [saute {p['skip']} tour(s)]"
        if p["prison"]:
            status += " [en prison]"
        self.info_label.config(text=status)


if __name__ == "__main__":
    app = GooseGame()
    app.mainloop()
