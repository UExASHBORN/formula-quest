# Formula Quest

A beginner-friendly desktop game built with Python and Pygame
to help students practise and remember mathematical formulas.

## Features

- Easy mode: Browse formulas, explanations, and worked examples.
- Medium mode: Answer four-option multiple-choice questions.
- Hard mode: Recall answers from memory with hints and answer reveal.
- Revision mode: Practise formulas previously answered incorrectly.
- Local progress persistence using JSON.
- Separate tracking for correct, incorrect, and assisted answers.
- No accounts, internet connection, database, or external API required.

## Technology

- Python 3
- Pygame
- JSON
- pathlib, json, and random from the Python standard library

## Requirements

- Python 3.10 or newer recommended
- pip
- A desktop environment capable of displaying a Pygame window

## Installation on Ubuntu/Debian

Open a terminal and move into the project directory.

Create a virtual environment:

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

Install the dependencies:

    python -m pip install -r requirements.txt

If virtual-environment creation fails because the venv module is
missing, install it using your distribution's package manager:

    sudo apt update
    sudo apt install python3-venv python3-pip

Launch the game:

    python main.py

## Controls

- Mouse: Navigate menus and select answers.
- Keyboard: Type answers in Hard mode.
- Enter: Submit an answer in Hard mode.
- Backspace: Delete a character while typing.
- Escape: Return to the main menu.

## Project structure

    formula_quest/
    ├── main.py
    ├── game.py
    ├── questions.py
    ├── progress.py
    ├── ui.py
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    └── data/
        └── formulas.json

The game creates data/progress.json automatically when it starts.

## Adding a formula

Add a new object to data/formulas.json.

Every object must include:

- id
- topic
- name
- formula
- explanation
- example_question
- correct_answer
- worked_solution
- question
- options
- hint
- hard_prompt
- accepted_answers

Use a unique ID. Provide exactly four distinct MCQ options, including
the correct answer. Add accepted answer variants that are genuinely
equivalent and appropriate for the expected notation.

Validate the JSON after editing. Restart the game to load the changes.

## Progress tracking

Progress is saved locally in data/progress.json.

The application tracks quiz submissions, independently correct
answers, incorrect answers, assisted answers, and formulas attempted.

Independent accuracy excludes assisted answers.

## Limitations

- Answer checking uses explicitly listed accepted answers.
- General symbolic equivalence is not implemented.
- Formula content should be independently checked before exam use.
- Progress is stored on the local machine.

## Future improvements

- Topic filters for GATE CS, GATE DA, CAT, and CMAT.
- Timed practice sessions.
- Formula search and bookmarking.
- Spaced-repetition scheduling.
- More verified question banks.
- Unit tests and automated content validation.
- Improved mathematical notation rendering.