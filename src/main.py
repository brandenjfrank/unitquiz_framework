import os
import json
import re
import random

# Fix the base path for quiz files
# The problem is that the script is running from src/ but looking for quizzes/ inside src/
# We need to adjust the path based on your project structure

# Option 1: Look in the parent directory of the script
QUIZ_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "quizzes")

# Option 2: Look in the same directory as the script
# QUIZ_ROOT = os.path.join(os.path.dirname(__file__), "..", "quizzes")

# Option 3: Hard-code the absolute path
# QUIZ_ROOT = r"C:\Users\Joey\Documents\Code\Python\unitquiz_framework\quizzes"

def clear_screen():
    """Clear the console screen in a cross-platform way."""
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Mac and Linux
    else:
        os.system('clear')

def print_welcome():
    """Display welcome message."""
    clear_screen()
    print("=" * 60)
    print("🧠  Welcome to UnitQuiz!")
    print("📚  A command-line quiz tool for study guides and certifications")
    print("=" * 60)
    print(f"Looking for quizzes in: {QUIZ_ROOT}")  # Print the path for debugging
    print()

def list_study_guides():
    """List all available study guides in the quizzes directory."""
    guides = []
    if not os.path.exists(QUIZ_ROOT):
        print(f"Warning: Quiz directory '{QUIZ_ROOT}' not found.")
        create_choice = input("Would you like to create this directory? (y/n): ").lower()
        if create_choice == 'y':
            os.makedirs(QUIZ_ROOT, exist_ok=True)
            print(f"Created directory: {QUIZ_ROOT}")
        return guides
        
    for name in os.listdir(QUIZ_ROOT):
        path = os.path.join(QUIZ_ROOT, name)
        if os.path.isdir(path) and name.startswith("SG_"):
            guides.append(name)
    
    if not guides:
        print(f"No study guides found in {QUIZ_ROOT}")
        print("Make sure your study guides are in folders starting with 'SG_'")
    
    return sorted(guides)

def choose_study_guide(guides):
    """Let the user select a study guide."""
    if not guides:
        print("No study guides found. Please check your file structure.")
        return None
        
    print("Available Study Guides:\n")
    for i, guide in enumerate(guides, 1):
        # Display a cleaner name by removing prefix and underscores
        display_name = guide.replace("SG_", "").replace("_", " ").title()
        print(f"{i}. {display_name}")
    print()

    while True:
        choice = input("Enter the number of the study guide to load: ")
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(guides):
                return guides[index]
        print("Invalid input. Try again.\n")

def list_units_in_guide(guide_path):
    """Load all units from the specified study guide."""
    units = []
    
    # Check if guide_path exists
    if not os.path.exists(guide_path):
        print(f"Warning: Guide path '{guide_path}' not found.")
        return units
    
    # Go through subfolders in the study guide
    for folder in sorted(os.listdir(guide_path)):
        folder_path = os.path.join(guide_path, folder)
        if os.path.isdir(folder_path) and folder.startswith("unit_"):
            # Look for the .json file inside the unit folder
            for file in os.listdir(folder_path):
                if file.endswith(".json"):
                    full_path = os.path.join(folder_path, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            units.append({
                                "filename": file,
                                "filepath": full_path,
                                "unit_number": data.get("unit_number", 0),
                                "title": data.get("title", "Untitled Unit"),
                                "summary": data.get("summary", ""),
                                "key_takeaways": data.get("key_takeaways", []),
                                "questions": data.get("questions", [])
                            })
                    except json.JSONDecodeError:
                        print(f"Warning: Could not parse JSON file: {full_path}")
                    except Exception as e:
                        print(f"Error reading {full_path}: {e}")
    
    # Sort by unit number
    return sorted(units, key=lambda x: x["unit_number"])

def choose_unit_action(units):
    """Let the user choose to view a summary or start a quiz."""
    while True:
        # Clear screen and show units list
        clear_screen()
        print("\n🔍 UNIT SELECTION")
        print("=" * 60)
        print("Available Units:")
        print("-" * 60)
        
        # Display units in a cleaner format
        for u in units:
            print(f"{u['unit_number']:2d}. {u['title']}")
        
        print("\n" + "-" * 60)
        print("OPTIONS:")
        print("- Type 'summary' followed by a unit number (e.g., 'summary 3') to view a unit summary")
        print("- Type 'quiz' to continue to quiz setup")
        print("=" * 60)

        action = input("\nEnter command: ").strip().lower()
        
        # Handle "summary X" format
        if action.startswith("summary "):
            try:
                unit_number = int(action.split()[1])
                unit = next((u for u in units if u["unit_number"] == unit_number), None)
                if unit:
                    display_unit_summary(unit)
                    continue
                else:
                    print(f"❌ Unit {unit_number} not found.")
            except (IndexError, ValueError):
                print("❌ Invalid format. Use 'summary X' where X is a unit number.")
            
            input("Press Enter to continue...")
            
        # Handle just "summary" format
        elif action == "summary":
            unit_input = input("Enter the unit number to view its summary: ")
            if unit_input.isdigit():
                unit_number = int(unit_input)
                unit = next((u for u in units if u["unit_number"] == unit_number), None)
                if unit:
                    display_unit_summary(unit)
                    continue
                else:
                    print(f"❌ Unit {unit_number} not found.")
            else:
                print("❌ Invalid unit number.")
            
            input("Press Enter to continue...")

        elif action == "quiz":
            return  # proceed to quiz setup
        
        elif action == "exit" or action == "quit":
            if input("Are you sure you want to exit? (y/n): ").lower() == 'y':
                print("Exiting program. Goodbye!")
                exit(0)
        
        else:
            print("❌ Invalid input. Please type 'summary X' or 'quiz'.")
            input("Press Enter to continue...")

def display_unit_summary(unit):
    """Display a formatted summary of a unit."""
    clear_screen()
    print("\n" + "=" * 80)
    print(f"📘 UNIT {unit['unit_number']}: {unit['title']}")
    print("=" * 80 + "\n")
    
    # Print summary with improved formatting
    if unit["summary"]:
        print("SUMMARY:")
        print("-" * 80)
        
        # Break the summary into paragraphs for better readability
        paragraphs = unit["summary"].split('\n')
        for para in paragraphs:
            if para.strip():  # Only print non-empty paragraphs
                print(f"{para.strip()}\n")
    
    # Print key takeaways if available
    if unit.get("key_takeaways") and len(unit["key_takeaways"]) > 0:
        print("\nKEY TAKEAWAYS:")
        print("-" * 80)
        for i, takeaway in enumerate(unit["key_takeaways"], 1):
            print(f"{i}. {takeaway}")
    
    # Print question count
    question_count = len(unit.get("questions", []))
    print(f"\nThis unit contains {question_count} practice questions.")
    
    print("\n" + "=" * 80)
    input("\nPress Enter to return to unit selection...")

def select_units_for_quiz(units):
    """Let the user select which units to include in the quiz."""
    clear_screen()
    print("\n📋 QUIZ SETUP")
    print("=" * 60)
    print("Which units would you like to quiz on?")
    print("-" * 60)
    print("Examples: 1,2,3  or  5  or  all\n")

    # Display units again for reference
    for u in units:
        print(f"{u['unit_number']}. {u['title']} ({len(u['questions'])} questions)")
    
    print("-" * 60)
    selected_input = input("\nEnter unit numbers (comma-separated or 'all'): ").strip().lower()

    if selected_input == "all":
        selected_units = units
    else:
        try:
            selected_numbers = [int(n.strip()) for n in selected_input.split(",")]
            selected_units = [u for u in units if u["unit_number"] in selected_numbers]
        except ValueError:
            print("❌ Invalid format. Please enter numbers like 1,2 or 'all'.")
            return select_units_for_quiz(units)

    if not selected_units:
        print("❌ No valid units selected.")
        input("Press Enter to try again...")
        return select_units_for_quiz(units)

    return selected_units

def choose_question_count(total_available):
    """Let the user choose how many questions to include in the quiz."""
    clear_screen()
    print("\n🔢 QUIZ SIZE")
    print("=" * 60)
    print(f"How many questions would you like to include? (Total available: {total_available})")
    print("-" * 60)
    print("Options: 10, 20, 50, all")
    print("=" * 60)

    allowed = [10, 20, 50]
    while True:
        entry = input("\nEnter a number (10/20/50) or 'all': ").strip().lower()
        if entry == "all":
            return total_available
        if entry.isdigit():
            count = int(entry)
            if count in allowed:
                if count > total_available:
                    print(f"⚠️  Only {total_available} questions available. Using that instead.")
                    return total_available
                return count
        print("❌ Please enter 10, 20, 50, or 'all'.")

def run_quiz(questions):
    """Run the actual quiz with the selected questions."""
    score = 0
    incorrect_questions = []
    
    clear_screen()
    print("\n" + "=" * 60)
    print(f"🧠 QUIZ STARTING - {len(questions)} QUESTIONS")
    print("=" * 60 + "\n")
    print("Ready to begin? Good luck!")
    input("Press Enter to start the quiz...")
    
    for i, q in enumerate(questions, 1):
        clear_screen()
        print(f"\nQuestion {i} of {len(questions)}")
        print(f"From Unit {q['unit_number']}: {q['unit_title']}")
        print("-" * 60 + "\n")
        
        # Display question text (strip any markdown formatting)
        question_text = q['question']
        question_text = re.sub(r'\*\*Answer:\s*[A-E]\*\*', '', question_text)
        question_text = re.sub(r'\*\*|\*', '', question_text)
        print(f"{question_text.strip()}\n")
        
        # Create a copy of the options for randomization
        option_contents = []
        for option in q["options"]:
            # Clean up option text
            option_text = option['text']
            option_text = re.sub(r'\*\*Answer:\s*[A-E]\*\*', '', option_text)
            option_text = re.sub(r'\*\*|\*', '', option_text)
            
            # Save the cleaned text and whether this is the correct answer
            is_correct = (option['id'] == q['answer'])
            option_contents.append({
                'text': option_text.strip(),
                'is_correct': is_correct
            })
        
        # Randomize the option contents
        random.shuffle(option_contents)
        
        # Display options with fixed A, B, C, D labels
        option_labels = ['A', 'B', 'C', 'D', 'E']
        correct_label = None
        
        for idx, content in enumerate(option_contents):
            if idx < len(option_labels):
                label = option_labels[idx]
                print(f"  {label}) {content['text']}")
                
                # Track which letter is now the correct answer
                if content['is_correct']:
                    correct_label = label
        
        # Get user answer
        while True:
            user_answer = input("\nYour answer (A-E): ").strip().upper()
            if user_answer in option_labels[:len(option_contents)]:
                break
            print("❌ Invalid option. Please enter a letter corresponding to an option.")
        
        # Check answer
        correct = user_answer == correct_label
        if correct:
            score += 1
            print("\n✅ Correct!")
        else:
            print(f"\n❌ Incorrect. The correct answer is {correct_label}.")
            
            # Store the question with updated correct answer for review
            q_copy = q.copy()
            q_copy['randomized_answer'] = correct_label
            q_copy['randomized_options'] = option_contents
            q_copy['option_labels'] = option_labels[:len(option_contents)]
            incorrect_questions.append(q_copy)
        
        # Proceed to next question
        if i < len(questions):
            input("\nPress Enter for the next question...")
    
    # Show final score
    clear_screen()
    print("\n" + "=" * 60)
    print("🏁 QUIZ COMPLETE!")
    print("=" * 60)
    print(f"\nYour score: {score}/{len(questions)} ({score/len(questions)*100:.1f}%)")
    
    # Provide score interpretation
    if score == len(questions):
        print("\n🏆 Perfect score! Outstanding work!")
    elif score >= len(questions) * 0.8:
        print("\n🌟 Excellent! You've mastered most of the material.")
    elif score >= len(questions) * 0.7:
        print("\n👍 Good job! You have a solid understanding of the topics.")
    elif score >= len(questions) * 0.6:
        print("\n👌 Decent effort. Keep studying to improve.")
    else:
        print("\n📚 More review needed. Don't give up!")
    
    # Ask if they want to review incorrect questions
    if incorrect_questions:
        review = input("\nWould you like to review the questions you got wrong? (y/n): ").strip().lower()
        if review == 'y':
            review_incorrect_answers(incorrect_questions)
    
    print("\n" + "=" * 60)
    input("\nPress Enter to return to the main menu...")
    
    return score, len(questions)

def review_incorrect_answers(questions):
    """Allow the user to review incorrect answers."""
    for i, q in enumerate(questions, 1):
        clear_screen()
        print("\n" + "=" * 60)
        print(f"QUESTION REVIEW {i}/{len(questions)}")
        print("=" * 60 + "\n")
        
        print(f"From Unit {q['unit_number']}: {q['unit_title']}\n")
        
        # Clean up question text
        question_text = q["question"]
        question_text = re.sub(r'\*\*Answer:\s*[A-E]\*\*', '', question_text)
        question_text = re.sub(r'\*\*|\*', '', question_text)
        print(question_text.strip() + "\n")
        
        # Check if this question used randomized options
        if 'randomized_options' in q:
            # Display options with the same randomization used during the quiz
            for idx, label in enumerate(q['option_labels']):
                if idx < len(q['randomized_options']):
                    content = q['randomized_options'][idx]
                    if label == q['randomized_answer']:
                        print(f"  {label}) {content['text']} ✓")
                    else:
                        print(f"  {label}) {content['text']}")
            
            print(f"\nCorrect Answer: {q['randomized_answer']}")
        else:
            # Display options with original order (for backward compatibility)
            for option in q["options"]:
                option_text = option['text']
                option_text = re.sub(r'\*\*Answer:\s*[A-E]\*\*', '', option_text)
                option_text = re.sub(r'\*\*|\*', '', option_text)
                
                if option["id"] == q["answer"]:
                    print(f"  {option['id']}) {option_text.strip()} ✓")
                else:
                    print(f"  {option['id']}) {option_text.strip()}")
            
            print(f"\nCorrect Answer: {q['answer']}")
        
        if i < len(questions):
            input("\nPress Enter to continue to the next question...")
        else:
            input("\nPress Enter to finish review...")

def review_incorrect_answers(questions):
    """Allow the user to review incorrect answers."""
    for i, q in enumerate(questions, 1):
        clear_screen()
        print("\n" + "=" * 60)
        print(f"QUESTION REVIEW {i}/{len(questions)}")
        print("=" * 60 + "\n")
        
        print(f"From Unit {q['unit_number']}: {q['unit_title']}\n")
        
        # Clean up question text
        question_text = q["question"]
        question_text = re.sub(r'\*\*Answer:\s*[A-E]\*\*', '', question_text)
        question_text = re.sub(r'\*\*|\*', '', question_text)
        print(question_text.strip() + "\n")
        
        # Display options with correct answer highlighted
        for option in q["options"]:
            option_text = option['text']
            option_text = re.sub(r'\*\*Answer:\s*[A-E]\*\*', '', option_text)
            option_text = re.sub(r'\*\*|\*', '', option_text)
            
            if option["id"] == q["answer"]:
                print(f"  {option['id']}) {option_text.strip()} ✓")
            else:
                print(f"  {option['id']}) {option_text.strip()}")
        
        print(f"\nCorrect Answer: {q['answer']}")
        
        if i < len(questions):
            input("\nPress Enter to continue to the next question...")
        else:
            input("\nPress Enter to finish review...")

def main():
    """Main application function."""
    print_welcome()

    guides = list_study_guides()
    if not guides:
        print("No study guides found in the quizzes folder.")
        return

    selected = choose_study_guide(guides)
    if not selected:
        return
        
    guide_path = os.path.join(QUIZ_ROOT, selected)

    units = list_units_in_guide(guide_path)
    if not units:
        print("No units found in the selected study guide.")
        return

    choose_unit_action(units)
    selected_units = select_units_for_quiz(units)

    # Collect all questions from selected units
    all_questions = []
    for u in selected_units:
        for q in u["questions"]:
            question_copy = q.copy()
            question_copy["unit_number"] = u["unit_number"]
            question_copy["unit_title"] = u["title"]
            all_questions.append(question_copy)

    if not all_questions:
        print("❌ No questions found in the selected units.")
        return

    count = choose_question_count(len(all_questions))
    random.shuffle(all_questions)
    quiz_questions = all_questions[:count]

    # Run the quiz
    run_quiz(quiz_questions)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nQuiz terminated. Goodbye!")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        input("Press Enter to exit...")