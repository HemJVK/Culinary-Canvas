import subprocess
import streamlit as st
from typing import Dict, Any
import logging
import base64
from menu_generator import RestaurantMenuGenerator
from secret_key import API_KEY as api_key
from menu_utils import MenuParser, format_menu_for_display
import os

# Set page configuration
st.set_page_config(
    page_title="Culinary Canvas",
    page_icon="🍽️",
    layout="wide"
)

if api_key:
    print("API Key found.")

# Function to set background image
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    css_code = f"""
    <style>
    .stApp {{
        background-image: url(data:image/png;base64,{encoded_string});
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)

# Path to your background image
image_path = "image.png"  # Replace with your local image path
set_background(image_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'generator' not in st.session_state:
        try:
            st.session_state.generator = RestaurantMenuGenerator(key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize generator: {str(e)}")
            st.error("Failed to initialize the menu generator. Please check your API key.")
            return False
    if 'last_menu' not in st.session_state:
        st.session_state.last_menu = None
    return True

def create_sidebar() -> Dict[str, Any]:
    """Create and return sidebar inputs."""
    with st.sidebar:
        st.title("Menu Options")
        with st.form(key='menu_form'):
            cuisine = st.selectbox(
                "Select Cuisine (Required)",
                options=["", "Indian", "Italian", "Mexican", "Chinese", "Japanese", 
                         "Thai", "American", "Mediterranean", "French", "Spanish"],
                format_func=lambda x: "Select a Cuisine" if x == "" else x,
                key="cuisine_select"
            )
            diet_options = st.multiselect(
                "Select Dietary Requirements (Required)",
                options=["Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free", 
                         "Dairy-Free", "Nut-Free"],
                key="diet_multi_select"
            )
            items_per_section = st.slider(
                "Number of Items per Section",
                min_value=1,
                max_value=5,
                value=3,
                key="items_per_section_slider"
            )
            generate_button = st.form_submit_button(
                "Generate Menu", 
            )
        return {
            "cuisine": cuisine,
            "diet_options": diet_options,
            "items_per_section": items_per_section,
            "generate_button": generate_button
        }


def display_menu(menu_response):
    """
    Display the generated menu with proper formatting and styling.
    Args:
        menu_response: MenuResponse object containing restaurant name and menu.
    """
    st.title(f"🏺 {menu_response.restaurant_name}")
    st.markdown("---")
    parser = MenuParser()
    try:
        parsed_menu = parser.parse_menu(menu_response.menu)
        for section, items in parsed_menu.items():
            st.markdown(f"### {section}")
            for item in items:
                dietary_info = f" ({', '.join(item['dietary'])})" if item['dietary'] else ""
                st.markdown(f"#### 🍽️ {item['name']}{dietary_info}")
                if item['description']:
                    st.markdown(f"*{item['description']}*")
                st.markdown("---")

        menu_text = format_menu_for_display(parsed_menu)
        st.download_button(
            label="📥 Download Menu",
            data=menu_text,
            file_name=f"{menu_response.restaurant_name.lower().replace(' ', '_')}_menu.txt",
            mime="text/plain"
        )

    except Exception as e:
        logger.error(f"Error parsing menu: {str(e)}")
        st.error("Failed to display the menu. Please check the generated menu text")


def main():
    """Main application function."""
    if not initialize_session_state():
        return
    st.title("🎪 Restaurant Menu Generator")
    st.markdown("---")
    inputs = create_sidebar()
    if not (inputs["cuisine"] and inputs["diet_options"]):
      st.warning("⚠️ Please select a cuisine and at least one dietary requirement.")
    if inputs["generate_button"]:
        with st.spinner("Generating your restaurant menu..."):
            try:
                menu_response = st.session_state.generator.generate_menu(
                    cuisine=inputs["cuisine"],
                    diets=inputs["diet_options"],
                    no_of_items=inputs["items_per_section"]
                )
                st.session_state.last_menu = menu_response
                display_menu(menu_response)
            except Exception as e:
                logger.error(f"Error generating menu: {str(e)}")
                st.error("Failed to generate menu. Please check your API key.")
    elif st.session_state.last_menu:
            display_menu(st.session_state.last_menu)


if __name__ == "__main__":
    main()