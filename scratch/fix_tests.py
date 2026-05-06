import os
import re

tests_dir = "testsprite_tests"

# Pattern to match: assert await frame.locator(...).nth(0).is_visible(), "..."
# We want to keep everything from assert to the closing quote of the error message string,
# and remove anything after that.
# Some strings end with ', so we'll match up to the last quote.
# Sometimes it's like: assert await frame.locator("xpath=//*[contains(., 'Cà phê')]").nth(0).is_visible(), "The AI answer should mention Cà phê as a knowledge-based response to the question.",
# We want to remove the trailing comma.

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    changed = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("assert await frame.locator"):
            # Use regex to extract the valid part of the assert statement
            # It usually ends with a string literal like "some message"
            match = re.match(r'^(\s*assert await frame\.locator\(.*?\)\.nth\(0\)\.is_visible\(\),\s*".*?")', line)
            if match:
                new_line = match.group(1) + "\n"
                if lines[i] != new_line:
                    lines[i] = new_line
                    changed = True
                    
    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Fixed {filepath}")

for filename in os.listdir(tests_dir):
    if filename.endswith(".py") and filename.startswith("TC"):
        fix_file(os.path.join(tests_dir, filename))
