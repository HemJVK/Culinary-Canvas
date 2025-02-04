from typing import Union, List, Dict, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from dataclasses import dataclass
import os
from secret_key import API_KEY as api_key
# from dashboard import api_key

@dataclass
class MenuResponse:
    """Data class to hold the structured menu response."""
    cuisine: str
    restaurant_name: str
    menu: str
    parsed_menu: List[Tuple[str, List[str]]]

class RestaurantMenuGenerator:
    """A class to generate restaurant names and menus using Google's Generative AI."""
    def __init__(self, key: str):
      self.llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=key)


    def _create_chains(self) -> Tuple[PromptTemplate, PromptTemplate]:
        """Create the prompt templates for name and menu generation."""
        name_template = PromptTemplate(
            input_variables=['cuisine', 'diet'],
            template="You are a world-class chef. I want to open a restaurant that serves {cuisine} "
                    "food for this {diet}. Suggest only one fancy name for this. Just the name."
        )

        menu_template = PromptTemplate(
            input_variables=['restaurant_name', 'cuisine', 'diet', 'no_of_items'],
            template="""
Based on the restaurant name '{restaurant_name}' and serving {cuisine} cuisine, 
create a menu with strictly {diet} options only.

Format the menu as follows:

**Appetizers**
{no_of_items} items
* Item Name: (dietary info)
  Detailed description of the item

**Main Courses**
{no_of_items} items
* Item Name: (dietary info)
  Detailed description of the item

**Desserts**
{no_of_items} items
* Item Name: (dietary info)
  Detailed description of the item

Make the menu diverse and appealing to the specified cuisine and dietary restrictions.
Include clear dietary information (e.g., Nut-free, Gluten-Free) for each item.
Follow the format strictly and consistently.
"""
        )

        return name_template, menu_template

    def generate_menu(self, 
                     cuisine: str, 
                     diets: Union[str, List[str]], 
                     no_of_items: int = 3) -> MenuResponse:
        """
        Generate a restaurant name and menu based on specified parameters.

        Args:
            cuisine (str): Type of cuisine (e.g., "Mexican", "Italian")
            diets (Union[str, List[str]]): Dietary restrictions
            no_of_items (int, optional): Number of items per section. Defaults to 3

        Returns:
            MenuResponse: Structured response containing restaurant details

        Raises:
            ValueError: If input parameters are invalid
            Exception: For other errors during generation
        """
        # Input validation
        if not cuisine or not isinstance(cuisine, str):
            raise ValueError("Cuisine must be a non-empty string")
        if not diets:
            raise ValueError("Diets must be specified")
        if no_of_items < 1:
            raise ValueError("Number of items must be positive")

        # Convert diets list to string if necessary
        if isinstance(diets, list):
            diets = ", ".join(diets)

        try:
            name_template, menu_template = self._create_chains()
            
            # Create chains
            name_chain = LLMChain(llm=self.llm, prompt=name_template, output_key='restaurant_name')
            menu_chain = LLMChain(llm=self.llm, prompt=menu_template, output_key='menu')

            # Combine chains
            chain = SequentialChain(
                chains=[name_chain, menu_chain],
                input_variables=['cuisine', 'diet', 'no_of_items'],
                output_variables=['restaurant_name', 'menu']
            )

            # Generate response
            response = chain({
                'cuisine': cuisine,
                'diet': diets,
                'no_of_items': no_of_items
            })

            # Parse the menu
            parsed_menu = self.parse_menu(response['menu'])

            return MenuResponse(
                cuisine=cuisine,
                restaurant_name=response['restaurant_name'].strip(),
                menu=response['menu'].strip(),
                parsed_menu=parsed_menu
            )

        except Exception as e:
            raise

    @staticmethod
    def parse_menu(menu_string: str) -> List[Tuple[str, List[str]]]:
        """
        Parse the generated menu string into a structured format.

        Args:
            menu_string (str): The raw menu string to parse

        Returns:
            List[Tuple[str, List[str]]]: List of (section_heading, items) tuples

        Raises:
            ValueError: If menu string is invalid or empty
        """
        if not menu_string:
            raise ValueError("Menu string cannot be empty")

        sections = menu_string.strip().split('\n\n')
        parsed_menu = []

        for section in sections:
            lines = section.strip().split('\n')
            
            # Extract heading
            if not lines or not lines[0].strip():
                continue
                
            heading = lines[0].strip("* ")
            if heading.startswith("**") and heading.endswith("**"):
                heading = heading[2:-2].strip()
            
            # Process items
            items = []
            current_item = []
            
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("*"):
                    if current_item:
                        items.append("\n".join(current_item))
                        current_item = []
                    current_item.append(line.lstrip("* "))
                elif line:
                    current_item.append(line)
            
            if current_item:
                items.append("\n".join(current_item))
            
            if heading and items:
                parsed_menu.append((heading, items))

        return parsed_menu


if __name__ == "__main__":
    try:
        # Example usage
        generator = RestaurantMenuGenerator(key=api_key)
        response = generator.generate_menu(
            cuisine="Mexican",
            diets=["vegetarian"],
            no_of_items=3
        )
        
        print(f"Restaurant Name: {response.restaurant_name}\n")
        print("Menu Sections:")
        for section, items in response.parsed_menu:
            print(f"\n{section}:")
            for item in items:
                print(f"- {item}")
                
    except Exception as e:
        raise