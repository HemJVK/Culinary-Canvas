# menu_utils.py

from typing import Dict, List

def MenuParser():
    class MenuParser:
        def parse_menu(self, menu_text: str) -> Dict[str, List[Dict[str, str]]]:
            """Parses the menu text and extracts item names, descriptions, and dietary info."""
            sections = {}
            current_section = None

            for line in menu_text.splitlines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith("**") and line.endswith("**"):
                    # This is a section header
                    current_section = line[2:-2].strip()
                    sections[current_section] = []

                elif line.startswith("*"):
                    # This is a menu item line
                    parts = line[1:].split(":", 1)  # Split only at the first ":"
                    if len(parts) == 2:
                        item_name = parts[0].strip()
                        description_with_dietary = parts[1].strip()

                        # Further split the description and dietary info
                        description_parts = description_with_dietary.split("(", 1)
                        description = description_parts[0].strip()

                        dietary = []
                        if len(description_parts) > 1:
                            dietary_str = description_parts[1].replace(")", "").strip()
                            dietary = [d.strip() for d in dietary_str.split(",")]

                        if current_section:
                            sections[current_section].append({
                                "name": item_name,
                                "description": description,
                                "dietary": dietary,
                            })

            return sections
    return MenuParser()

def format_menu_for_display(parsed_menu: Dict[str, List[Dict[str, str]]]) -> str:
    """Formats the parsed menu into a readable string."""
    menu_text = ""
    for section, items in parsed_menu.items():
        menu_text += f"**{section}**\n\n"
        for item in items:
            dietary_info = f" ({', '.join(item['dietary'])})" if item['dietary'] else ""
            menu_text += f"* {item['name']}{dietary_info}\n"
            if item['description']:
                menu_text += f"  {item['description']}\n"
        menu_text += "\n"
    return menu_text