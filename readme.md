# MedievAIl 

## Team Members
- **TREMINE Marin**: [GitHub](https://github.com/marintremine)
- **LOMBARDO Anthony**: [GitHub](https://github.com/Liwis779)
- **ROMANET Valentin**: [GitHub](https://github.com/ValRom28)
- **MARTIN-JOVE Charles**: [GitHub](https://github.com/charlesmj18)
- **OUSAID Lilia**: [GitHub](https://github.com/Lylia-04)
- **ORTI Augustin**: [Github](https://github.com/LogicPulsee)
- **PUSKULLU Muhammed**: [GitHub](https://github.com/MuhammedPuskullu)

## Description

MedievAIl is an Age of Empires II tribute developed in Python. It was created as a first-year engineering school's project at the National Institutes of Science and Technology of Centre Val de Loire .

## Tech Stack

The application is developed using the following technologies:

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-14354C?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-00599C?style=for-the-badge&logo=matplotlib&logoColor=white)
![Curses](https://img.shields.io/badge/Curses-3776AB?style=for-the-badge&logo=terminal&logoColor=white)

## Functionalities

While MedievAIl focuses on core combat mechanics rather than full empire management, it features a robust battle engine and specialized simulation tools:

- Battle Simulator: Orchestrates real-time combat between two AI-controlled generals.
  - Pygame View: A 2.5D isometric graphical interface with unit animations (attack, walk, die) and interactive controls like game speed adjustment, camera movement, and pause/save features.
  - Terminal View: A lightweight visualization using the curses library for quick simulation feedback.
- Tournament Mode: A benchmarking tool that runs automated round-robin matches between multiple AI generals across different scenarios. It generates a detailed HTML report summarizing global scores, win/loss matrices, and scenario-specific performance.
- Lanchester’s Laws (Bonus): We used matplotlib to plot the number of survivors at the end of a battle between N-size army against 2N-size, and compare it to the Linear Law (for melee units) and Square Law (for ranged units)
- Save & Snapshot System: The engine supports saving the current state of a battle to JSON or generating an instant HTML snapshot to inspect the battlefield state in a web browser.

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/marintremine/MedievAIl
   cd MedievAIl
   ```

2. **Create and Activate a Virtual Environment**:

    - First, create a virtual environment in the project directory:
    ```bash
    virtualenv .venv
    ```

    - Then, activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

3. **Install Dependencies**:
    - Download Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Game**

You can run the game and its various modes using the `battle` command:

- **Start a Battle**  
    ```bash
    python main.py battle scenario/<scenario> <AI1> <AI2> -t/-p -d DATAFILE
    ```
    - `<scenario>`: Scenario name
    - `<AI1>`, `<AI2>`: AI agent names
    - `-t`: (Optional) Launch terminal view
    - `-p`: (Optional) Launch PyGame view
    - `-d DATAFILE`: (Optional) Specify file to write battle data

Example : `python main.py battle scenarios/symmetric_armies.json aegis attacktest`

Use `python main.py battle --help` for more details on each command.

- **Start a Tourney**  
    ```bash
    python main.py tourney -G <AI1> <AI2> <AIn> -S scenarios/<scenario1> scenarios/<scenario2> scenarios/<scenarion> -N N
    ```
  
  - `-G`: Specifies generals that will fight each other
  - `<AI1>`, `<AI2>`, `<AIn>`: AI agent names; there is no limit to the number of generals
  - `-S`: Specifies scenarios that will be used
  - `<scenario1>`, `<scenario2>`, `<scenarion>`: Scenario names; there is no limit to the number of scenarios
  - `-N N`: Specifies the number of battles per pair
  - `-t`: (Optional) Launch terminal view
  - `-p`: (Optional) Launch PyGame view
  - `-d DATAFILE`: (Optional) Specify file to write battle data

Example : `python main.py tourney -G attacktest aegis braindead -S scenarios/scenario_test.json scenarios/symmetric_armies.json -N 2`

Use `python main.py tourney --help` for more details on each command.

- **Plot a battle**  
    ```bash
    python main.py plot <ai> <plotter> <scenario_args> 
    ```

  - `<ai>`: AI agent name, it's an AI fighting itself
  - `<plotter>`: Plotter names
  - `-N N`: Specifies the number of battles
  - `-d DATAFILE`: (Optional) Specify file to save the matplotlib plot

Example : `python main.py plot daft PlotLanchester Lanchester "[Pikeman,Crossbowman]" "range(1,100)"`

NB : Only the PlotLanchester plotter and Lanchester scenario were implemented

Use `python main.py plot --help` for more details on each command.

