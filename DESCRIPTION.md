# Pixel Chomp

## 1. Project Overview
This project creates a Pac-Man game using Python and Pygame. The game features a classic arcade-style maze where the player controls Pac-Man to eat dots and avoid ghosts. Game mechanics include power-ups, multiple difficulty levels, and score tracking.

## 2. Project Review
An analysis of existing Pac-Man games revealed improvements for:
- Enhanced ghost pathfinding and movement
- Player statistics tracking
- Timer for round duration
- Three difficulty levels with varied mechanics

## 3. Programming Development

### 3.1 Game Concept
Guide Pac-Man through a maze to collect dots and avoid ghosts. Power pellets allow temporary ghost-eating.

**Game Modes:**
1. **Easy**: Standard gameplay
2. **Normal**: Faster ghosts, shorter power-up duration
3. **Hard**: More ghosts, high speed, fewer power-ups

### 3.2 Object-Oriented Programming Implementation

#### PacMan (Player Character)
- **Attributes**: position, speed, state, lives
- **Methods**: move(), eat_dot(), eat_ghost(), power_up()

#### Ghost (Enemy)
- **Attributes**: position, speed, direction, AI_state (chase/scatter/frightened)
- **Methods**: move(), change_state(), respawn(), check_collisions()

#### Maze (Game Map)
- **Attributes**: layout, dots, power_pellets
- **Methods**: load_maze(), check_collision(), remove_dot()

#### GameController (Game Logic)
- **Attributes**: game_state, score, timer, game_mode
- **Methods**: start_game(), update_game_state(), check_win_condition(), set_difficulty()

#### StatisticsManager (Player Data Tracker)
- **Attributes**: player_data, session_timer
- **Methods**: record_data(), save_to_file(), generate_report()

### 3.3 Algorithms Involved
- A* or BFS for ghost pathfinding
- Event-driven input handling
- Timer tracking for session and power-ups

## 4. Statistical Data (Prop Stats)

### 4.1 Data Features
Tracks:
1. Power pellets collected
2. Dots collected
3. Ghosts eaten
4. Survival time per session
5. High score history

### 4.2 Data Recording Method
Data stored in CSV

### 4.3 Data Analysis Report

**Basic Stats:**
- Mean: Average dots per game
- Median: Survival time
- Std Deviation: Performance consistency

**Trends:**
- Score progression
- Survival trends
- Ghost encounters

**Visualization:**
- Line Graphs: Score over time
- Bar Charts: Performance by mode
- Pie Charts: Player vs Ghost interactions

## 5. Project Timeline

| Week | Task |
|------|------|
| 1 (10 Mar) | Proposal submission / Project initiation |
| 2 (17 Mar) | Full proposal submission |
| 3 (24 Mar) | Initial game prototype development |
| 4 (31 Mar) | AI implementation |
| 5 (7 Apr) | Difficulty modes + stats integration |
| 6 (14 Apr) | Draft submission |

### Milestone Breakdown

| Week | Goal | Milestone |
|------|------|-----------|
| 1 (10 Mar) | Proposal | Submitted & initiated |
| 2 (17 Mar) | Full Proposal | Submitted & approved |
| 3 (3-9 Apr) | Prototype Dev | Core mechanics complete |
| 4 (10-16 Apr) | AI Implementation | Pathfinding & chase AI |
| 5 (17-23 Apr) | Difficulty + Stats | Integrated and tested |
| 6 (24 Apr - 11 May) | Polishing + Docs | Final report & presentation ready |

---

## Feature Data Collection Table

| Feature | Purpose | Collection Method | Class/Variable | Display Method |
|--------|---------|-------------------|----------------|----------------|
| Dots collected | Measure efficiency | Record at 10 timestamps | `PacMan.dots_collected` | Bar Chart (by difficulty) |
| Ghosts eaten | Risk & power-up use | Track each ghost eaten at 10 timestamps | `PacMan.ghosts_eaten` | Line Graph |
| Survival time | Assess endurance | Record every 10 seconds | `StatisticsManager.session_timer` | Median, Std Dev |
| High score | Progress tracking | Log score at 10 timestamps | `GameController.score` | Line Graph |
| Player vs Ghost Ratio | Aggression vs caution | Track ghost and Pac-Man deaths | `PacMan.eat_ghost()` & `PacMan.live` | Pie Chart |

---

## Graph Objectives Summary

| Graph | Feature | Objective | Type | X-axis | Y-axis |
|-------|---------|-----------|------|--------|--------|
| Graph 1 | Dots collected | Player efficiency | Bar | Difficulty | Dots |
| Graph 2 | Ghosts eaten | Risk behavior | Line | Session | Ghosts Eaten |
| Graph 3 | Survival time | Difficulty balance | Median/SD | Session | Time (s) |
| Graph 4 | High score | Progression | Line | Session | Score |
| Graph 5 | Player vs Ghost Ratio | Interaction balance | Pie | Ghosts vs Pac-Man | % Interactions |
