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

### OpenAI's ChatGPT and DALLE API ###
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

def dalle(prompt: str) -> str:
    response = openai_client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="256x256",
        quality="standard",
        n=1,
    )
    return response.data[0].url

### CUSTOM ASSISTANT CODE ###
import travel_data

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


def identify_country(prompt):
    # identify the country if there is one
    identify_country_instruction = (
        "Given the prompt, identify what country the user is asking about. "
        "Answer only with the country identified. "
        "If there's no country that can be determined, answer with 'none'. "
        "For example, if the prompt is 'i want to learn more about china', answer with 'china'. "
        "For example, if the prompt is 'what are some hotels', answer with 'none'"
    )
    identified_country = chatgpt(prompt, identify_country_instruction).strip().lower()

    if identified_country == 'none':
        return None
    if identified_country not in travel_data.countries:
        return "not supported"
    return identified_country

def assistant(prompt: str) -> str:
    """
    Personalized response based on the prompt
    """
    instructions = (
        "Given the prompt, identify if the user wants to learn about hotels, restaurants, or sightseeing. "
        "Only answer with 'hotels', 'restaurants', 'sightseeing', or 'other'. "
        "Example: prompt is 'what are some hotels', answer is 'hotel'. "
        "Example: prompt is 'tell me some history', answer is 'other'. "
    )
    for _ in range(3):
        results = chatgpt(prompt, instructions).lower().strip()
        if results in ["hotels", "restaurants", "sightseeing", "other"]:
            break
    else:
        results = "other"

    if results == "other":
        context = (
            f"You're a friendly travel agent working with a person named {st.session_state.user_name}. "
            f"Answer the user's question. They are planning to travel to {st.session_state.country}. "
            f"Keep the answer conversational and informal in style and avoid very long answers (max 200 words)."
            f"Make sure to refer to the person by their name, {st.session_state.user_name}, and related your answer to {st.session_state.country}. "
            "For non-travel or related questions, please don't answer. Respond with 'I can only answer travel-related questions'"
            "Thank you!"
        )
        return chatgpt(prompt, context), dalle(f"give an image of {st.session_state.country} related to {prompt}")
    
    if results == "hotels":
        _data = travel_data.list_of_hotels
        response = "Here are some popular hotels 🏨: "
    if results == "restaurants":
        _data = travel_data.list_of_restaurants
        response = "Here are some popular restaurants 🍜 🍝 🍮: "
    if results == "sightseeing":
        _data = travel_data.list_of_places
        response = "Here are some popular sights to see 🗺: "

    _data_content = random.sample(_data[st.session_state.country], 5)
    for i in _data_content:
        name, desc, address = i
        response += f"\n\n1. **{name}**: {desc}. The address is {address}"

    response += f"\n\nLet me know if you need more recommendations for {travel_data.countries_to_proper[st.session_state.country]}! I'm happy to help {st.session_state.user_name}!"

    return response, None

context = ""




### WEBSITE CODE ###
# session variables
if "user_name" not in st.session_state: st.session_state.user_name = None
if "country" not in st.session_state: st.session_state.country = None

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "assistant", 
        "images": [],
        "content": (
            "Hello, I'm GPTour and I'm here to help with your travels. "
            "Before we begin, what is your name?"
            )
    }]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=config["custom"][f"{message['role']}_avatar"]):
        st.write(message["content"])
        if message["images"] != []:
            for img in message["images"]:
                st.image(img)

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "images": [], "content": prompt})
    with st.chat_message("user", avatar=config["custom"]["user_avatar"]):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=config["custom"]["assistant_avatar"]):
        with st.spinner("Thinking..."):
            images = []
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
                if not st.session_state.country:
                    country = identify_country(prompt)

                    if country == "not supported":
                        response = "I'm sorry, but at the moment, I don't support or provide information on this country! The countries I can provide information are: Armenia, France, Italy, Spain, Germany, USA, UK, Brazil, Greece, Singapore, Australia, China, UAE, and Canada."
                    elif country and not st.session_state.country:
                        st.session_state.country = country
                        response = (
                            f"I would love give more information on {travel_data.countries_to_proper[st.session_state.country]} {travel_data.countries_to_emoji[st.session_state.country]}! "
                            f"\n\nI can give recommendations for sightseeing, hotels, and restaurants!"
                            f"\n\nHere's a picture of what traveling to {travel_data.countries_to_proper[st.session_state.country]} might entail:"
                        )
                        images.append(dalle(f"A beautiful, travel picture for {st.session_state.country}. Make it sunny and gorgeous please and feature an iconic landmark!"))
                    else:
                        response = "I couldn't catch which country you'd be interested in - could you share a country you are interest in? The countries I can provide information are: Armenia, France, Italy, Spain, Germany, USA, UK, Brazil, Greece, Singapore, Australia, China, UAE, and Canada."
                else:
                    response, image = assistant(prompt)
                    if image:
                        images.append(image)

            st.write(response)
            if images != []:
                for img in images:
                    st.image(img)
    
    message = {"role": "assistant", "images": images, "content": response}
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
