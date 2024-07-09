import os
import sys
import threading
import time
import textwrap

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
CYAN = "\033[36m"

# Function to print the static cat
def print_static_cat(frame):
    sys.stdout.write('\033[H')  # Move cursor to the top
    for i, line in enumerate(frame.splitlines()):
        sys.stdout.write(f'\033[{i+1};1H{line}')  # Print each line of the frame at the correct position
    sys.stdout.flush()

# Function to animate the cat
def animate(frames, delay=0.12):
    end_time = time.time() + 5  # Run animation for 5 seconds
    while time.time() < end_time:
        for frame in frames:
            sys.stdout.write('\033[H')  # Move cursor to the top
            for i, line in enumerate(frame.splitlines()):
                sys.stdout.write(f'\033[{i+1};1H{line}')  # Print each line of the frame at the correct position
            sys.stdout.flush()
            time.sleep(delay)

# Function to handle the answering animation
def answering_animation(skipped_lines):
    end_time = time.time() + 5  # Run animation for 5 seconds
    animation_frames = ["Cat's answering   ", "Cat's answering.  ", "Cat's answering.. ", "Cat's answering..."]
    while time.time() < end_time:
        for frame in animation_frames:
            sys.stdout.write(f'\033[{3 + skipped_lines};55H{GREEN}{frame}{RESET}')
            sys.stdout.flush()
            time.sleep(0.5)

# Function to display the answer after the "thinking" animation
def display_answer(skipped_lines):
    with open("answer.txt", "r", encoding="utf8") as f:
        answer = f.read().strip()
    sys.stdout.write(f'\033[{2 + skipped_lines};55H{" " * 30}')  # Clear the thinking line
    answer = f'{GREEN}Answer:{RESET} {answer}'
    wrapped_answer = textwrap.wrap(answer, width=83)  # Adjust width to fit the display
    for i, line in enumerate(wrapped_answer):
        sys.stdout.write(f'\033[{3 + i + skipped_lines};55H{line}')
    sys.stdout.write(f'\033[{4 + len(wrapped_answer) + skipped_lines};55HPress {CYAN}Enter{RESET} to continue')
    sys.stdout.flush()

# Function to prompt for user input
def prompt_for_input(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    user_input = input().strip()
    return user_input

# Main function to run the application
def main():
    frames = []
    for i in range(7):
        with open(f'cat_typing_{i}.txt', encoding="utf8") as file:
            frames.append(file.read())

    while True:
        # Clear the console
        os.system('cls' if os.name == 'nt' else 'clear')

        # Print the static cat first
        print_static_cat(frames[0])

        # Prompt for user input
        question = prompt_for_input(f'\033[1;55H{RED}Question: {RESET}')
        
        # Save user input to prompt.txt
        with open("prompt.txt", "w", encoding="utf8") as f:
            f.write(question)
            
        os.system('cls' if os.name == 'nt' else 'clear')

        wrapped_question = textwrap.wrap(question, width=80)
        sys.stdout.write(f'\033[1;55H{RED}Question: {RESET}{wrapped_question[0]}')
        for i, line in enumerate(wrapped_question[1:], start=1):
            sys.stdout.write(f'\033[{1 + i};55H{line}')
        sys.stdout.flush()
        
        # Start the cat animation and answering animation concurrently
        animation_thread = threading.Thread(target=animate, args=(frames,))
        answering_thread = threading.Thread(target=answering_animation, args=(len(wrapped_question) - 1,))
        
        animation_thread.start()
        answering_thread.start()
        
        animation_thread.join()
        answering_thread.join()

        # Display the answer from answer.txt
        display_answer(len(wrapped_question) - 1)

        # Wait for the user to press Enter to continue
        input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass  # Allow the user to exit the loop with Ctrl+C
