import streamlit as st

### PAGE CONFIGURATION ###
# set the page / tab title
st.set_page_config(page_title="GPTour")

# set the header
st.header("GPTour Chat")

### LOGGING ###
import logging
log = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s: %(message)s",
    )
log.info("Logger configured")

import json

def pretty_print_dict(dictionary):
    # Use json.dumps with indent for pretty printing
    return json.dumps(dictionary, indent=4)


### AI ASSISTANT CODE ###
def assistant(prompt: str, context: str = "You are a helpful assistant.") -> str:
    return "Not Programmed Yet!"

context = ""

### AI ASSISTANT CODE ###


### WEBSITE CODE ###
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = assistant(prompt, context)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
### WEBSITE CODE ###








#####################

# import streamlit as st
# import random

# def get_country_info(country):
#     # In a real application, you might fetch country information from a database or an API
#     # For simplicity, I'll use a dictionary with some sample data
#     country_info = {
#         "USA": "The United States of America is a country located in North America.",
#         "UK": "The United Kingdom is a country located off the northwestern coast of mainland Europe.",
#         "Canada": "Canada is a country in North America, known for its friendly people and beautiful landscapes.",
#         # Add more countries and their information as needed
#     }

#     return country_info.get(country, "Country information not available.")

# def main():
#     st.title("Country Information App")

#     # Ask the user for their preference via a chat-like interface
#     user_choice = st.text_input("Which country would you like to learn about? (Type a country name)")

#     if user_choice:
#         # Display information based on the user's choice
#         country_info = get_country_info(user_choice)
#         st.markdown(f"**Information about {user_choice}:**")
#         st.write(country_info)
#     else:
#         # If the user hasn't entered a choice, provide an option to pick a country at random
#         random_country_button = st.button("Pick a Country at Random")
#         if random_country_button:
#             # Generate a random country
#             random_country = random.choice(list(get_country_info.keys()))
#             st.markdown(f"**Information about a Random Country ({random_country}):**")
#             st.write(get_country_info(random_country))

# if __name__ == "__main__":
#     main()
