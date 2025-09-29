import pygame
import sys
from typing import Dict, Optional, List, Tuple

pygame.init()


WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS


WHITE = (245, 245, 220)
BLACK = (139, 69, 19)
BLUE = (0, 0, 255)


class Piece:
    def __init__(self, name: str):
        self.name: str = name
        self.color: str = name[0]
        self.kind: str = name[1]

    def is_valid_move(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        board: List[List[Optional[str]]],
    ) -> bool:
        sx, sy = start
        ex, ey = end
        dx, dy = ex - sx, ey - sy
        target = board[ex][ey]

        if target and target[0] == self.color:
            return False

        if self.kind == "p":
            direction = -1 if self.color == "w" else 1
            start_row = 6 if self.color == "w" else 1
            if sy == ey and not target:
                if ex == sx + direction:
                    return True
                if (
                    sx == start_row
                    and ex == sx + 2 * direction
                    and not board[sx + direction][sy]
                ):
                    return True
            if (
                abs(ey - sy) == 1
                and ex == sx + direction
                and target
                and target[0] != self.color
            ):
                return True

        elif self.kind == "r":
            if dx == 0 or dy == 0:
                return self.clear_path(start, end, board)

        elif self.kind == "b":
            if abs(dx) == abs(dy):
                return self.clear_path(start, end, board)

        elif self.kind == "q":
            if dx == 0 or dy == 0 or abs(dx) == abs(dy):
                return self.clear_path(start, end, board)

        elif self.kind == "n":
            return (abs(dx), abs(dy)) in [(2, 1), (1, 2)]

        elif self.kind == "k":
            return max(abs(dx), abs(dy)) == 1

        return False

    def clear_path(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        board: List[List[Optional[str]]],
    ) -> bool:
        sx, sy = start
        ex, ey = end
        dx = (ex - sx) // max(1, abs(ex - sx)) if ex != sx else 0
        dy = (ey - sy) // max(1, abs(ey - sy)) if ey != sy else 0
        x, y = sx + dx, sy + dy
        while (x, y) != (ex, ey):
            if board[x][y]:
                return False
            x += dx
            y += dy
        return True


def load_images() -> Dict[str, pygame.Surface]:
    pieces = ["wp", "bp", "wr", "br", "wn", "bn", "wb", "bb", "wq", "bq", "wk", "bk"]
    images: Dict[str, pygame.Surface] = {}
    for piece in pieces:
        images[piece] = pygame.transform.scale(
            pygame.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE)
        )
    return images


def draw_board(win: pygame.Surface):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(
                win,
                color,
                (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )


def highlight_square(win: pygame.Surface, selected: Optional[Tuple[int, int]]):
    if selected:
        row, col = selected
        pygame.draw.rect(
            win,
            BLUE,
            (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            3,
        )


def draw_pieces(
    win: pygame.Surface,
    board: List[List[Optional[str]]],
    images: Dict[str, pygame.Surface],
) -> None:

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                win.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))


def create_board() -> List[List[Optional[str]]]:
    board: List[List[Optional[str]]] = [[None for _ in range(8)] for _ in range(8)]
    for i in range(8):
        board[1][i] = "bp"
        board[6][i] = "wp"
    board[0] = ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"]
    board[7] = ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
    return board


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Diddy Chess GUI")
    board = create_board()
    images = load_images()
    turn = "w"  # 'w' for white, 'b' for black
    selected: Optional[tuple[int, int]] = None

    while True:
        draw_board(win)
        draw_pieces(win, board, images)
        highlight_square(win, selected)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
                piece = board[row][col]
                if selected:
                    piece_name = board[selected[0]][selected[1]]
                    if piece_name is not None:
                        piece = Piece(piece_name)
                        if piece.color == turn and piece.is_valid_move(
                            selected, (row, col), board
                        ):
                            board[row][col] = piece_name
                            board[selected[0]][selected[1]] = None
                            turn = "b" if turn == "w" else "w"
                        selected = None

                elif piece is not None and piece[0] == turn:
                    selected = (row, col)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
