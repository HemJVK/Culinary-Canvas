# menu_utils.py
from typing import List, Tuple, Dict
import re

class MenuParser:
    """Handles parsing and cleaning of menu text."""
    
    @staticmethod
    def clean_item(item: str) -> Tuple[str, str, List[str]]:
        """
        Clean a menu item and extract its components.
        
        Returns:
            Tuple[str, str, List[str]]: (name, description, dietary_info)
        """
        # Remove extra asterisks and emojis
        item = re.sub(r'\*{2}|🍽️|\* ', '', item).strip()
        
        # Split into name/description
        parts = item.split(':', 1)
        if len(parts) != 2:
            return item, "", []
            
        name, description = parts
        
        # Extract dietary info
        dietary_info = []
        if '(' in name and ')' in name:
            name_parts = name.split('(')
            name = name_parts[0].strip()
            dietary_info = [
                restriction.strip() 
                for restriction in name_parts[1].replace(')', '').split(',')
            ]
            
        return name, description.strip(), dietary_info

    @staticmethod
    def validate_dietary_restrictions(name: str, description: str, restrictions: List[str]) -> List[str]:
        """Validate and correct dietary restrictions based on item description."""
        validated = restrictions.copy()
        
        # Common validation rules
        if 'Vegan' in validated:
            if any(ingredient in description.lower() for ingredient in 
                  ['cheese', 'honey', 'milk', 'cream', 'yogurt']):
                validated.remove('Vegan')
                if 'Vegetarian' not in validated:
                    validated.append('Vegetarian')
                    
        if 'Gluten-Free' in validated:
            if any(ingredient in description.lower() for ingredient in 
                  ['pita', 'bread', 'filo', 'phyllo', 'pasta']):
                validated.remove('Gluten-Free')
                
        if 'Nut-Free' in validated:
            if any(ingredient in description.lower() for ingredient in 
                  ['almond', 'walnut', 'pecan', 'pine nut', 'pistachio']):
                validated.remove('Nut-Free')
                
        return validated

    @staticmethod
    def parse_menu(menu_text: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse the menu text into structured sections with items.
        
        Returns:
            Dict[str, List[Dict[str, str]]]: Structured menu data
        """
        menu_lines = menu_text.strip().split('\n')
        current_section = None
        sections = {
            'Appetizers': [],
            'Main Courses': [],
            'Desserts': []
        }

        section_pattern = re.compile(r'\*{0,2}(Appetizers|Main Courses|Desserts)\*{0,2}')
        
        for line in menu_lines:
            line = line.strip()
            if not line:
                continue

            # Check for section headers
            section_match = section_pattern.match(line)
            if section_match:
                current_section = section_match.group(1)
                continue

            # Skip if we're not in a valid section
            if not current_section or current_section not in sections:
                continue

            # Process menu items
            if ':' in line:  # Only process lines that look like menu items
                name, description, dietary = MenuParser.clean_item(line)
                if name:
                    validated_dietary = MenuParser.validate_dietary_restrictions(
                        name, description, dietary
                    )
                    sections[current_section].append({
                        'name': name,
                        'description': description,
                        'dietary': validated_dietary
                    })

        return sections

def format_menu_for_display(menu_data: Dict[str, List[Dict[str, str]]]) -> str:
    """Format menu data into a properly structured markdown string."""
    markdown_lines = []
    
    for section, items in menu_data.items():
        if items:  # Only show sections that have items
            markdown_lines.append(f"### {section}\n")
            
            for item in items:
                dietary_info = f" ({', '.join(item['dietary'])})" if item['dietary'] else ""
                markdown_lines.append(f"#### 🍽️ {item['name']}{dietary_info}")
                if item['description']:
                    markdown_lines.append(f"*{item['description']}*\n")
            
            markdown_lines.append("---\n")
    
    return "\n".join(markdown_lines)

# Example usage:
if __name__ == "__main__":
    sample_menu = """
    **Appetizers**
    Mediterranean Hummus (Vegan, Gluten-Free): Creamy hummus made with chickpeas, tahini, lemon juice, and garlic, served with warm pita bread.
    Falafel Bites (Vegan, Gluten-Free): Crispy falafel balls made from chickpeas, herbs, and spices, served with a tahini dipping sauce.
    
    **Main Courses**
    Vegetable Moussaka (Vegan, Gluten-Free): Layers of eggplant, zucchini, potatoes, and tomatoes topped with a creamy vegan béchamel sauce.
    
    **Desserts**
    Baklava (Vegan, Nut-Free): Sweet pastry made with layers of filo dough, nuts (optional), and a honey-based syrup.
    """
    
    parser = MenuParser()
    parsed_menu = parser.parse_menu(sample_menu)
    formatted_menu = format_menu_for_display(parsed_menu)
    print(formatted_menu)


