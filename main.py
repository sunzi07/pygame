import pygame, sys, os, math, random, time, json, hashlib
from pygame.locals import *

# 현재 파일의 디렉토리로 작업 경로 설정
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Pygame 초기화 및 창 설정
pygame.init()
pygame.display.set_caption("Pong")
screen = pygame.display.set_mode((1200, 700))
clock = pygame.time.Clock()

# 공 이미지 로드 및 크기 확인
try:
    ball_image = pygame.image.load("image/ball.png").convert_alpha()
    ball_size = ball_image.get_size()
except FileNotFoundError as e:
    print(f"이미지 파일을 찾을 수 없습니다: {e}")
    print("image 폴더에 ball.png 파일이 있는지 확인하세요.")
    sys.exit(1)

# 점수 및 게임 상태 변수
rscore = 0  # 오른쪽 플레이어 점수
lscore = 0  # 왼쪽 플레이어 점수
vs_ai = False  # AI 대전 여부
nickname = ""  # 플레이어 닉네임

# 폰트 설정
font = pygame.font.SysFont("malgungothic", 32)  # 기본 텍스트
font2 = pygame.font.SysFont("malgungothic", 50)  # 큰 텍스트
font3 = pygame.font.SysFont("malgungothic", 24)  # 중간 텍스트
font_body = pygame.font.SysFont("malgungothic", 20)  # 본문 텍스트
font4 = pygame.font.SysFont("malgungothic", 30)  # 스킬 표시용
font_small = pygame.font.SysFont("malgungothic", 18)  # 작은 텍스트
font_menu = pygame.font.SysFont("malgungothic", 40)  # 메뉴 텍스트
font_countdown = pygame.font.SysFont("malgungothic", 100)  # 카운트다운 텍스트
font_restart = pygame.font.SysFont("malgungothic", 20)  # 재시작 안내 텍스트

# 게임 시작 시간
match_start = time.time()

# 데이터 파일 경로
USER_FILE = "users.json"  # 사용자 정보 파일
SCORE_FILE = "scores.json"  # 최고 점수 파일

# 사용자 데이터 로드
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# 사용자 데이터 저장
def save_user(nickname, password):
    users = load_users()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[nickname] = {"password": hashed_password}
    with open(USER_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# 최고 점수 로드
def load_high_scores():
    try:
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# 최고 점수 저장
def save_high_score(nickname, score):
    high_scores = load_high_scores()
    high_scores[nickname] = max(high_scores.get(nickname, 0), score)
    with open(SCORE_FILE, "w") as f:
        json.dump(high_scores, f, ensure_ascii=False, indent=4)

# 회원가입 화면
def signup_screen():
    base_input_boxes = [
        pygame.Rect(500, 300, 200, 40),  # 닉네임 입력 상자
        pygame.Rect(500, 360, 200, 40)   # 비밀번호 입력 상자
    ]
    inputs = ["", ""]
    labels = ["닉네임:", "비밀번호:"]
    active_box = 0
    error_message = ""
    while True:
        input_boxes = base_input_boxes.copy()
        screen.fill((0, 0, 0))
        prompt_text = font_menu.render("회원가입", True, (255, 255, 255))
        screen.blit(prompt_text, (600 - prompt_text.get_width() / 2, 200))
        instruction_text = font_small.render("Enter로 이동/제출, 오른쪽 방향키로 로그인 화면, 닉네임/비밀번호 최대 10자", True, (255, 255, 255))
        screen.blit(instruction_text, (600 - instruction_text.get_width() / 2, 260))
        
        for i, (box, label) in enumerate(zip(input_boxes, labels)):
            pygame.draw.rect(screen, (255, 255, 255) if i == active_box else (150, 150, 150), box, 2)
            label_text = font.render(label, True, (255, 255, 255))
            screen.blit(label_text, (box.x - label_text.get_width() - 10, box.y + 5))
            text_surface = font.render("*" * len(inputs[i]) if i == 1 else inputs[i], True, (255, 255, 255))
            screen.blit(text_surface, (box.x + 5, box.y + 5))

        if error_message:
            error_text = font_small.render(error_message, True, (255, 0, 0))
            screen.blit(error_text, (600 - error_text.get_width() / 2, 420))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    return None
                elif event.key == K_RETURN:
                    if active_box == len(input_boxes) - 1:
                        active_box = 0
                    else:
                        active_box += 1
                    if all(inputs) and len(inputs[0]) <= 10 and len(inputs[1]) <= 10:
                        users = load_users()
                        if inputs[0] in users:
                            error_message = "이미 존재하는 닉네임입니다!"
                        else:
                            save_user(inputs[0], inputs[1])
                            return inputs[0]
                    elif active_box == 0 and error_message:
                        error_message = ""
                elif event.key == K_BACKSPACE:
                    inputs[active_box] = inputs[active_box][:-1]
                elif len(inputs[active_box]) < 10:
                    if event.unicode:
                        inputs[active_box] += event.unicode

# 로그인 화면
def login_screen():
    base_input_boxes = [
        pygame.Rect(500, 330, 200, 40),  # 닉네임 입력 상자
        pygame.Rect(500, 390, 200, 40)   # 비밀번호 입력 상자
    ]
    inputs = ["", ""]
    labels = ["닉네임:", "비밀번호:"]
    active_box = 0
    error_message = ""
    while True:
        input_boxes = base_input_boxes.copy()
        screen.fill((0, 0, 0))
        prompt_text = font_menu.render("로그인", True, (255, 255, 255))
        screen.blit(prompt_text, (600 - prompt_text.get_width() / 2, 230))
        instruction_text = font_small.render("Enter로 이동/제출, 오른쪽 방향키로 회원가입 화면, 닉네임/비밀번호 최대 10자", True, (255, 255, 255))
        screen.blit(instruction_text, (600 - instruction_text.get_width() / 2, 290))

        for i, (box, label) in enumerate(zip(input_boxes, labels)):
            pygame.draw.rect(screen, (255, 255, 255) if i == active_box else (150, 150, 150), box, 2)
            label_text = font.render(label, True, (255, 255, 255))
            screen.blit(label_text, (box.x - label_text.get_width() - 10, box.y + 5))
            text_surface = font.render("*" * len(inputs[i]) if i == 1 else inputs[i], True, (255, 255, 255))
            screen.blit(text_surface, (box.x + 5, box.y + 5))

        if error_message:
            error_text = font_small.render(error_message, True, (255, 0, 0))
            screen.blit(error_text, (600 - error_text.get_width() / 2, 450))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    result = signup_screen()
                    if result:
                        return result
                elif event.key == K_RETURN:
                    if active_box == len(input_boxes) - 1:
                        active_box = 0
                    else:
                        active_box += 1
                    if all(inputs):
                        users = load_users()
                        hashed_password = hashlib.sha256(inputs[1].encode()).hexdigest()
                        if inputs[0] in users and users[inputs[0]]["password"] == hashed_password:
                            return inputs[0]
                        else:
                            error_message = "닉네임 또는 비밀번호가 잘못되었습니다."
                    elif active_box == 0 and error_message:
                        error_message = ""
                elif event.key == K_BACKSPACE:
                    inputs[active_box] = inputs[active_box][:-1]
                elif len(inputs[active_box]) < 10:
                    if event.unicode:
                        inputs[active_box] += event.unicode

# 초기 인증
def authenticate():
    return login_screen()

# 난이도 설정
difficulty = None
difficulty_multipliers = {"쉬움": 1.5, "보통": 1.0, "어려움": 0.3}  # 스킬 쿨다운 배수
ai_speed_multipliers = {"쉬움": 0.6, "보통": 1.2, "어려움": 1.8}  # AI 이동 속도 배수
ai_accuracy_multipliers = {"쉬움": 0.4, "보통": 0.8, "어려움": 1.2}  # AI 정확도 배수
skill_activation_prob = {"쉬움": 0.005, "보통": 0.01, "어려움": 0.015}  # 스킬 발동 확률 (사용 안 함)

# 게임 방법 화면 상태 변수
show_instructions = False
instruction_page = 1

# 공 증가 관련 변수
ball_split_times = []
ball_split_count = 0
hide_ball_split_text = False
last_split_time = 0

# 게임 방법 텍스트 (수정됨)
friends_text = (
    "친구끼리 하는 경우\n"
    "왼쪽 사람: Q키와 W키로 위\n아래 이동, D키로 공을 튕긴다.\n스킬: 1(공 속도 증가),\n2(패들 확장), 3(상대 속도 저하)\n\n"
    "오른쪽 사람: I키와 O키로\n위 아래 이동, J키로 공을 튕긴다.\n스킬: 8(공 속도 증가),\n9(패들 확장), 0(상대 속도 저하)\n\n"
    "공 증가: 게임 중 랜덤으로 발생"
)

ai_text = (
    "AI와 하는 경우\n"
    "왼쪽 플레이어: Q키와 W키로\n위 아래 이동, D키로 공을 튕긴다.\n스킬: 1(공 속도 증가),\n2(패들 확장), 3(상대 속도 저하)\n\n"
    "공 증가: 게임 중 랜덤으로 발생"
)

restart_text = "재시작 키: F"

# 게임 방법 화면 표시 함수 (수정됨)
def draw_instructions():
    pygame.draw.rect(screen, (255, 255, 255), (200, 100, 800, 500))  # 배경 사각형
    pygame.draw.rect(screen, (0, 0, 0), (200, 100, 800, 500), 3)  # 테두리
    pygame.draw.line(screen, (0, 0, 0), (600, 100), (600, 600), 2)  # 구분선

    if instruction_page == 1:
        lines = friends_text.split('\n')
        y_offset = 120
        for i, line in enumerate(lines):
            if line.strip():
                if i == 0:
                    text = font3.render(line, True, (0, 0, 0))
                    x = 200 + (400 - text.get_width()) / 2
                else:
                    text = font_body.render(line, True, (0, 0, 0))
                    x = 220
                screen.blit(text, (x, y_offset))
                y_offset += 30 if i > 0 else 40
            else:
                y_offset += 15

        lines = ai_text.split('\n')
        y_offset = 120
        for i, line in enumerate(lines):
            if line.strip():
                if i == 0:
                    text = font3.render(line, True, (0, 0, 0))
                    x = 600 + (400 - text.get_width()) / 2
                else:
                    text = font_body.render(line, True, (0, 0, 0))
                    x = 620
                screen.blit(text, (x, y_offset))
                y_offset += 30 if i > 0 else 40
            else:
                y_offset += 15

        restart = font_restart.render(restart_text, True, (0, 0, 0))
        restart_x = 620
        restart_y = 450
        screen.blit(restart, (restart_x, restart_y))

        next_text = font_small.render("넘기기(n)", True, (0, 0, 0))
        page_text = font_small.render("페이지(1/1)", True, (0, 0, 0))
        screen.blit(next_text, (900 - next_text.get_width(), 510))
        screen.blit(page_text, (900 - page_text.get_width(), 530))

    back_text = font_small.render("메인화면으로 돌아가기(K)", True, (0, 0, 0))
    screen.blit(back_text, (210, 570))

# 난이도 선택
def select_difficulty():
    global difficulty, show_instructions, instruction_page
    while difficulty is None:
        screen.fill((0, 0, 0))
        if show_instructions:
            draw_instructions()
        else:
            txt1 = font_menu.render("난이도 선택", True, (255, 255, 255))
            txt2 = font_menu.render("1: 쉬움", True, (255, 255, 255))
            txt3 = font_menu.render("2: 보통", True, (255, 255, 255))
            txt4 = font_menu.render("3: 어려움", True, (255, 255, 255))
            screen.blit(txt1, (600 - txt1.get_width() / 2, 200))
            screen.blit(txt2, (600 - txt2.get_width() / 2, 300))
            screen.blit(txt3, (600 - txt3.get_width() / 2, 350))
            screen.blit(txt4, (600 - txt4.get_width() / 2, 400))
            instructions_prompt = font_small.render("게임 방법(K)", True, (255, 255, 255))
            screen.blit(instructions_prompt, (1200 - instructions_prompt.get_width() - 10, 700 - instructions_prompt.get_height() - 10))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_k:
                    show_instructions = not show_instructions
                    instruction_page = 1
                elif event.key == K_n and show_instructions:
                    instruction_page = 1  # 페이지가 하나뿐이므로 변경 없음
                elif not show_instructions:
                    if event.key == K_1:
                        difficulty = "쉬움"
                    elif event.key == K_2:
                        difficulty = "보통"
                    elif event.key == K_3:
                        difficulty = "어려움"

# 플레이어 선택
def select_opponent():
    global vs_ai, show_instructions, instruction_page
    opponent = None
    while opponent is None:
        screen.fill((0, 0, 0))
        if show_instructions:
            draw_instructions()
        else:
            txt1 = font_menu.render("상대 선택", True, (255, 255, 255))
            txt2 = font_menu.render("1: arkadaş와 함께", True, (255, 255, 255))
            txt3 = font_menu.render("2: AI와 함께", True, (255, 255, 255))
            screen.blit(txt1, (600 - txt1.get_width() / 2, 200))
            screen.blit(txt2, (600 - txt2.get_width() / 2, 300))
            screen.blit(txt3, (600 - txt3.get_width() / 2, 350))
            instructions_prompt = font_small.render("게임 방법(K)", True, (255, 255, 255))
            screen.blit(instructions_prompt, (1200 - instructions_prompt.get_width() - 10, 700 - instructions_prompt.get_height() - 10))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_k:
                    show_instructions = not show_instructions
                    instruction_page = 1
                elif event.key == K_n and show_instructions:
                    instruction_page = 1  # 페이지가 하나뿐이므로 변경 없음
                elif not show_instructions:
                    if event.key == K_1:
                        opponent = "친구"
                        vs_ai = False
                    elif event.key == K_2:
                        opponent = "AI"
                        vs_ai = True

# 게임 시작
def start_game():
    global match_start, show_instructions, ball_split_times, ball_split_count, hide_ball_split_text, last_split_time, instruction_page
    show_instructions = False
    instruction_page = 1
    ball_split_count = 0
    hide_ball_split_text = False
    last_split_time = 0
    select_difficulty()
    select_opponent()
    for countdown in [3, 2, 1]:
        screen.fill((0, 0, 0))
        txt = font_countdown.render(str(countdown), True, (255, 255, 255))
        screen.blit(txt, (600 - txt.get_width() / 2, 350 - txt.get_height() / 2))
        pygame.display.update()
        pygame.time.wait(1000)
    match_start = time.time()
    possible_times = sorted(list(set([t for t in range(3, 31, 3)] + [t for t in range(5, 31, 5)])))
    possible_times = [t for t in possible_times if t < 47]
    ball_split_times = sorted(random.sample(possible_times, 3))

# 패들 클래스
class Bat:
    def __init__(self, ctrls, x, side):
        self.ctrls = ctrls  # 컨트롤 키
        self.x = x  # x 위치
        self.y = 310  # y 위치
        self.side = side  # -1: 왼쪽, 1: 오른쪽
        self.lastbop = 0  # 마지막 타격 시간
        self.paddle_length = 100  # 패들 길이
        self.move_speed = 12  # 이동 속도
        self.specials = {
            "speed_burst": {"cooldown": 0, "duration": 0},  # 공 속도 증가
            "paddle_extend": {"cooldown": 0, "duration": 0},  # 패들 확장
            "slow_motion": {"cooldown": 0, "duration": 0}  # 상대 속도 저하
        }

    def move(self):
        # 플레이어 이동 (AI 모드에서는 왼쪽만 플레이어)
        if not vs_ai or self.side == -1:
            if pressed_keys[self.ctrls[0]] and self.y > 0:
                self.y -= self.move_speed
            if pressed_keys[self.ctrls[1]] and self.y + self.paddle_length < 700:
                self.y += self.move_speed

    def ai_move(self, ball_y):
        # AI 이동 로직
        if vs_ai and self.side == 1:
            target_y = ball_y - self.paddle_length / 2 * ai_accuracy_multipliers[difficulty]
            speed = self.move_speed * ai_speed_multipliers[difficulty]
            lerp_factor = 0.1
            self.y = self.y + (target_y - self.y) * lerp_factor
            if self.y < 0:
                self.y = 0
            elif self.y + self.paddle_length > 700:
                self.y = 700 - self.paddle_length

    def draw(self):
        # 패들 그리기, 타격 시 살짝 이동 효과
        offset = -self.side * (time.time() < self.lastbop + 0.05) * 12
        pygame.draw.line(screen, (255, 255, 255), (self.x + offset, self.y),
                         (self.x + offset, self.y + self.paddle_length), 6)

    def bop(self):
        # 공 타격 처리
        if time.time() > self.lastbop + 0.3:
            self.lastbop = time.time()

    def special(self, special_type, balls, opponent):
        # 스킬 발동
        current_time = time.time()
        base_cooldowns = {"speed_burst": 10, "paddle_extend": 15, "slow_motion": 15}
        cooldown = base_cooldowns[special_type] * difficulty_multipliers[difficulty]
        if special_type == "speed_burst" and current_time > self.specials["speed_burst"]["cooldown"] + cooldown:
            print(f"Bat {self.side} triggered speed_burst")
            speed_multiplier = 1.8 if difficulty == "어려움" else 1.5
            for ball in balls:
                if not ball.speed_boost:
                    ball.speed *= speed_multiplier
                    ball.speed_boost = True
                    ball.speed_boost_end = current_time + 3
            self.specials["speed_burst"]["cooldown"] = current_time
        elif special_type == "paddle_extend" and current_time > self.specials["paddle_extend"]["cooldown"] + cooldown:
            print(f"Bat {self.side} triggered paddle_extend")
            self.paddle_length = 150
            self.specials["paddle_extend"]["duration"] = current_time + 5
            self.specials["paddle_extend"]["cooldown"] = current_time
        elif special_type == "slow_motion" and current_time > self.specials["slow_motion"]["cooldown"] + cooldown:
            print(f"Bat {self.side} triggered slow_motion")
            opponent.move_speed = 6
            self.specials["slow_motion"]["duration"] = current_time + 4
            self.specials["slow_motion"]["cooldown"] = current_time

    def update_specials(self, opponent):
        # 스킬 지속 시간 관리
        current_time = time.time()
        if self.specials["paddle_extend"]["duration"] and current_time > self.specials["paddle_extend"]["duration"]:
            self.paddle_length = 100
            self.specials["paddle_extend"]["duration"] = 0
        if self.specials["slow_motion"]["duration"] and current_time > self.specials["slow_motion"]["duration"]:
            opponent.move_speed = 12
            self.specials["slow_motion"]["duration"] = 0

# 공 클래스
class Ball:
    def __init__(self):
        self.d = (math.pi / 3) * random.random() + (math.pi / 3) + math.pi * random.randint(0, 1)  # 초기 방향
        self.speed = 16  # 초기 속도
        self.dx = math.sin(self.d) * self.speed  # x 방향 속도
        self.dy = math.cos(self.d) * self.speed  # y 방향 속도
        self.x = 575  # 초기 x 위치
        self.y = 325  # 초기 y 위치
        self.speed_boost = False  # 속도 증가 상태
        self.speed_boost_end = 0  # 속도 증가 종료 시간
        self.image = ball_image  # 공 이미지

    def move(self):
        # 공 이동
        self.x += self.dx
        self.y += self.dy
        if self.speed_boost and time.time() > self.speed_boost_end:
            speed_multiplier = 1.8 if difficulty == "어려움" else 1.5
            self.speed /= speed_multiplier
            self.dx = math.sin(self.d) * self.speed
            self.dy = math.cos(self.d) * self.speed
            self.speed_boost = False

    def draw(self):
        # 공 그리기
        screen.blit(self.image, (int(self.x), int(self.y)))

    def bounce(self):
        # 벽 충돌 처리
        if (self.y <= 0 and self.dy < 0) or (self.y >= 650 and self.dy > 0):
            self.dy *= -1
            self.d = math.atan2(self.dx, self.dy)
        
        # 패들 충돌 처리
        for bat in bats:
            paddle_rect = pygame.Rect(bat.x - 10 if bat.side == -1 else bat.x, bat.y, 16, bat.paddle_length)
            ball_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
            if paddle_rect.colliderect(ball_rect) and abs(self.dx) / self.dx == bat.side:
                self.d += random.random() * math.pi / 4 - math.pi / 8
                if (0 < self.d < math.pi / 6) or (math.pi * 5 / 6 < self.d < math.pi):
                    self.d = ((math.pi / 3) * random.random() + (math.pi / 3)) + math.pi
                elif (math.pi < self.d < math.pi * 7 / 6) or (math.pi * 11 / 6 < self.d < math.pi * 2):
                    self.d = ((math.pi / 3) * random.random() + (math.pi / 3))
                self.d *= -1
                self.d %= math.pi * 2
                max_speed = 30 if difficulty == "어려움" else 25
                increase_rate = 1.08 if difficulty == "어려움" else 1.05
                if time.time() < bat.lastbop + 0.05 and self.speed < max_speed and not self.speed_boost:
                    self.speed *= increase_rate
                self.dx = math.sin(self.d) * self.speed
                self.dy = math.cos(self.d) * self.speed

# 공 증가 함수
def trigger_ball_split(balls):
    if balls:
        new_ball = Ball()
        new_ball.x = balls[0].x
        new_ball.y = balls[0].y
        new_ball.d = balls[0].d + math.pi / 4
        new_ball.dx = math.sin(new_ball.d) * new_ball.speed
        new_ball.dy = math.cos(new_ball.d) * new_ball.speed
        balls.append(new_ball)

# 초기 객체 생성
balls = [Ball()]
bats = [Bat([K_q, K_w], 10, -1), Bat([K_i, K_o], 1184, 1)]

# 사용자 인증
nickname = authenticate()

# 게임 시작
start_game()

# 게임 루프
while 1:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_d:  # 왼쪽 플레이어: D 키로 튕김
                bats[0].bop()
            if event.key == K_j and not vs_ai:  # 오른쪽 플레이어: J 키로 튕김
                bats[1].bop()
            # 왼쪽 플레이어 스킬
            if event.key == K_1:
                bats[0].special("speed_burst", balls, bats[1])
            elif event.key == K_2:
                bats[0].special("paddle_extend", balls, bats[1])
            elif event.key == K_3:
                bats[0].special("slow_motion", balls, bats[1])
            # 오른쪽 플레이어 스킬 (AI 모드에서는 무시)
            if not vs_ai:
                if event.key == K_8:
                    bats[1].special("speed_burst", balls, bats[0])
                elif event.key == K_9:
                    bats[1].special("paddle_extend", balls, bats[0])
                elif event.key == K_0:
                    bats[1].special("slow_motion", balls, bats[0])

    pressed_keys = pygame.key.get_pressed()

    screen.fill((0, 0, 0))
    pygame.draw.line(screen, (255, 255, 255), (screen.get_width() / 2, 0), 
                     (screen.get_width() / 2, screen.get_height()), 3)  # 중앙선
    pygame.draw.circle(screen, (255, 255, 255), 
                       (int(screen.get_width() / 2), int(screen.get_height() / 2)), 60, 3)  # 중앙 원
    
    # 타이머 표시
    remaining_time = int(60 - (time.time() - match_start))
    txt = font.render(str(remaining_time), True, (255, 255, 255), (0, 0, 0))
    screen.blit(txt, (screen.get_width() / 2 - txt.get_width() / 2, 20))

    # 공 증가 텍스트
    if ball_split_count < len(ball_split_times) and not hide_ball_split_text:
        elapsed_time = time.time() - match_start
        time_until_split = max(0, int(ball_split_times[ball_split_count] - elapsed_time))
        ball_split_text = font.render("공 증가:", True, (255, 255, 255), (0, 0, 0))
        ball_split_text_x = screen.get_width() / 2 - ball_split_text.get_width() / 2
        ball_split_text_y = 60
        screen.blit(ball_split_text, (ball_split_text_x, ball_split_text_y))

        ball_split_timer_text = font_small.render(f"{time_until_split}초 후", True, (255, 255, 255), (0, 0, 0))
        ball_split_timer_text_x = screen.get_width() / 2 - ball_split_timer_text.get_width() / 2
        ball_split_timer_text_y = ball_split_text_y + ball_split_text.get_height() + 5
        screen.blit(ball_split_timer_text, (ball_split_timer_text_x, ball_split_timer_text_y))

    # 공 증가 실행
    if ball_split_count < len(ball_split_times) and (time.time() - match_start >= ball_split_times[ball_split_count]):
        trigger_ball_split(balls)
        ball_split_count += 1
        hide_ball_split_text = True
        last_split_time = time.time()

    # 텍스트 숨김 해제
    if hide_ball_split_text and ball_split_count < len(ball_split_times):
        if time.time() - last_split_time >= 1:
            hide_ball_split_text = False

    for bat in bats:
        bat.move()
        if vs_ai and bat.side == 1 and balls:
            bat.ai_move(balls[0].y)
        bat.update_specials(bats[1] if bat == bats[0] else bats[0])
        bat.draw()

    i = 0
    while i < len(balls):
        ball = balls[i]
        ball.move()
        ball.bounce()
        ball.draw()
        if ball.x < -50:
            balls.pop(i)
            rscore += 1
        elif ball.x > 1200:
            balls.pop(i)
            lscore += 1
        else:
            i += 1
        if not balls:
            balls.append(Ball())

    if time.time() - match_start <= 60:
        txt = font.render(f"점수: {lscore}", True, (255, 255, 255))
        score_height = txt.get_height()
        screen.blit(txt, (300 - txt.get_width() / 2, 20))
        
        txt = font.render(f"점수: {rscore}", True, (255, 255, 255))
        screen.blit(txt, (900 - txt.get_width() / 2, 20))

        special_names = {
            "speed_burst": "속도 증가",
            "paddle_extend": "패들 확장",
            "slow_motion": "상대 속도 저하"
        }
        base_cooldowns = {"speed_burst": 10, "paddle_extend": 15, "slow_motion": 15}
        for i, bat in enumerate(bats):
            y_offset = 20 + score_height + 10
            panel_center_x = 300 if i == 0 else 900
            for special, data in bat.specials.items():
                if special in special_names:
                    cooldown_end = data["cooldown"] + base_cooldowns[special] * difficulty_multipliers[difficulty]
                    remaining_time = max(0, int(cooldown_end - time.time()))
                    skill_text = special_names[special]
                    cooldown_time = f"{remaining_time}초"
                    txt_skill = font4.render(skill_text, True, (255, 255, 255))
                    txt_cooldown_time = font_small.render(cooldown_time, True, (255, 255, 255))
                    total_width = txt_skill.get_width() + txt_cooldown_time.get_width() + 5
                    screen.blit(txt_skill, (panel_center_x - total_width / 2, y_offset))
                    screen.blit(txt_cooldown_time, (panel_center_x - total_width / 2 + txt_skill.get_width() + 5, y_offset + 10))
                    y_offset += 40

    if time.time() - match_start > 60:
        player_score = lscore if vs_ai else max(lscore, rscore)
        save_high_score(nickname, player_score)
        high_scores = load_high_scores()
        high_score = high_scores.get(nickname, 0)

        txt = font2.render("점수", True, (255, 0, 255))
        score_title_height = txt.get_height()
        screen.blit(txt, (screen.get_width() / 4 - txt.get_width() / 2, screen.get_height() / 4))
        screen.blit(txt, (screen.get_width() * 3 / 4 - txt.get_width() / 2, screen.get_height() / 4))
        
        txt = font3.render(str(lscore), True, (255, 255, 255))
        screen.blit(txt, (screen.get_width() / 4 - txt.get_width() / 2, screen.get_height() / 4 + score_title_height + 10))
        
        txt = font3.render(str(rscore), True, (255, 255, 255))
        screen.blit(txt, (screen.get_width() * 3 / 4 - txt.get_width() / 2, screen.get_height() / 4 + score_title_height + 10))
        
        txt = font3.render(f"{nickname}의 최고 점수: {high_score}", True, (255, 255, 0), (0, 0, 0))
        screen.blit(txt, (screen.get_width() / 2 - txt.get_width() / 2, screen.get_height() / 4 + score_title_height + 50))
        
        txt = font4.render("재시작: F", True, (255, 255, 255), (0, 0, 0))
        screen.blit(txt, (screen.get_width() / 2 - txt.get_width() / 2, screen.get_height() / 2 - txt.get_height() / 2))

        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_f]:
                lscore = 0
                rscore = 0
                bats[0].y = 250
                bats[1].y = 250
                balls = [Ball()]
                for bat in bats:
                    bat.paddle_length = 100
                    bat.move_speed = 12
                    for special in bat.specials.values():
                        special["cooldown"] = 0
                        special["duration"] = 0
                nickname = authenticate()
                start_game()
                break
            pygame.display.update()

    pygame.display.update()