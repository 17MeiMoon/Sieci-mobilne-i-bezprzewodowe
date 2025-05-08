import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox
from collections import deque
from matplotlib.widgets import Button

manual_blockades_set = set()


def click_handler(event, ax, L, fig):
    if event.inaxes != ax:
        return
    x, y = round(event.xdata), round(event.ydata)
    if (x, y) not in click_handler.points:
        click_handler.points.append((x, y))
    if len(click_handler.points) == 2:
        a, b = click_handler.points
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1:
            edge = frozenset([a, b])
            if edge in manual_blockades_set:
                manual_blockades_set.remove(edge)
                redraw_blockades(ax, L)
                fig.canvas.draw()
            else:
                manual_blockades_set.add(edge)
                ax.plot([a[0], b[0]], [a[1], b[1]], color='red', linewidth=2)
                fig.canvas.draw()
        else:
            messagebox.showwarning("Błąd", "Wybierz dwa sąsiadujące węzły!")
        click_handler.points.clear()


def redraw_blockades(ax, L):
    ax.clear()
    ax.set_xlim(-0.5, L + 0.5)
    ax.set_ylim(-0.5, L + 0.5)
    ax.set_aspect('equal')
    for i in range(L + 1):
        ax.axhline(i, color='gray', linewidth=0.5)
        ax.axvline(i, color='gray', linewidth=0.5)
    for edge in manual_blockades_set:
        a, b = list(edge)
        ax.plot([a[0], b[0]], [a[1], b[1]], color='red', linewidth=2)
    ax.set_title("Kliknij dwa węzły by dodać/usunąć blokadę")


def draw_grid_and_get_blockades(L):
    fig, ax = plt.subplots(figsize=(10, 6))
    redraw_blockades(ax, L)
    click_handler.points = []
    fig.canvas.mpl_connect("button_press_event", lambda event: click_handler(event, ax, L, fig))

    # Dodajemy nowy przyciski w rogu okna
    button_ax_reset = fig.add_axes([0.8, 0.01, 0.15, 0.05])  # Reset
    button_reset = Button(button_ax_reset, 'Resetuj blokady', color='lightgray', hovercolor='gray')

    button_ax_finish = fig.add_axes([0.8, 0.07, 0.15, 0.05])  # Zakończ
    button_finish = Button(button_ax_finish, 'Start', color='lightgray', hovercolor='gray')

    def on_finish(event):
        plt.close(fig)  # Zamyka okno

    def on_reset(event):
        global manual_blockades_set
        manual_blockades_set.clear()  # Resetuje blokady
        redraw_blockades(ax, L)
        fig.canvas.draw()

    button_finish.on_clicked(on_finish)
    button_reset.on_clicked(on_reset)

    plt.tight_layout()
    plt.show()


def bfs(start, end, blocked_edges, blocked_nodes, L):
    queue = deque()
    visited = set()
    parent = {}
    queue.append(start)
    visited.add(start)
    while queue:
        current = queue.popleft()
        if current == end:
            break
        x, y = current
        neighbors = []
        if x > 0: neighbors.append((x - 1, y))
        if x < L - 1: neighbors.append((x + 1, y))
        if y > 0: neighbors.append((x, y - 1))
        if y < L - 1: neighbors.append((x, y + 1))

        for neighbor in neighbors:
            edge = frozenset([current, neighbor])
            # Sprawdzamy, czy węzeł lub krawędź są zablokowane
            if neighbor not in visited and neighbor not in blocked_nodes and edge not in blocked_edges:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    path = []
    node = end
    while node != start:
        if node not in parent:
            return None
        path.append(node)
        node = parent[node]
    path.append(start)
    path.reverse()
    return path


def run_simulation(L, p_block, start, end, randomize_points, manual_blockades_enabled):
    if randomize_points:
        start = (np.random.randint(0, L), np.random.randint(0, L))
        end = (np.random.randint(0, L), np.random.randint(0, L))
        while start == end:
            end = (np.random.randint(0, L), np.random.randint(0, L))

    blocked_edges = set(manual_blockades_set)
    blocked_nodes = set()
    # Dodajemy węzły, które są częścią blokad
    for edge in blocked_edges:
        a, b = list(edge)
        blocked_nodes.add(a)
        blocked_nodes.add(b)

    current_position = start
    actual_path = [start]
    event_log = [(0, start, False)]
    time_counter = 1

    while current_position != end:
        path = bfs(current_position, end, blocked_edges, blocked_nodes, L)
        if path is None or len(path) < 2:
            messagebox.showwarning("Brak trasy", "Nie znaleziono możliwej trasy do celu z powodu blokad.")
            return

        next_step = path[1]
        edge = frozenset([current_position, next_step])
        blocked_now = False

        if not manual_blockades_enabled and (edge not in blocked_edges):
            if np.random.rand() < p_block:
                blocked_edges.add(edge)
                blocked_nodes.add(next_step)  # Dodajemy węzeł do zablokowanych
                blocked_nodes.add(current_position)  # Dodajemy węzeł do zablokowanych
                blocked_now = True

        if edge in blocked_edges:
            event_log.append((time_counter, current_position, True))
        else:
            current_position = next_step
            actual_path.append(current_position)
            event_log.append((time_counter, current_position, False))
            time_counter += 1

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(-0.5, L + 0.5)
    ax.set_ylim(-0.5, L + 0.5)
    ax.set_aspect('equal')
    for i in range(L + 1):
        ax.axhline(i, color='gray', linewidth=0.5)
        ax.axvline(i, color='gray', linewidth=0.5)
    for edge in blocked_edges:
        a, b = list(edge)
        ax.plot([a[0], b[0]], [a[1], b[1]], color='red', linewidth=2)
    for i in range(len(actual_path) - 1):
        a = actual_path[i]
        b = actual_path[i + 1]
        ax.plot([a[0], b[0]], [a[1], b[1]], color='blue', linewidth=1.5)
    ax.plot(start[0], start[1], 'go', markersize=10)
    ax.plot(end[0], end[1], 'mo', markersize=10)
    vehicle, = ax.plot([], [], 'ro', markersize=8)
    time_text = ax.text(0.02, 1.02, '', transform=ax.transAxes)

    def init():
        vehicle.set_data([], [])
        time_text.set_text('')
        return vehicle, time_text

    def update(frame):
        if frame < len(actual_path):
            x, y = actual_path[frame]
            vehicle.set_data([x], [y])
            time_text.set_text(f'Czas: {frame}')
        return vehicle, time_text

    ani = FuncAnimation(fig, update, frames=len(actual_path), init_func=init, interval=1000, blit=True)
    plt.tight_layout()

    button_ax_report = fig.add_axes([0.8, 0.07, 0.15, 0.05])
    button_report = Button(button_ax_report, 'Pokaż raport', color='lightgray', hovercolor='gray')

    def show_report(event):
        times = [log[0] for log in event_log]
        positions = [log[1] for log in event_log]
        blocked = [log[2] for log in event_log]

        fig_report, ax_report = plt.subplots(figsize=(8, 4))
        ax_report.plot(times, [pos[0] for pos in positions], label='X', marker='o')
        ax_report.plot(times, [pos[1] for pos in positions], label='Y', marker='s')
        ax_report.set_xlabel("Czas")
        ax_report.set_ylabel("Pozycja")
        ax_report.set_title("Pozycja pojazdu w czasie")
        ax_report.grid(True)
        ax_report.legend()

        for t, was_blocked in zip(times, blocked):
            if was_blocked:
                ax_report.axvline(t, color='red', linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.show()

    button_report.on_clicked(show_report)

    plt.show()


def start_gui():
    def start_sim():
        try:
            L_val = int(entry_L.get())
            p_val = float(entry_p.get())
            randomize = var_random.get()
            manual_blocks = var_manual.get()
            if manual_blocks:
                draw_grid_and_get_blockades(L_val)
            if not randomize:
                sx = int(entry_sx.get())
                sy = int(entry_sy.get())
                ex = int(entry_ex.get())
                ey = int(entry_ey.get())
                start_pos = (sx, sy)
                end_pos = (ex, ey)
            else:
                start_pos = end_pos = None
            run_simulation(L_val, p_val, start_pos, end_pos, randomize, manual_blocks)
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowe dane!")

    root = tk.Tk()
    root.title("Symulator Ruchu Pojazdu")
    tk.Label(root, text="Rozmiar siatki (L):").grid(row=0, column=0, sticky="e")
    entry_L = tk.Entry(root)
    entry_L.insert(0, "10")
    entry_L.grid(row=0, column=1)

    tk.Label(root, text="Prawdopodobieństwo blokady (p):").grid(row=1, column=0, sticky="e")
    entry_p = tk.Entry(root)
    entry_p.insert(0, "0.2")
    entry_p.grid(row=1, column=1)

    var_random = tk.BooleanVar()
    var_random.set(True)
    var_manual = tk.BooleanVar()
    var_manual.set(False)

    def toggle_manual_entries():
        state = tk.NORMAL if not var_random.get() else tk.DISABLED
        for entry in [entry_sx, entry_sy, entry_ex, entry_ey]:
            entry.configure(state=state)

    tk.Checkbutton(root, text="Losowe punkty start i koniec", variable=var_random, command=toggle_manual_entries).grid(
        row=2, columnspan=2)

    tk.Label(root, text="Start x,y:").grid(row=3, column=0, sticky="e")
    entry_sx = tk.Entry(root, width=5)
    entry_sy = tk.Entry(root, width=5)
    entry_sx.insert(0, "0")
    entry_sy.insert(0, "0")
    entry_sx.grid(row=3, column=1, sticky="w")
    entry_sy.grid(row=3, column=1, sticky="e")

    tk.Label(root, text="Koniec x,y:").grid(row=4, column=0, sticky="e")
    entry_ex = tk.Entry(root, width=5)
    entry_ey = tk.Entry(root, width=5)
    entry_ex.insert(0, "9")
    entry_ey.insert(0, "9")
    entry_ex.grid(row=4, column=1, sticky="w")
    entry_ey.grid(row=4, column=1, sticky="e")

    tk.Checkbutton(root, text="Ręczne blokady (klik)", variable=var_manual).grid(row=5, columnspan=2)

    toggle_manual_entries()
    tk.Button(root, text="Start Symulacji", command=start_sim).grid(row=6, columnspan=2, pady=10)
    root.mainloop()


if __name__ == "__main__":
    start_gui()
