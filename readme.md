# MedievAIl 

## Team Members
- **TREMINE Marin**: [GitHub](https://github.com/marintremine)
- **PUSKULLU Muhammed**: [GitHub](https://github.com/MuhammedPuskullu)
- **MARTIN-JOVE Charles**: [GitHub](https://github.com/charlesmj18)
- **ROMANET Valentin**: [GitHub](https://github.com/ValRom28)
TODO: Add other team members

## Description

TODO

## Tech Stack

The application is developed using the following technologies:

TODO

## Functionalities

TODO

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/marintremine/MedievAIl
   cd MedievAIl
   ```

2. **Create and Activate a Virtual Environment**:

    - First, create a virtual environment in the project directory:
    ```bash
    virtualenv venv
    ```

    - Then, activate the virtual environment:
    ```bash
    source venv/bin/activate
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
    python main.py battle run <scenario> <AI1> <AI2> [-t] [-d DATAFILE]
    ```
    - `<scenario>`: Scenario name
    - `<AI1>`, `<AI2>`: AI agent names
    - `-t`: (Optional) Launch terminal view instead of 2.5D
    - `-d DATAFILE`: (Optional) Specify file to write battle data

- **Load a Saved Game**  
    ```bash
    python main.py battle load <savefile>
    ```
    - `<savefile>`: Path to the saved game file

Use `python main.py battle --help` for more details on each command.
