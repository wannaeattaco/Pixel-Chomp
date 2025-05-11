"""Statistic Manager class"""
import csv
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd


class StatisticsManager:
    """Handles recording and reporting game statistics"""

    def __init__(self):
        self.player_data = {
            'timestamp': [], 'score': [], 'duration': [],
            'lives_lost': [], 'dots_collected': [],
            'ghosts_eaten': [], 'power_pallets_collected': [],
            'difficulty': []
        }
        self.timestamps = []
        self.fig = None
        self.canvas = None
        self.combo = None
        self.win = None

    def record_timestamp(self, timestamp, pacman):
        """Record timestamp of the game"""
        self.timestamps.append({
            'time': timestamp,
            'score': pacman.score,
            'dots': pacman.dots_collected,
            'ghosts': pacman.ghosts_eaten,
            'lives': pacman.lives
        })

    def record_data(self, pacman, duration, difficulty):
        """Record data of the game"""
        self.player_data['timestamp'].append(datetime.now().isoformat())
        self.player_data['score'].append(pacman.score)
        self.player_data['duration'].append(duration)
        self.player_data['lives_lost'].append(3 - pacman.lives)
        self.player_data['dots_collected'].append(pacman.dots_collected)
        self.player_data['ghosts_eaten'].append(pacman.ghosts_eaten)
        self.player_data['power_pallets_collected'].append(
            pacman.power_pallets_collected)
        self.player_data['difficulty'].append(difficulty)

    def save_to_file(self, filename='game_stats.csv'):
        """Save data to file"""
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.player_data.keys())
            if not file_exists:
                writer.writeheader()
            i = len(self.player_data['timestamp']) - 1
            if i >= 0:
                row = {k: self.player_data[k][i] for k in self.player_data}
                writer.writerow(row)

    def generate_report(self):
        """Generate summary report for the most recent game session"""
        if not self.player_data['score']:
            return ""
        report = "\nGame Performance Report\n" + "=" * 24 + "\n"
        current_difficulty = self.player_data['difficulty'][0] \
        if self.player_data['difficulty'] else None

        high_score = 0
        try:
            df = pd.read_csv('game_stats.csv')
            if current_difficulty:
                df_diff = df[df['difficulty'] == current_difficulty]
                if not df_diff.empty:
                    high_score = int(df_diff['score'].max())
        except Exception:
            high_score = max(self.player_data['score'])

        total_score = self.player_data['score'][-1] if self.player_data['score'] else 0
        total_dots = self.player_data['dots_collected'][-1] if \
        self.player_data['dots_collected'] else 0
        total_ghosts = self.player_data['ghosts_eaten'][-1] if \
        self.player_data['ghosts_eaten'] else 0
        total_pallets = self.player_data['power_pallets_collected'][-1] if \
        self.player_data['power_pallets_collected'] else 0

        report += f"High Score: {high_score}\n"
        report += f"Total Score: {total_score}\n"
        report += f"Total Dots Collected: {total_dots}\n"
        report += f"Total Ghosts Eaten: {total_ghosts}\n"
        report += f"Total Power Pallets: {total_pallets}\n"
        report += f"Difficulty: {current_difficulty.capitalize() if current_difficulty else ''}\n"
        return report

    def plot_text_stats(self, ax, df):
        """Plot text statistics in a table format"""
        difficulties = ['Easy', 'Normal', 'Hard']
        grouped = df.groupby('difficulty').agg({
            'score': ['max', 'mean'],
            'duration': 'mean'
        })
        grouped.columns = ['High Score', 'Average Score', 'Avg Survival Time (s)']
        grouped = grouped.reset_index()
        stats = {row['difficulty'].capitalize(): row for _, row in grouped.iterrows()}

        table_data = []
        headers = ['Difficulty', 'High Score', 'Average Score', 'Avg Survival Time (s)']
        
        for diff in difficulties:
            row = stats.get(diff, None)
            if row is not None:
                table_data.append([
                    diff,
                    f"{int(row['High Score'])}",
                    f"{row['Average Score']:.2f}",
                    f"{row['Avg Survival Time (s)']:.1f}"
                ])
            else:
                table_data.append([diff, "0", "0.00", "0.0"])

        table = ax.table(
            cellText=table_data,
            colLabels=headers,
            loc='center',
            cellLoc='center',
            colWidths=[0.2, 0.25, 0.25, 0.3]
        )

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#404040')
                cell.set_text_props(color='white')
            else:
                cell.set_facecolor('#f0f0f0' if row % 2 == 0 else 'white')

        ax.axis('off')
        ax.set_title('Statistics by Difficulty', pad=20, fontsize=14, weight='bold')

    def plot_dots_by_difficulty(self, ax, df):
        """Plot dots collected by difficulty"""
        data = [df[df['difficulty'] == diff]['dots_collected']
                for diff in ['easy', 'normal', 'hard'] if
                not df[df['difficulty'] == diff].empty]
        labels = [diff.capitalize() for diff in ['easy', 'normal', 'hard'] if
                  not df[df['difficulty'] == diff].empty]
        ax.boxplot(data, tick_labels=labels)
        ax.set_title('Dots Collected by Difficulty')
        ax.set_ylabel('Dots')
        ax.set_xlabel('Difficulty')

    def plot_ghosts_eaten(self, ax, df):
        """Plot ghosts eaten over sessions"""
        colors = {'easy': 'royalblue', 'normal': 'orange', 'hard': 'crimson'}
        markers = {'easy': 'o', 'normal': 's', 'hard': '^'}
        for diff in ['easy', 'normal', 'hard']:
            sub = df[df['difficulty'] == diff]
            if not sub.empty:
                grouped = sub.groupby('duration')['ghosts_eaten'].mean().reset_index()
                ax.plot(grouped['duration'], grouped['ghosts_eaten'],
                        marker=markers[diff], markersize=8, linestyle='-', linewidth=2,
                        color=colors[diff], label=diff.capitalize())
        ax.set_title('Ghosts Eaten Over Sessions')
        ax.set_xlabel('Session Duration (s)')
        ax.set_ylabel('Average Ghosts Eaten')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_facecolor('#f7f7f7')
        ax.legend()

    def plot_high_scores(self, ax, df):
        """Plot high scores per session"""
        colors = {'easy': 'royalblue', 'normal': 'orange', 'hard': 'crimson'}
        markers = {'easy': 'o', 'normal': 's', 'hard': '^'}
        for diff in ['easy', 'normal', 'hard']:
            sub = df[df['difficulty'] == diff]
            if not sub.empty:
                grouped = sub.groupby('duration')['score'].mean().reset_index()
                ax.plot(grouped['duration'], grouped['score'],
                        marker=markers[diff], markersize=8, linestyle='-', linewidth=2,
                        color=colors[diff], label=diff.capitalize())
        ax.set_title('High Scores Per Session')
        ax.set_xlabel('Session Duration (s)')
        ax.set_ylabel('Average Score')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_facecolor('#f7f7f7')
        ax.legend()

    def plot_player_vs_ghost(self, fig, df):
        """Plot player vs ghost ratio"""
        fig.clf()
        fig.set_size_inches(8, 5)
        fig.subplots_adjust(left=0.09, right=0.85, wspace=0.25, top=0.75, bottom=0.15)
        for i, diff in enumerate(['easy', 'normal', 'hard']):
            ax = fig.add_subplot(1, 3, i + 1)
            sub = df[df['difficulty'] == diff]
            ghosts_eaten = sub['ghosts_eaten'].sum()
            lives_lost = sub['lives_lost'].sum()
            total = ghosts_eaten + lives_lost
            if total == 0:
                ax.text(0.5, 0.5, f'No data for {diff.capitalize()}',
                        ha='center', va='center', fontsize=10)
                ax.axis('off')
            else:
                ax.pie(
                    [ghosts_eaten, lives_lost],
                    labels=['Ghosts Eaten', 'Get Eaten'],
                    autopct='%1.1f%%',
                    colors=['skyblue', 'salmon'],
                    textprops={'fontsize': 8},
                    radius=0.9
                )
                ax.set_title(f'{diff.capitalize()}', fontsize=13)
        fig.suptitle('Player vs. Ghost Ratio by Difficulty', fontsize=16, y=0.90)

    def update_plot(self, choice):
        """Update plot based on selection"""
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        try:
            df = pd.read_csv('game_stats.csv')
        except FileNotFoundError:
            ax.text(0.5, 0.5, 'No statistics data found to plot.',
                    ha='center', va='center', fontsize=12)
            self.canvas.draw()
            return

        if choice == 'Dots Collected by Difficulty':
            self.plot_dots_by_difficulty(ax, df)
        elif choice == 'Ghosts Eaten Over Sessions':
            self.plot_ghosts_eaten(ax, df)
        elif choice == 'High Scores Per Session':
            self.plot_high_scores(ax, df)
        elif choice == 'Player vs Ghost Ratio':
            self.plot_player_vs_ghost(self.fig, df)
        elif choice == 'Stats by Difficulty':
            self.plot_text_stats(ax, df)
        self.canvas.draw()

    def on_selection_change(self, _=None):
        """Handle selection change in combobox"""
        self.update_plot(self.combo.get())

    def go_back(self, back_callback):
        """Handle back button click"""
        self.win.destroy()
        if back_callback:
            back_callback()

    def quit_stats(self):
        """Handle quit button click"""
        os._exit(0)

    def show_graph_selector(self, back_callback=None, btn_style=None):
        """Show graph selector window"""
        try:
            df = pd.read_csv('game_stats.csv')
        except FileNotFoundError:
            print("No statistics data found to plot.")
            return

        self.win = tk.Tk()
        self.win.title("Pixel Chomp Statistics")
        self.win.configure(bg='black')
        self.win.geometry('700x800')

        label_frame = tk.Frame(self.win, bg='black')
        label_frame.pack(pady=5)
        label = tk.Label(label_frame, text="Choose a graph to display:", bg='black', fg='white',
                         font=("Arial", 16, "bold"))
        label.pack(side=tk.LEFT, padx=(0, 10))

        self.combo = ttk.Combobox(label_frame, values=[
            'Dots Collected by Difficulty',
            'Ghosts Eaten Over Sessions',
            'High Scores Per Session',
            'Player vs Ghost Ratio',
            'Stats by Difficulty'
        ])
        self.combo.pack(side=tk.LEFT)

        self.fig = Figure(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.win)
        self.canvas.get_tk_widget().pack()

        self.combo.bind("<<ComboboxSelected>>", self.on_selection_change)
        self.combo.current(0)
        self.update_plot(self.combo.get())

        back_btn = tk.Button(
            self.win, text="BACK", command=lambda: self.go_back(back_callback),
            **btn_style
        )
        back_btn.pack(pady=20)

        quit_btn = tk.Button(
            self.win, text="QUIT", command=self.quit_stats,
            **btn_style
        )
        quit_btn.pack(pady=5)
        self.win.mainloop()
