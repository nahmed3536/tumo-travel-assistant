import streamlit as st
import random

def get_country_info(country):
    # In a real application, you might fetch country information from a database or an API
    # For simplicity, I'll use a dictionary with some sample data
    country_info = {
        "USA": "The United States of America is a country located in North America.",
        "UK": "The United Kingdom is a country located off the northwestern coast of mainland Europe.",
        "Canada": "Canada is a country in North America, known for its friendly people and beautiful landscapes.",
        # Add more countries and their information as needed
    }

    return country_info.get(country, "Country information not available.")

def main():
    st.title("Country Information App")

    # Ask the user for their preference via a chat-like interface
    user_choice = st.text_input("Which country would you like to learn about? (Type a country name)")

    if user_choice:
        # Display information based on the user's choice
        country_info = get_country_info(user_choice)
        st.markdown(f"**Information about {user_choice}:**")
        st.write(country_info)
    else:
        # If the user hasn't entered a choice, provide an option to pick a country at random
        random_country_button = st.button("Pick a Country at Random")
        if random_country_button:
            # Generate a random country
            random_country = random.choice(list(get_country_info.keys()))
            st.markdown(f"**Information about a Random Country ({random_country}):**")
            st.write(get_country_info(random_country))

if __name__ == "__main__":
    main()
