"""Tank Battle 2D - run with: python tank_battle.py"""
import math
import random
import time
import tkinter as tk
from collections import deque
import json
from pathlib import Path


WIDTH, HEIGHT, CELL = 960, 640, 32
COLS, ROWS = WIDTH // CELL, HEIGHT // CELL
ITEM_SPAWN_MS = 3000
ITEM_NAMES = {
    "speed": ("Tăng tốc", "#39d98a"),
    "freeze": ("Đóng băng", "#75c9ff"),
    "ammo": ("Nạp 7 đạn", "#ffd166"),
    "heal": ("Hồi 2 máu", "#58e28c"),
    "rapid": ("Đạn vô hạn", "#f78c6b"),
    "bomb": ("Bom hẹn giờ", "#bf7bff"),
    "pierce": ("Xuyên tường", "#ff5cc8"),
}


class TankBattle:
    def __init__(self, root):
        self.root = root
        self.root.title("Tank Battle 2D")
        self.root.configure(bg="#101827")
        self.level = tk.StringVar(value="normal")
        self.running = False
        self.scores_path = Path(__file__).with_name("tank_scores.json")
        self.high_scores = self.load_scores()
        self.last_tick = time.monotonic()
        self.build_menu()
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

    def build_menu(self):
        self.menu = tk.Frame(self.root, bg="#101827", padx=30, pady=25)
        self.menu.pack(fill="both", expand=True)
        tk.Label(self.menu, text="TANK BATTLE", fg="#f7d774", bg="#101827",
                 font=("Arial", 28, "bold")).pack(pady=(30, 8))
        tk.Label(self.menu, text="Xe tăng 2D • Sinh tồn qua 3 độ khó", fg="#aab6cc",
                 bg="#101827", font=("Arial", 12)).pack(pady=(0, 25))
        for value, text in [("easy", "EASY  —  Kẻ địch lang thang, phát hiện trong 5 ô"),
                            ("normal", "NORMAL  —  Kẻ địch truy sát và bắn chủ động"),
                            ("hard", "HARD  —  Kẻ địch phối hợp vây ép trong 10 ô")]:
            tk.Radiobutton(self.menu, text=text, variable=self.level, value=value,
                           fg="#e5eaf3", selectcolor="#1d2b45", bg="#101827",
                           activebackground="#101827", activeforeground="#ffffff",
                           font=("Arial", 11), anchor="w", width=52).pack(pady=4)
        tk.Button(self.menu, text="BẮT ĐẦU", command=self.start, bg="#f7d774", fg="#182033",
                  relief="flat", font=("Arial", 13, "bold"), padx=28, pady=10).pack(pady=24)
        tk.Label(self.menu, text="← ↑ → ↓: di chuyển     Enter: bắn     Space: dùng item\n"
                                  "Hàng đợi tối đa 3 item — nhặt món mới nhất sẽ thay item cũ nhất.",
                 justify="center", fg="#92a0ba", bg="#101827", font=("Arial", 10)).pack()

    def load_scores(self):
        try:
            data = json.loads(self.scores_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save_score(self, name):
        name = name.strip()[:16] or "Người chơi"
        self.high_scores.append({"name": name, "score": self.score, "mode": self.level.get()})
        self.high_scores.sort(key=lambda entry: entry["score"], reverse=True)
        self.high_scores = self.high_scores[:3]
        self.scores_path.write_text(json.dumps(self.high_scores, ensure_ascii=False, indent=2), encoding="utf-8")
        self.show_leaderboard()

    def back_home(self):
        if hasattr(self, "end_screen"): self.end_screen.destroy()
        elif hasattr(self, "canvas"): self.canvas.destroy()
        self.build_menu()

    def show_end_screen(self, won):
        self.canvas.destroy()
        self.end_screen = tk.Frame(self.root, bg="#101827", padx=30, pady=20)
        self.end_screen.pack(fill="both", expand=True)
        title = "CHIẾN THẮNG!" if won else "GAME OVER"
        color = "#63dfaa" if won else "#ff7279"
        tk.Label(self.end_screen, text=title, fg=color, bg="#101827", font=("Arial", 27, "bold")).pack(pady=(18, 5))
        tk.Label(self.end_screen, text=f"Điểm của bạn: {self.score}", fg="#f7d774", bg="#101827", font=("Arial", 16, "bold")).pack(pady=(0, 14))
        save = tk.Frame(self.end_screen, bg="#101827")
        save.pack(pady=4)
        tk.Label(save, text="Tên người chơi:", fg="#cbd5e8", bg="#101827", font=("Arial", 11)).pack(side="left", padx=6)
        self.name_input = tk.Entry(save, width=20, font=("Arial", 11))
        self.name_input.insert(0, "Người chơi")
        self.name_input.pack(side="left", padx=6)
        tk.Button(save, text="LƯU ĐIỂM", command=lambda: self.save_score(self.name_input.get()),
                  bg="#f7d774", fg="#172238", relief="flat", font=("Arial", 10, "bold")).pack(side="left", padx=6)
        self.leaderboard = tk.Label(self.end_screen, bg="#172238", fg="#eaf1ff", justify="left", width=42,
                                    padx=16, pady=11, font=("Consolas", 11))
        self.leaderboard.pack(pady=16)
        self.show_leaderboard()
        buttons = tk.Frame(self.end_screen, bg="#101827")
        buttons.pack(pady=6)
        tk.Button(buttons, text="↻  CHƠI LẠI", command=self.replay, bg="#45d3a0", fg="#102033", relief="flat",
                  font=("Arial", 11, "bold"), padx=16, pady=8).pack(side="left", padx=7)
        tk.Button(buttons, text="⌂  CHỌN ĐỘ KHÓ", command=self.back_home, bg="#36425b", fg="#ffffff", relief="flat",
                  font=("Arial", 11, "bold"), padx=16, pady=8).pack(side="left", padx=7)

    def show_leaderboard(self):
        rows = ["  TOP 3 NGƯỜI CHƠI CAO ĐIỂM", ""]
        for index, entry in enumerate(self.high_scores, start=1):
            rows.append(f"  {index}. {entry['name']:<16} {entry['score']:>5}  {entry['mode'].upper()}")
        while len(rows) < 5: rows.append("  —")
        self.leaderboard.config(text="\n".join(rows))

    def replay(self):
        self.end_screen.destroy()
        self.start()

    def start(self):
        self.menu.destroy()
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#182235", highlightthickness=0)
        self.canvas.pack()
        self.keys = set()
        self.player = {"x": 4.5, "y": 9.5, "angle": 0, "ammo": 0, "items": deque(maxlen=3),
                       "speed_until": 0, "rapid_until": 0, "pierce_until": 0, "hp": 5,
                       "shoot_cooldown": 0}
        count = {"easy": 4, "normal": 6, "hard": 8}[self.level.get()]
        self.walls = self.make_walls()
        self.enemies = []
        for _ in range(count):
            x, y = self.find_free_position(min_distance=7)
            self.enemies.append({"x": x, "y": y,
                                 "angle": random.random() * math.tau, "hp": 2, "cooldown": random.uniform(0, 1),
                                 "wander": random.random() * math.tau, "target": None})
        self.bullets, self.items, self.bombs = [], [], []
        self.message, self.message_until = "Tìm item Nạp 7 đạn để bắt đầu bắn!", time.monotonic() + 4
        self.frozen_until = 0
        self.next_item = time.monotonic() + 1
        self.score = 0
        self.running = True
        self.last_tick = time.monotonic()
        self.tick()

    def make_walls(self):
        walls = set()
        for x in range(COLS): walls.update({(x, 0), (x, ROWS - 1)})
        for y in range(ROWS): walls.update({(0, y), (COLS - 1, y)})
        for x, y, w, h in [(8, 3, 1, 6), (15, 1, 1, 5), (21, 8, 1, 7), (10, 13, 6, 1), (25, 3, 3, 1)]:
            for xx in range(x, x + w):
                for yy in range(y, y + h): walls.add((xx, yy))
        return walls

    def find_free_position(self, min_distance=0):
        """Return the center of an empty map cell, away from the player's spawn."""
        for _ in range(200):
            x, y = random.randint(1, COLS - 2) + .5, random.randint(1, ROWS - 2) + .5
            if not self.solid(x, y) and math.dist((x, y), (4.5, 9.5)) >= min_distance:
                return x, y
        return 2.5, 2.5  # map always has this open fallback cell

    def key_down(self, event):
        if self.running: self.keys.add(event.keysym)
    def key_up(self, event):
        self.keys.discard(event.keysym)

    def solid(self, x, y, ignore_walls=False):
        # The map border remains solid even when the player has the wall-piercing effect.
        return (not ignore_walls and (int(x), int(y)) in self.walls) or x < .5 or y < .5 or x > COLS - .5 or y > ROWS - .5

    def move(self, obj, dx, dy):
        nx, ny = obj["x"] + dx, obj["y"] + dy
        moved = False
        ghost = obj is self.player and time.monotonic() < self.player["pierce_until"]
        if not self.solid(nx, obj["y"], ghost): obj["x"] = nx
        if dx and obj["x"] == nx: moved = True
        if not self.solid(obj["x"], ny, ghost): obj["y"] = ny
        if dy and obj["y"] == ny: moved = True
        return moved

    def shoot(self, owner, x, y, angle):
        now = time.monotonic()
        unlimited = owner == "player" and now < self.player["rapid_until"]
        piercing = owner == "player" and now < self.player["pierce_until"]
        if owner == "player" and self.player["ammo"] <= 0 and not unlimited:
            self.flash("Không có đạn — hãy nhặt item vàng!")
            return
        if owner == "player" and not unlimited: self.player["ammo"] -= 1
        self.bullets.append({"x": x, "y": y, "dx": math.cos(angle) * 10, "dy": math.sin(angle) * 10,
                             "owner": owner, "pierce": piercing, "unlimited": unlimited, "life": 2})

    def use_item(self):
        if not self.player["items"]:
            self.flash("Chưa có item để dùng!"); return
        kind = self.player["items"].popleft(); now = time.monotonic()
        if kind == "speed": self.player["speed_until"] = now + 10
        elif kind == "freeze": self.frozen_until = now + 3
        elif kind == "ammo": self.player["ammo"] += 7
        elif kind == "heal": self.player["hp"] = min(5, self.player["hp"] + 2)
        elif kind == "rapid": self.player["rapid_until"] = now + 5
        elif kind == "pierce": self.player["pierce_until"] = now + 5
        elif kind == "bomb": self.bombs.append({"x": self.player["x"], "y": self.player["y"], "explode": now + 3})
        self.flash("Dùng: " + ITEM_NAMES[kind][0])

    def player_update(self, dt):
        dx = ("Right" in self.keys) - ("Left" in self.keys); dy = ("Down" in self.keys) - ("Up" in self.keys)
        if dx or dy:
            self.player["angle"] = math.atan2(dy, dx)
            speed = 4.8 if time.monotonic() < self.player["speed_until"] else 3.0
            self.move(self.player, dx * speed * dt, dy * speed * dt)
        self.player["shoot_cooldown"] = max(0, self.player["shoot_cooldown"] - dt)
        if "Return" in self.keys and self.player["shoot_cooldown"] <= 0:
            unlimited = time.monotonic() < self.player["rapid_until"]
            self.shoot("player", self.player["x"], self.player["y"], self.player["angle"])
            # Holding Enter gives a visible rapid-fire stream only while the infinite-ammo effect is active.
            self.player["shoot_cooldown"] = .11 if unlimited else .28
        if "space" in self.keys:
            self.keys.discard("space"); self.use_item()
        for item in self.items[:]:
            if math.dist((self.player["x"], self.player["y"]), (item["x"], item["y"])) < .75:
                self.items.remove(item)
                if item["kind"] == "ammo":
                    # Ammunition is equipped immediately, so Enter can fire without spending a queue slot.
                    self.player["ammo"] += 7
                    self.flash("Nhặt: Nạp 7 đạn — Enter để bắn!")
                else:
                    self.player["items"].append(item["kind"])
                    self.flash("Nhặt: " + ITEM_NAMES[item["kind"]][0])

    def enemy_update(self, dt):
        now = time.monotonic()
        if now < self.frozen_until: return
        hard = self.level.get() == "hard"
        for e in self.enemies:
            dist = math.dist((e["x"], e["y"]), (self.player["x"], self.player["y"]))
            sees = dist <= 5
            angle = e["wander"]
            spotter = None
            if sees:
                angle = math.atan2(self.player["y"] - e["y"], self.player["x"] - e["x"])
            elif hard:
                allies = [a for a in self.enemies if a is not e and math.dist((a["x"], a["y"]), (e["x"], e["y"])) <= 10]
                spotter = next((a for a in allies if math.dist((a["x"], a["y"]), (self.player["x"], self.player["y"])) <= 5), None)
                if spotter:  # flank around the shared target
                    angle = math.atan2(self.player["y"] - e["y"], self.player["x"] - e["x"]) + (0.65 if id(e) % 2 else -0.65)
            if not sees and not (hard and spotter):
                e["wander"] += random.uniform(-1.3, 1.3) * dt
            e["angle"] = angle
            if not self.move(e, math.cos(angle) * 1.25 * dt, math.sin(angle) * 1.25 * dt):
                # A wall is blocking the direct route: pick a new heading rather than staying stuck.
                e["wander"] = angle + random.choice((-1, 1)) * random.uniform(.8, 1.6)
            e["cooldown"] -= dt
            if sees and e["cooldown"] <= 0:
                self.shoot("enemy", e["x"], e["y"], angle); e["cooldown"] = random.uniform(.8, 1.6)

    def update_bullets(self, dt):
        for b in self.bullets[:]:
            b["life"] -= dt; b["x"] += b["dx"] * dt; b["y"] += b["dy"] * dt
            blocked = self.solid(b["x"], b["y"])
            if blocked and not b["pierce"]: b["life"] = 0
            targets = self.enemies if b["owner"] == "player" else [self.player]
            for target in targets[:]:
                if math.dist((b["x"], b["y"]), (target["x"], target["y"])) < .55:
                    target["hp"] -= 1
                    if b["owner"] == "player":
                        if target["hp"] <= 0: self.enemies.remove(target); self.score += 100
                        if not b["pierce"]: b["life"] = 0
                    else: b["life"] = 0
            if b["life"] <= 0: self.bullets.remove(b)

    def spawn_item(self):
        if len(self.items) >= 5: return
        x, y = self.find_free_position(min_distance=2)
        self.items.append({"x": x, "y": y, "kind": random.choice(list(ITEM_NAMES))})

    def flash(self, message):
        self.message, self.message_until = message, time.monotonic() + 2.5

    def draw(self):
        c = self.canvas; c.delete("all")
        for x, y in self.walls: c.create_rectangle(x*CELL, y*CELL, (x+1)*CELL, (y+1)*CELL, fill="#36425b", outline="#4b5976")
        # The real top border is in row 0; repeat it below the HUD so it stays visible.
        c.create_rectangle(0, 47, WIDTH, 52, fill="#36425b", outline="#4b5976")
        for item in self.items:
            name, color = ITEM_NAMES[item["kind"]]; x, y = item["x"]*CELL, item["y"]*CELL
            c.create_oval(x-11,y-11,x+11,y+11,fill=color,outline="#f6fbff",width=2); c.create_text(x,y,text=name[0],fill="#152036",font=("Arial",10,"bold"))
        for bomb in self.bombs:
            x,y=bomb["x"]*CELL,bomb["y"]*CELL; c.create_oval(x-11,y-11,x+11,y+11,fill="#d94949",outline="#ffe5a3",width=2)
        for e in self.enemies: self.draw_tank(e, "#ee5d64")
        self.draw_tank(self.player, "#45d3a0")
        for b in self.bullets:
            color = "#ff5cc8" if b["pierce"] else ("#ff9f43" if b["unlimited"] else "#fff4ac")
            c.create_oval(b["x"]*CELL-4,b["y"]*CELL-4,b["x"]*CELL+4,b["y"]*CELL+4,fill=color,outline="")
        c.create_rectangle(0,0,WIDTH,47,fill="#0e1523",outline="")
        effects = []
        now=time.monotonic()
        for k,label,until in [("speed","⚡ Speed",self.player["speed_until"]),("rapid","∞ Bắn",self.player["rapid_until"]),("pierce","⟿ Xuyên",self.player["pierce_until"])]:
            if now<until: effects.append(f"{label} {until-now:.0f}s")
        c.create_text(14,14,anchor="w",text=f"HP: {'♥'*self.player['hp']}   Đạn: {self.player['ammo']}   Điểm: {self.score}",fill="#f3f6ff",font=("Arial",12,"bold"))
        c.create_text(14,34,anchor="w",text="Hiệu ứng: " + (" • ".join(effects) or "—"),fill="#9eb0d1",font=("Arial",9))
        q="  ".join(ITEM_NAMES[k][0] for k in self.player["items"]) or "Trống"
        c.create_text(WIDTH-14,14,anchor="e",text=f"Item [{len(self.player['items'])}/3]: {q}",fill="#f7d774",font=("Arial",11,"bold"))
        c.create_text(WIDTH-14,34,anchor="e",text=f"Độ khó: {self.level.get().upper()} | Còn {len(self.enemies)} quái",fill="#9eb0d1",font=("Arial",9))
        if now < self.message_until: c.create_text(WIDTH/2,70,text=self.message,fill="#ffffff",font=("Arial",13,"bold"))

    def draw_tank(self, t, color):
        c=self.canvas; x,y=t["x"]*CELL,t["y"]*CELL; a=t["angle"]
        # Square hull, treads and turret make the tank instantly readable in motion.
        c.create_rectangle(x-15, y-11, x+15, y+11, fill="#1b2638", outline="#0d1420", width=2)
        c.create_rectangle(x-12, y-8, x+12, y+8, fill=color, outline="#e7faff", width=1)
        c.create_line(x, y, x + math.cos(a)*21, y + math.sin(a)*21, fill="#243244", width=7)
        c.create_line(x, y, x + math.cos(a)*21, y + math.sin(a)*21, fill="#d9e7ef", width=3)
        c.create_rectangle(x-5, y-5, x+5, y+5, fill=color, outline="#ffffff")
        if "hp" in t and t is not self.player:
            c.create_rectangle(x-12,y-18,x+12,y-15,fill="#541c28",outline="")
            c.create_rectangle(x-12,y-18,x-12+12*t["hp"],y-15,fill="#83e199",outline="")

    def tick(self):
        if not self.running: return
        now=time.monotonic(); dt=min(.05, now-self.last_tick); self.last_tick=now
        self.player_update(dt); self.enemy_update(dt); self.update_bullets(dt)
        for bomb in self.bombs[:]:
            if now >= bomb["explode"]:
                for e in self.enemies[:]:
                    if math.dist((bomb["x"],bomb["y"]),(e["x"],e["y"]))<2.7: self.enemies.remove(e); self.score += 100
                self.bombs.remove(bomb); self.flash("BOM! Kích nổ vị trí đã đặt")
        if now >= self.next_item: self.spawn_item(); self.next_item = now + ITEM_SPAWN_MS/1000
        ended = None
        if self.player["hp"] <= 0: self.running=False; ended = False
        elif not self.enemies: self.running=False; ended = True
        self.draw()
        if self.running: self.root.after(16, self.tick)
        elif ended is not None: self.root.after(350, lambda: self.show_end_screen(ended))


if __name__ == "__main__":
    root = tk.Tk()
    TankBattle(root)
    root.mainloop()
