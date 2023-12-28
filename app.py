import streamlit as st

### PAGE CONFIGURATION ###
# set the page / tab title
st.set_page_config(page_title="GPTour")

# set the header
st.header("GPTour Chat")

### IMPORTS ###
from typing import Optional
import random

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


### CONFIG TOML ###
# access toml configuration
import toml
config = toml.load(".streamlit/config.toml")

### OpenAI's ChatGPT API ###
import os
import openai

openai_client = openai.OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)

def chatgpt(prompt: str, context: str = "You are a helpful assistant.", model: str = "gpt-3.5-turbo") -> str:
    response = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": context,
            },
             {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    return response.choices[0].message.content

### CUSTOM ASSISTANT CODE ###
def identify_user(prompt: str) -> Optional[str]:
    """
    Identifies the user
    """
    context = (
        "Instruction: given the prompt, your goal is to extract the first name of the user. "
        "Only return the name. If you can't determine it, please return with 'undetermined'. "
        "Example: if the prompt is 'my name is Mary', answer with 'Mary'. "
        "Example: if the prompt is 'my friends call me jake', answer with 'Jake'. "
        "Example: if the prompt is 'i like beaches and sunset', answer with 'undetermined' as there's no name mentioned."
    )

    result = chatgpt(prompt, context)

    try:
        user_name = result.strip().lower() # clean the results
        assert user_name != "undetermined" # make sure it's not undetermined

        user_name = user_name[0].upper() + user_name[1:] # capitalize first letter
        return user_name
    except Exception as e:
        log.info(f"Couldn't parse prompt = {prompt} for name. Found error: {e}")


def assistant(prompt: str, context: str = "You are a helpful assistant.") -> str:
    return "Not Programmed Yet!"

context = ""




### WEBSITE CODE ###
# session variables
if "user_name" not in st.session_state: st.session_state.user_name = None

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "assistant", 
        "content": (
            "Hello, I'm GPTour and I'm here to help with your travels. "
            "Before we begin, what is your name?"
            )
    }]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=config["custom"][f"{message['role']}_avatar"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=config["custom"]["user_avatar"]):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=config["custom"]["assistant_avatar"]):
        with st.spinner("Thinking..."):
            if not st.session_state.user_name:
                # first identify for the user's names
                user_name = identify_user(prompt)

                # update session name
                if not st.session_state.user_name and user_name:
                    st.session_state.user_name = user_name

                # update response based on whether the name is found
                if not st.session_state.user_name:
                    possible_name_follow_ups = [
                        "I'm sorry but I couldn't catch your name - could you please share with me?",
                        "I couldn't catch your name - I'd love to know how to refer to you doing our conversation.",
                        "Before we begin, it would be helpful to have your name."
                        "I'm excited to help you with your travels! Before we start, it would be helpful for me to have your name!"
                    ]
                    response = random.choice(possible_name_follow_ups)
                else:
                    response = (
                        f"Welcome {st.session_state.user_name}! I'm here to help you with your travels! ✈️ 🏨 🧳\n\n"
                        "What country would be interested in learning more about? "
                        "If you're unsure or curious, I can recommend a country for your travels! "
                    )
            else:
                response = assistant(prompt, context)
            
            st.write(response)
    
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)









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
