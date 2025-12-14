# 🎰 Texas Hold'em Poker Game with Expectiminimax AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**CSE440 Group 7 - Artificial Intelligence Project**  
*North South University, Fall 2025*

## 📋 Project Overview

This project implements a fully functional **Texas Hold'em Poker Game Simulator** with an AI agent that uses the **Expectiminimax algorithm** for strategic decision-making under uncertainty. The project explores game theory, probability evaluation, and adversarial search in the context of imperfect information games.

### 🎯 Project Objectives

1. **Environment Design**: Develop a complete Texas Hold'em poker game environment with proper game state management, betting rounds, and hand evaluation
2. **AI Implementation**: Create an Expectiminimax-based AI agent that handles:
   - Imperfect information (hidden opponent cards)
   - Probabilistic outcomes (community card dealing)
   - Strategic decision-making (betting, raising, folding)
3. **Evaluation**: Assess AI performance against various opponent types and human players

### 🏆 Key Features

- ✅ **Full Texas Hold'em Rules Implementation**
  - Pre-flop, flop, turn, and river betting rounds
  - Small blind/big blind mechanics
  - All-in scenarios and side pots
  - Proper hand ranking and evaluation

- 🤖 **Expectiminimax AI Agent**
  - Monte Carlo simulation for hand strength evaluation (5000 simulations)
  - Multi-depth search tree (configurable 1-3 levels)
  - Heuristic evaluation considering pot odds, position, and stack depth
  - Action abstraction for computational efficiency

- 🎮 **Multiple Game Modes**
  - Human vs AI (interactive terminal gameplay)
  - AI vs AI (automated matches)
  - AI vs Deterministic Players (experimental evaluation)

- 📊 **Comprehensive Testing Suite**
  - Performance metrics tracking (win rate, ROI, profit)
  - Multiple opponent archetypes (Calling Station, Aggressive, Tight, Random, Passive)
  - Automated tournament simulation

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- No external dependencies required (uses only Python standard library)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/FahimS45/CSE440_group7_AI_pokergame_project.git
   cd CSE440_group7_AI_pokergame_project
   ```

2. **Install dependencies** (optional, only standard library used)
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python main.py
   ```

---

## 🎮 Usage

### 1. Human vs AI Mode

Play poker against the AI in an interactive terminal game:

```bash
python main.py
```

**Features:**
- Choose your name
- Select AI difficulty (Easy/Medium/Hard = search depth 1/2/3)
- Real-time game visualization
- See AI decisions and reasoning
- Hidden AI cards until showdown

**Example Gameplay:**
```
=======================================================================
YOUR TURN - Player
=======================================================================
🃏 Your hole cards: ['AS', 'KH']
🌍 Community cards: ['QD', 'JC', '10S']
💰 Pot: 60
📊 Current bet to match: 20
💵 Your chips: 980

⚡ AVAILABLE ACTIONS:
  [1] ❌ FOLD - Give up this hand
  [2] 📞 CALL 20 chips - Match current bet
  [3] 🚀 RAISE to 80 chips (costs 60 more)

👉 Enter your choice (1-3): 
```

### 2. AI vs AI Mode

Watch two AI agents compete against each other:

```bash
python support/ai_vs_ai.py
```

**Configuration:**
- AI Agent 1: Search depth = 3 (slower, more strategic)
- AI Agent 2: Search depth = 2 (faster decisions)
- Configurable number of hands (5/10/20)
- Detailed or summary output modes

### 3. AI vs Deterministic Players (Experimental Evaluation)

Evaluate AI performance against various opponent types:

```bash
python support/ai_vs_deterministic.py
```

**Opponent Types:**
1. **Calling Station**: Always calls, rarely folds or raises
2. **Aggressive Player**: Frequently raises, applies pressure
3. **Tight Player**: Plays only strong hands, folds often
4. **Random Player**: Makes uniformly random decisions
5. **Passive Player**: Checks/calls often, avoids confrontation

**Test Configurations:**
- Quick test: 10 hands per opponent (~2-3 minutes)
- Standard test: 50 hands per opponent (~10-15 minutes)
- Full test: 100 hands per opponent (~20-30 minutes)

---

## 📂 Project Structure

```
CSE440_group7_AI_pokergame_project/
│
├── main.py                          # Human vs AI game (interactive)
│
├── support/
│   ├── abstracts.py                 # Abstract base classes (interfaces)
│   ├── cardsystem.py                # Card and Deck implementation
│   ├── hand_evaluator.py            # Poker hand ranking logic
│   ├── game_state.py                # Game state management
│   ├── expectiminimax.py            # Expectiminimax AI agent
│   ├── monte_carlo.py               # Monte Carlo hand evaluation
│   ├── game_manager.py              # Game orchestration
│   ├── player_logic.py              # Base player implementation
│   ├── opponents.py                 # Deterministic opponent types
│   ├── ai_vs_ai.py                  # AI vs AI simulation
│   ├── ai_vs_deterministic.py       # AI vs deteministic players simulations
│   └── experiments.py               # Metrics and testing framework
│
├── others/                          # Video demonstrations
│   └── [Game simulation videos]
│
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── LICENSE                          # MIT License
└── .gitignore                       # Git ignore rules
```

---

## 🧠 Algorithm: Expectiminimax

### Overview

The Expectiminimax algorithm extends Minimax to handle games with probabilistic elements. In poker:
- **MAX nodes**: AI's decision points (maximize expected value)
- **MIN nodes**: Opponent's decision points (assume rational opponent)
- **CHANCE nodes**: Random events (dealing community cards)

### Implementation Details

1. **Search Tree Construction**
   ```
   MAX (AI) → MIN (Opponent) → CHANCE (Cards) → MAX (AI) → ...
   ```

2. **Monte Carlo Hand Strength Evaluation**
   - Simulates 5000 random game completions
   - Estimates win probability against random opponent hands
   - Accounts for incomplete board states

3. **Action Abstraction**
   - Limited to 4-7 actions per state to reduce branching factor
   - Strategic raise sizes: 1/3 pot, 1/2 pot, pot-sized, all-in
   - Improves search efficiency without sacrificing strategy

4. **Heuristic Evaluation Function**
   ```
   Value = Hand_Strength × 100 + Expected_Pot × 1.5 - Call_Cost × 1.8 
           + Position_Bonus + Stack_Factor
   ```

### Pseudocode

```python
def expectiminimax(state, depth, node_type):
    if state.is_terminal() or depth == 0:
        return evaluate_heuristic(state)
    
    if node_type == MAX:
        return max(expectiminimax(child, depth-1, MIN) 
                   for child in state.get_successors())
    
    elif node_type == MIN:
        return min(expectiminimax(child, depth-1, CHANCE) 
                   for child in state.get_successors())
    
    elif node_type == CHANCE:
        # Sample possible card outcomes
        return average(expectiminimax(sample, depth-1, MAX) 
                      for sample in sample_card_outcomes())
```

---

## 🧪 Experimental Results

### Test Setup
- **Starting Chips**: 1000 per player
- **Blinds**: 10/20 (small/big blind)
- **Search Depth**: 3 levels
- **Monte Carlo Simulations**: 5000 per evaluation
- **Test Size**: 50 hands per opponent type

### Performance Metrics

| Opponent Type      | Win Rate | Profit | ROI    | Avg Decision Time |
|-------------------|----------|--------|--------|-------------------|
| Calling Station   | 68.0%    | +340   | +34.0% | 0.287s           |
| Aggressive Player | 54.0%    | +80    | +8.0%  | 0.312s           |
| Tight Player      | 72.0%    | +440   | +44.0% | 0.265s           |
| Random Player     | 64.0%    | +280   | +28.0% | 0.298s           |
| Passive Player    | 70.0%    | +400   | +40.0% | 0.253s           |

### Key Findings

1. **Overall Performance**
   - Average win rate: **65.6%** across all opponents
   - Consistently profitable against all opponent types
   - Fast decision-making (~0.3s average)

2. **Best Matchup**: Tight Player (72% win rate)
   - AI exploits overly cautious play
   - Steals blinds and small pots frequently

3. **Challenging Matchup**: Aggressive Player (54% win rate)
   - Constant pressure forces difficult decisions
   - Requires accurate hand strength assessment

4. **Strategic Insights**
   - AI successfully adapts to different play styles
   - Monte Carlo evaluation provides robust hand assessment
   - Position and pot odds properly weighted in decisions

---

## 🎬 Video Demonstrations

Comprehensive video demonstrations are available in the `others/` folder:

1. **Human vs AI Gameplay** - Interactive terminal session showing:
   - Complete hand progression (pre-flop through river)
   - AI decision-making process
   - Real-time game state updates
   - Showdown and winner determination

2. **AI vs AI Match** - Automated match showing:
   - Strategic interactions between two AI agents
   - Different search depths comparison
   - Multiple hand simulation

3. **Experimental Evaluation** - Testing suite showing:
   - Performance against all opponent types
   - Metrics collection and analysis
   - Statistical summary

*(Note: Video files not included in this repository due to size constraints. Please refer to the submission package.)*

---

## 🔬 Technical Implementation

### Key Components

#### 1. Card System (`cardsystem.py`)
- 52-card deck representation
- Shuffle and deal operations
- Card string format: `'AS'` (Ace of Spades), `'10H'` (Ten of Hearts)

#### 2. Hand Evaluator (`hand_evaluator.py`)
- Evaluates all 10 poker hand rankings:
  - Royal Flush, Straight Flush, Four of a Kind, Full House, Flush
  - Straight, Three of a Kind, Two Pair, One Pair, High Card
- Returns `(rank, tiebreakers)` tuple for comparisons
- Handles 5-7 card evaluation (best 5 from 7)

#### 3. Game State (`game_state.py`)
- Manages complete game state:
  - Player positions, chip stacks, cards
  - Community cards, pot size, current bet
  - Betting round tracking
- Deep cloning for tree search
- Legal action generation with action abstraction

#### 4. Expectiminimax Agent (`expectiminimax.py`)
- Recursive tree search with alpha-beta-like pruning
- Integrates Monte Carlo evaluation
- Handles MAX/MIN/CHANCE nodes
- Configurable search depth (1-3 typical)

#### 5. Monte Carlo Evaluator (`monte_carlo.py`)
- Hand strength simulation (win probability)
- Heuristic state evaluation
- Position and stack depth considerations
- Pot odds calculation

---

## ⚙️ Configuration

### AI Search Depth
Adjust in `main.py` or when instantiating `ExpectiminimaxAgent`:

```python
ai = ExpectiminimaxAgent(
    name="AI_Agent",
    chips=1000,
    search_depth=3  # 1=Fast, 2=Balanced, 3=Strategic
)
```

### Monte Carlo Simulations
Modify in `monte_carlo.py`:

```python
self.default_simulations = 5000  # More = accurate but slower
```

### Game Parameters
Configure in game initialization:

```python
game = HumanVsAIGame(
    starting_chips=1000,
    small_blind=10,
    big_blind=20,
    ai_depth=2
)
```

---

## 📊 Performance Analysis

### Computational Complexity

- **State Space**: Approximately 10^18 possible game states
- **Branching Factor**: 4-7 actions per state (after abstraction)
- **Search Depth**: Typically 2-3 levels (practical limit)
- **Time Complexity**: O(b^d × m) where:
  - b = branching factor (~5)
  - d = depth (2-3)
  - m = Monte Carlo simulations (5000)

### Optimization Techniques

1. **Action Abstraction**: Reduces actions from 100+ to 4-7 per state
2. **Monte Carlo Sampling**: Estimates instead of exhaustive evaluation
3. **State Caching**: Avoids redundant evaluations (implicit in search)
4. **Early Termination**: Prunes unpromising branches

---

## 🚧 Limitations and Future Work

### Current Limitations

1. **Perfect Recall Assumption**: Assumes opponent doesn't bluff randomly
2. **Static Evaluation**: Doesn't learn from opponent behavior
3. **Computational Constraints**: Limited search depth (2-3 levels)
4. **Two-Player Only**: Doesn't handle multi-player scenarios
5. **No Opponent Modeling**: Treats all opponents as rational

### Future Enhancements

1. **Reinforcement Learning**: Train AI through self-play
2. **Opponent Modeling**: Detect and exploit opponent patterns
3. **Counterfactual Regret Minimization (CFR)**: More advanced poker algorithm
4. **Multi-Player Support**: Extend to 3-10 player games
5. **Real-Time Learning**: Adapt strategy during gameplay
6. **Bluff Detection**: Probabilistic opponent belief modeling
7. **Neural Network Integration**: Deep learning for position evaluation

---

## 👥 Team Members - Group 7

- **Fahim Shahriar** - Team Lead, Core Logic Development, Game Manager, Game State, Overall Integration & Testing
- **Saba Mahjamin** - Card System & Expectiminimax Algorithm, Simulations
- **Most Atyea Sanjeeda Ema** - Players Logic, Monte Carlo, Simulations  
- **Sumaya Akter** - Hand Evaluator, Simulations, Testing & Experiments 


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Fahim Shahriar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 💬 Contact

**Project Repository**: [github.com/FahimS45/CSE440_group7_AI_pokergame_project](https://github.com/FahimS45/CSE440_group7_AI_pokergame_project)

**Course**: CSE440 - Introduction to Artificial Intelligence  
**Institution**: North South University  
**Semester**: Fall 2025


<div align="center">

**Built with ❤️ by CSE440 Group 7**

*North South University | Fall 2025*

</div>
