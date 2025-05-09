import os
import json
import re
import sys

# Base paths - adjust as needed
QUIZ_ROOT = "quizzes"
GUIDE_NAME = "SG_01__salesforce_ai_associate"

def clean_title_for_filename(title):
    """Convert a title to a suitable filename format."""
    # Convert to lowercase
    clean = title.lower()
    # Replace spaces and non-alphanumeric chars with underscores
    clean = re.sub(r'[^a-z0-9]+', '_', clean)
    # Remove consecutive underscores
    clean = re.sub(r'_+', '_', clean)
    # Remove leading/trailing underscores
    clean = clean.strip('_')
    return clean

def extract_units_from_markdown(content):
    """Extract all units from the formatted Markdown study guide."""
    units = []
    
    # Match unit headers in the format: "## Unit X: Title" or "## Unit X: Title"
    unit_pattern = r'##\s+Unit\s+(\d+):?\s+([^\n]+)'
    unit_matches = list(re.finditer(unit_pattern, content))
    
    for i, match in enumerate(unit_matches):
        unit_number = int(match.group(1))
        title = match.group(2).strip()
        
        # Get content until next unit or end of file
        start_pos = match.end()
        end_pos = unit_matches[i+1].start() if i+1 < len(unit_matches) else len(content)
        unit_content = content[start_pos:end_pos].strip()
        
        # Process unit content
        unit = {
            "unit_number": unit_number,
            "title": title,
            "summary": "",
            "key_takeaways": [],
            "questions": []
        }
        
        # Extract summary section
        summary_match = re.search(r'###\s+Summary\s*\n(.*?)(?=###|$)', unit_content, re.DOTALL)
        if summary_match:
            summary_text = summary_match.group(1).strip()
            # Clean up bullet points
            summary_text = re.sub(r'^[\s-]*\*\*([^:]+):\*\*', r'\1:', summary_text, flags=re.MULTILINE)
            unit["summary"] = summary_text
        
        # Extract key takeaways from the summary
        # Many units have key points formatted with bullet points and bold headers
        takeaways = []
        bullet_points = re.finditer(r'^[\s-]*\*\*([^:]+):\*\*\s*(.*?)$', summary_text, re.MULTILINE)
        for bullet in bullet_points:
            takeaway = f"{bullet.group(1)}: {bullet.group(2).strip()}"
            takeaways.append(takeaway)
        
        if takeaways:
            unit["key_takeaways"] = takeaways
        
        # Extract questions 
        questions_match = re.search(r'###\s+Study Questions.*?\n(.*?)(?=$)', unit_content, re.DOTALL)
        if questions_match:
            questions_text = questions_match.group(1).strip()
            
            # Find individual questions using the numbered format: "1. **Question text**"
            question_pattern = r'(\d+)\.\s+\*\*([^\*]+)\*\*\s*(.*?)(?=\d+\.\s+\*\*|$)'
            question_matches = re.finditer(question_pattern, questions_text, re.DOTALL)
            
            for q_match in question_matches:
                q_num = q_match.group(1)
                q_text = q_match.group(2).strip()
                q_content = q_match.group(3).strip()
                
                # Extract options - they're formatted as "- A) Option text"
                options = []
                option_pattern = r'[-\s]*([A-E])\)\s+(.*?)(?=\n\s*[-\s]*[A-E]\)|$)'
                option_matches = re.finditer(option_pattern, q_content, re.DOTALL)
                
                for opt_match in option_matches:
                    opt_id = opt_match.group(1)
                    opt_text = opt_match.group(2).strip()
                    options.append({"id": opt_id, "text": opt_text})
                
                # Extract answer - it's formatted as "**Answer: X**"
                answer = None
                answer_match = re.search(r'\*\*Answer:\s*([A-E])\*\*', q_content)
                if answer_match:
                    answer = answer_match.group(1)
                
                if q_text and options and answer:
                    unit["questions"].append({
                        "question": q_text,
                        "options": options,
                        "answer": answer,
                        "explanation": ""
                    })
        
        units.append(unit)
    
    return units

def generate_txt_content(unit):
    """Generate a readable text version of the unit."""
    txt = f"UNIT {unit['unit_number']}: {unit['title']}\n"
    txt += "=" * 50 + "\n\n"
    
    txt += "SUMMARY:\n"
    txt += unit['summary'] + "\n\n"
    
    if unit['key_takeaways']:
        txt += "KEY TAKEAWAYS:\n"
        for i, takeaway in enumerate(unit['key_takeaways'], 1):
            txt += f"  {i}. {takeaway}\n"
        txt += "\n"
    
    txt += "QUESTIONS:\n"
    for i, q in enumerate(unit['questions'], 1):
        txt += f"{i}. {q['question']}\n"
        for option in q['options']:
            txt += f"   {option['id']}) {option['text']}\n"
        if q['answer']:
            txt += f"   Answer: {q['answer']}\n\n"
        else:
            txt += "   Answer: Not specified\n\n"
    
    return txt

def create_unit_files(unit, guide_path):
    """Create JSON and TXT files for a unit."""
    # Create directory name using the cleaned title
    clean_title = clean_title_for_filename(unit['title'])
    unit_dir_name = f"unit_{unit['unit_number']:02d}__{clean_title}"
    unit_dir_path = os.path.join(guide_path, unit_dir_name)
    
    # Create directory if it doesn't exist
    os.makedirs(unit_dir_path, exist_ok=True)
    
    # Create file paths
    json_file_path = os.path.join(unit_dir_path, f"{unit_dir_name}.json")
    txt_file_path = os.path.join(unit_dir_path, f"{unit_dir_name}.txt")
    
    # Write JSON file
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(unit, f, indent=2, ensure_ascii=False)
    
    # Write TXT file
    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.write(generate_txt_content(unit))
    
    return unit_dir_path

def main():
    """Main function to process the study guide."""
    if len(sys.argv) > 1:
        study_guide_path = sys.argv[1]
    else:
        study_guide_path = input("Enter the full path to the formatted study guide file: ")
    
    if not os.path.exists(study_guide_path):
        print(f"Error: File {study_guide_path} does not exist.")
        return
    
    # Read the formatted study guide
    with open(study_guide_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define guide path
    guide_path = os.path.join(QUIZ_ROOT, GUIDE_NAME)
    os.makedirs(guide_path, exist_ok=True)
    
    # Extract units
    units = extract_units_from_markdown(content)
    
    # Save each unit
    created_dirs = []
    for unit in units:
        if unit['summary'] or unit['questions']:
            unit_dir = create_unit_files(unit, guide_path)
            created_dirs.append(unit_dir)
            print(f"Created Unit {unit['unit_number']}: {unit['title']} with {len(unit['questions'])} questions")
        else:
            print(f"Warning: Unit {unit['unit_number']} has no content. Skipping.")
    
    print(f"\nSuccessfully processed {len(units)} units.")
    print(f"Created {len(created_dirs)} unit directories.")

if __name__ == "__main__":
    main()