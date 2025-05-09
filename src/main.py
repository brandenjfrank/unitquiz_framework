import os
import json
import re
import random


QUIZ_ROOT = os.path.join(os.path.dirname(__file__), "..", "quizzes")

def print_welcome():
    print("=" * 60)
    print("🧠  Welcome to UnitQuiz!")
    print("📚  A command-line quiz tool for study guides and certifications")
    print("=" * 60)
    print()

def list_study_guides():
    guides = []
    for name in os.listdir(QUIZ_ROOT):
        path = os.path.join(QUIZ_ROOT, name)
        if os.path.isdir(path) and name.startswith("SG_"):
            guides.append(name)
    return sorted(guides)

def choose_study_guide(guides):
    print("Available Study Guides:\n")
    for i, guide in enumerate(guides, 1):
        print(f"{i}. {guide}")
    print()

    while True:
        choice = input("Enter the number of the study guide to load: ")
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(guides):
                return guides[index]
        print("Invalid input. Try again.\n")


def list_units_in_guide(guide_path):
    units = []
    
    # Go through subfolders in the study guide
    for folder in sorted(os.listdir(guide_path)):
        folder_path = os.path.join(guide_path, folder)
        if os.path.isdir(folder_path) and folder.startswith("unit_"):
            # Look for the .json file inside the unit folder
            for file in os.listdir(folder_path):
                if file.endswith(".json"):
                    full_path = os.path.join(folder_path, file)
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        units.append({
                            "filename": file,
                            "filepath": full_path,
                            "unit_number": data.get("unit_number", 0),
                            "title": data.get("title", "Untitled Unit"),
                            "summary": data.get("summary", ""),
                            "questions": data.get("questions", [])
                        })
    return units

def choose_unit_action(units):
    print("Available Units:\n")
    for u in units:
        print(f"{u['unit_number']}. {u['title']}")
    print()

    while True:
        action = input("Type 'summary' to read a unit summary, or 'quiz' to continue to quiz setup: ").strip().lower()
        if action == "summary":
            unit_input = input("Enter the unit number to view its summary: ")
            if unit_input.isdigit():
                unit_number = int(unit_input)
                unit = next((u for u in units if u["unit_number"] == unit_number), None)
                if unit:
                    print(f"\n📘 Unit {unit['unit_number']}: {unit['title']}")
                    print("-" * 60)
                    print(unit["summary"])
                    print("-" * 60)
                    print()
                    continue  # Allow user to view another summary or switch to quiz
            print("❌ Invalid unit number.\n")

        elif action == "quiz":
            return  # proceed to quiz setup
        else:
            print("❌ Invalid input. Please type 'summary' or 'quiz'.\n")

def select_units_for_quiz(units):
    print("\nWhich units would you like to quiz on?")
    print("Examples: 1,2,3  or  5  or  all\n")

    selected_input = input("Enter unit numbers (comma-separated or 'all'): ").strip().lower()

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
        return select_units_for_quiz(units)

    return selected_units

def choose_question_count(total_available):
    print("\nHow many questions would you like to take? (10, 20, 50, all)")

    allowed = [10, 20, 50]
    while True:
        entry = input("Enter a number (10/20/50) or 'all': ").strip().lower()
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
1

def main():
    print_welcome()

    guides = list_study_guides()
    if not guides:
        print("No study guides found in the quizzes folder.")
        return

    selected = choose_study_guide(guides)
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

    # TODO: Start quiz here
    print(f"\n🧪 Starting quiz with {len(quiz_questions)} questions...\n")

    

if __name__ == "__main__":
    main()