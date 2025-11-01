# PokerMind: A Multi-Modal, Adaptive AI for Strategic and Social Poker Play

## Abstract

Current poker AIs excel in statistical reasoning but lack the social intelligence that defines expert human play. This project bridges that gap by developing **PokerMind**, an AI framework that integrates hard statistical analysis with soft social reasoning. PokerMind doesn't just calculate odds; it models opponent strategies, infers how it is perceived, and actively manages its table image to deceive and adapt. By combining Convolutional Neural Networks (CNNs) for hand analysis, Bayesian opponent modeling, and a novel "Social Perception Module," this project aims to create a more holistic and human-like poker AI capable of dynamic meta-strategy.

## Research Gap & Motivation

Existing research tackles poker AI in isolated silos:
*   **Statistical Modeling:** Focuses on hand strength (e.g., [4]) and opponent strategy prediction using Bayesian methods and neural networks (e.g., [3]).
*   **Social Intelligence:** Explores how nonverbal cues affect human perception of a robot's intentions (e.g., [2]).
*   **Specific Game AI:** Builds models for particular tasks like bidding in Dou-Di-Zhu (e.g., [1]).

**The Gap:** No existing system integrates these facets. A truly robust AI must not only predict opponent moves but also understand and manipulate the social narrative of the game. PokerMind addresses this by creating a unified architecture for **multi-modal opponent modeling** and **adaptive strategic deception**.

## Features

*   **Integrated Opponent Modeling:**
    *   **Statistical Model:** Uses Bayesian inference and neural networks to predict opponent hand ranges and strategies.
    *   **Player Typing:** Classifies opponents into predefined archetypes (e.g., Tight-Aggressive, Loose-Passive).
    *   **Social Perception Module:** Models how each opponent likely perceives the AI (e.g., as a "Bluffer" or "Rock"), based on the AI's own action history.

*   **Meta-Strategy & Deception:**
    *   The AI uses its integrated model to execute a dynamic strategy. It can intentionally bluff or play passively to reinforce or contradict its current table image, confusing opponents and exploiting their misreadings.

*   **Efficient Hand Evaluation:**
    *   Implements a lightweight, regression-based hand strength calculator for fast, real-time decision-making.

*   **Multi-Variant Framework:**
    *   The core architecture is designed to be adaptable to various poker games, including Texas Hold'em and Dou-Di-Zhu.

## Project Structure
