import pygame, random, math, sys
pygame.init()
info = pygame.display.Info()
W, H = (info.current_w, info.current_h) if info.current_w > 0 else (1080, 2436)
if H > W: W, H = H, W
screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", int(H * 0.024), bold=True)
DB = {
    "Верхний кварк": ((255, 50, 50), 2, 100), "Нижний кварк": ((50, 50, 255), -1, 100),
    "Странный кварк": ((0, 255, 255), -1, 120), "Очарованный кварк": ((255, 0, 255), 2, 150),
    "Прелестный кварк": ((255, 165, 0), -1, 200), "Истинный кварк": ((255, 255, 255), 2, 300)
}
class Particle:
    def __init__(self, name, x=None, y=None, is_p=False, is_anti=False):
        self.is_p, self.is_anti, self.is_lonely, self.was_lonely = is_p, is_anti, False, False
        if is_p: self.name, self.color, self.charge, self.hp, self.radius = "Протон", (245, 245, 250), 3, 600, 30
        else:
            bn = name.replace("Анти-", "")
            self.color, bc, bhp = DB[bn]
            self.charge, self.hp, self.radius = (-bc if is_anti else bc), float(bhp), 15
            self.name = f"Анти-{bn}" if is_anti else bn
        self.x = float(x if x else random.randint(150, W - 150))
        self.y = float(y if y else random.randint(100, H - 200))
        self.dx, self.dy = float(random.uniform(-3, 3)), float(random.uniform(-3, 3))
        self.t_name = font.render(self.name, True, (255, 255, 255))
        self.hp_color = (0, 220, 255) if self.is_p else (50, 255, 50)
        self.last_hp_int, self.t_hp = -1, None
    def update(self):
        if self.x < 120: self.dx += (120 - self.x) * 0.2
        elif self.x > W - 120: self.dx -= (self.x - (W - 120)) * 0.2
        if self.y < 140: self.dy += (140 - self.y) * 0.2
        elif self.y > H - 150: self.dy -= (self.y - (H - 150)) * 0.2
        spd = math.sqrt(self.dx**2 + self.dy**2)
        if spd > 12.0: self.dx, self.dy = (self.dx/spd)*12.0, (self.dy/spd)*12.0
        self.x, self.y = self.x + self.dx, self.y + self.dy
        if self.x < 30 or self.x > W - 30: self.dx *= -1; self.x = max(30, min(self.x, W - 30))
        if self.y < 50 or self.y > H - 50: self.dy *= -1; self.y = max(50, min(self.y, H - 50))
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        if self.is_p: pygame.draw.circle(screen, (0, 190, 255), (int(self.x), int(self.y)), self.radius + 3, 3)
        else:
            if self.is_anti: pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius + 2, 3)
            if self.is_lonely: pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.radius + 6, 3)
        screen.blit(self.t_name, (int(self.x) - self.t_name.get_width()//2, int(self.y) - self.radius - 40))
        curr_hp = int(self.hp)
        if curr_hp != self.last_hp_int:
            self.last_hp_int = curr_hp
            self.t_hp = font.render(f"{curr_hp} HP", True, self.hp_color)
        screen.blit(self.t_hp, (int(self.x) - self.t_hp.get_width()//2, int(self.y) - self.radius - 20))
particles = [Particle(random.choice(list(DB.keys()))) for _ in range(15)]
start_ticks = pygame.time.get_ticks()
while True:
    for event in pygame.event.get_loop() if hasattr(pygame, "get_loop") else pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for _ in range(3):
                if len(particles) < 30:
                    rand_t = random.choice(list(DB.keys()))
                    is_a = random.choice([True, False])
                    p_new = Particle(rand_t, x=mx + random.randint(-15, 15), y=my + random.randint(-15, 15), is_anti=is_a)
                    angle = random.uniform(0, 2 * math.pi)
                    force = random.uniform(4.0, 7.0)
                    p_new.dx, p_new.dy = math.cos(angle) * force, math.sin(angle) * force
                    particles.append(p_new)
    screen.fill((5, 5, 15))
    num = len(particles)
    merged, annihilated, new_p = set(), set(), []
    groups = {p: i for i, p in enumerate(particles)}
    active_links = []
    for i in range(num):
        p1 = particles[i]
        for j in range(i + 1, num):
            p2 = particles[j]
            if p2 in annihilated or p1 in annihilated: continue
            if p1.is_p or p2.is_p:
                p, q = (p1, p2) if p1.is_p else (p2, p1)
                if not q.is_p and num < 40:
                    g_dx, g_dy = p.x - q.x, p.y - q.y
                    g_dst = math.sqrt(g_dx**2 + g_dy**2) or 1
                    if g_dst < 500: q.dx += (g_dx/g_dst)*0.15; q.dy += (g_dy/g_dst)*0.15
                continue
            dx, dy = p2.x - p1.x, p2.y - p1.y
            d_sq = dx**2 + dy**2
            if (p1.charge > 0 and p2.charge > 0) or (p1.charge < 0 and p2.charge < 0):
                if 0 < d_sq < 90000:
                    d = math.sqrt(d_sq); p1.dx -= (dx/d)*0.2; p1.dy -= (dy/d)*0.2; p2.dx += (dx/d)*0.2; p2.dy += (dy/d)*0.2
            elif d_sq < 160000: 
                g1, g2 = groups[p1], groups[p2]
                if g1 != g2:
                    s1 = sum(1 for p in particles if groups[p] == g1)
                    s2 = sum(1 for p in particles if groups[p] == g2)
                    if s1 + s2 <= 3:
                        for p in particles:
                            if groups[p] == g2: groups[p] = g1
                        active_links.append((p1, p2))
                        if num < 45:
                            r, g, b = (p1.color[0]+p2.color[0])//2, (p1.color[1]+p2.color[1])//2, (p1.color[2]+p2.color[2])//2
                            pygame.draw.line(screen, (r, g, b), (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), 2)
    for p1, p2 in active_links:
        dx, dy = p2.x - p1.x, p2.y - p1.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            strong = dist * 0.0004
            p1.dx += strong * (dx / dist); p1.dy += strong * (dy / dist)
            p2.dx -= strong * (dx / dist); p2.dy -= strong * (dy / dist)
    for i in range(num):
        p = particles[i]
        if p.is_p or p in annihilated: continue
        g_size = sum(1 for other in particles if groups[other] == groups[p])
        if g_size == 1:
            p.is_lonely = True
            if not p.was_lonely: p.hp -= 15.0  
            p.hp -= 0.5  
        else: p.is_lonely = False
        p.was_lonely = p.is_lonely
    for i in range(num):
        p1 = particles[i]
        if p1 in merged or p1 in annihilated or p1.hp <= 0: continue
        for j in range(i + 1, num):
            p2 = particles[j]
            if p2 in merged or p2 in annihilated or p2.hp <= 0: continue
            dx, dy = p2.x - p1.x, p2.y - p1.y
            dist_sq = dx**2 + dy**2
            if dist_sq < (p1.radius + p2.radius)**2:
                if not p1.is_p and not p2.is_p and (p1.is_anti != p2.is_anti):
                    annihilated.update([p1, p2])
                    pygame.draw.circle(screen, (255, 255, 255), (int((p1.x+p2.x)/2), int((p1.y+p2.y)/2)), 40)
                    break
                d = math.sqrt(dist_sq) or 1
                if not p1.is_p and not p2.is_p and p1.charge != p2.charge: p1.hp -= 8; p2.hp -= 8
                if not p1.is_p and not p2.is_p and not p1.is_anti and not p2.is_anti:
                    for k in range(num):
                        p3 = particles[k]
                        if p3 == p1 or p3 == p2 or p3 in merged or p3 in annihilated or p3.is_p or p3.is_anti or p3.hp <= 0: continue
                        if (p3.x - p1.x)**2 + (p3.y - p1.y)**2 < 2025:
                            if (p1.charge + p2.charge + p3.charge) == 3:
                                merged.update([p1, p2, p3])
                                new_p.append(Particle(None, (p1.x+p2.x+p3.x)/3, (p1.y+p2.y+p3.y)/3, True))
                                break
                if p1 in merged: break
                nx, ny = dx / d, dy / d
                kx, ky = p1.dx - p2.dx, p1.dy - p2.dy
                imp = kx * nx + ky * ny
                p1.dx -= imp * nx; p1.dy -= imp * ny; p2.dx += imp * nx; p2.dy += imp * ny
            if dist_sq > 0 and not p1.is_p and not p2.is_p:
                if (p1.charge > 0 and p2.charge < 0) or (p1.charge < 0 and p2.charge > 0):
                    d = math.sqrt(dist_sq); st = d * 0.0004
                    p1.dx += st * (dx/d); p1.dy += st * (dy/d); p2.dx -= st * (dx/d); p2.dy -= st * (dy/d)
    for p in particles:
        if p.hp <= 0 and p not in merged and p not in annihilated and not p.is_p:
            if len(particles) < 30: 
                rand_type = random.choice(list(DB.keys()))
                p_mat = Particle(rand_type, x=p.x - 20, y=p.y, is_anti=False)
                p_anti = Particle(rand_type, x=p.x + 20, y=p.y, is_anti=True)
                angle = random.uniform(0, 2 * math.pi)
                force = 4.0
                p_mat.dx, p_mat.dy = math.cos(angle) * force, math.sin(angle) * force
                p_anti.dx, p_anti.dy = -math.cos(angle) * force, -math.sin(angle) * force
                new_p.extend([p_mat, p_anti])
    particles = [p for p in particles if p.hp > 0 and p not in merged and p not in annihilated]
    particles.extend(new_p)
    for p in particles: p.update(); p.draw()
    for cx, cy in [(45, 45), (W - 65, 45), (45, H - 150), (W - 65, H - 150)]:
        pygame.draw.circle(screen, (60, 65, 75), (cx, cy), 45)
        pygame.draw.circle(screen, (0, 190, 255), (cx, cy), 15)
    info_str = f"FPS: {int(clock.get_fps())} | Объектов: {len(particles)} | Время: {(pygame.time.get_ticks()-start_ticks)/1000.0:.1f}c"
    screen.blit(font.render(info_str, True, (255, 255, 255)), (20, 15))
    pygame.display.flip()
    clock.tick(60)
