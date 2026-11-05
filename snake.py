"""终端贪吃蛇 —— 只用 Python 标准库，Windows/macOS/Linux 均可运行。

玩法：WASD 或方向键移动，吃到 * 加 1 分，撞墙或撞到自己就结束。
按 R 重开一局，按 Q 退出。
"""

import os
import random
import sys
import time

W, H = 20, 12          # 场地宽高（格）
TICK = 0.15            # 每步秒数，越小越快

try:                   # 保证中文在 Windows 终端正常显示
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

if os.name == "nt":
    import msvcrt

    def get_key():
        """非阻塞读取一个按键，没有按键返回 None。"""
        if not msvcrt.kbhit():
            return None
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):        # 方向键前缀
            ch = msvcrt.getch()
            return {b"H": "w", b"P": "s", b"K": "a", b"M": "d"}.get(ch)
        return ch.decode(errors="ignore").lower()

else:
    import select
    import termios
    import tty

    def get_key():
        if not select.select([sys.stdin], [], [], 0)[0]:
            return None
        ch = sys.stdin.read(1)
        if ch == "\x1b":                    # ESC 序列（方向键）
            seq = sys.stdin.read(2)
            return {"A": "w", "B": "s", "C": "d", "D": "a"}.get(seq[-1])
        return ch.lower()


def draw(snake, food, score, over):
    body = set(snake)
    lines = [f"  分数: {score}    长度: {len(snake)}"]
    lines.append("  +" + "-" * W + "+")
    for y in range(H):
        row = "".join(
            "#" if (x, y) in body else "*" if (x, y) == food else " "
            for x in range(W)
        )
        lines.append("  |" + row + "|")
    lines.append("  +" + "-" * W + "+")
    if over:
        lines.append("  游戏结束！按 R 重开，按 Q 退出。")
    else:
        lines.append("  WASD/方向键移动，Q 退出。")
    sys.stdout.write("\x1b[H" + "\n".join(lines) + "\n")
    sys.stdout.flush()


def new_food(snake):
    """在空格子里随机放一个食物；满屏时返回 None。"""
    empty = [(x, y) for x in range(W) for y in range(H) if (x, y) not in snake]
    return random.choice(empty) if empty else None


def step(snake, direction, food, w=W, h=H):
    """走一步。撞墙或撞到自己返回 (None, food, 0) 表示结束。"""
    dx, dy = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}[direction]
    head = (snake[0][0] + dx, snake[0][1] + dy)
    eating = head == food

    # 不吃食物时尾巴会腾出来，所以撞到"最后一格尾巴"不算撞自己
    body = list(snake) if eating else snake[:-1]
    if not (0 <= head[0] < w and 0 <= head[1] < h) or head in body:
        return None, food, 0

    body = [head] + list(snake)
    if eating:
        return body, new_food(body), 1
    return body[:-1], food, 0


def main():
    saved = None
    if os.name != "nt":
        saved = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
    sys.stdout.write("\x1b[2J\x1b[?25l")       # 清屏 + 隐藏光标

    try:
        while True:
            # ---- 初始化一局 ----
            snake = [(W // 2, H // 2)]
            direction = "d"
            score = 0
            food = new_food(snake)
            over = False
            last = time.time()

            draw(snake, food, score, over)

            # ---- 一局的主循环 ----
            while True:
                key = get_key()
                if key == "q":
                    return
                if over:
                    if key == "r":
                        break
                    time.sleep(0.02)
                    continue
                if key in ("w", "a", "s", "d"):
                    opposite = {"w": "s", "s": "w", "a": "d", "d": "a"}
                    if key != opposite[direction]:
                        direction = key

                if time.time() - last < TICK:
                    time.sleep(0.01)
                    continue
                last = time.time()

                nxt, food, gained = step(snake, direction, food)
                if nxt is None:
                    over = True
                else:
                    snake, score = nxt, score + gained
                draw(snake, food, score, over)
    finally:
        sys.stdout.write("\x1b[?25h\n")        # 恢复光标
        sys.stdout.flush()
        if saved is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved)


if __name__ == "__main__":
    main()
