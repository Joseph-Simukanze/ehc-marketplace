import re
from chatbot.utils import search_products_by_query


def handle_chat_message(message):
    """
    Basic chatbot logic to respond to product-related queries
    such as price, availability, and product name.

    Args:
        message (str): User's input message.

    Returns:
        str: Chatbot response.
    """

    # Normalize the message
    message = message.lower()

    # Check if user is asking about price
    if "price" in message or "cost" in message:
        products = search_products_by_query(message)
        if products.exists():
            response = "Here are some prices I found:\n"
            response += "\n".join(f"{p.title} - ZMW {p.price}" for p in products)
        else:
            response = "Sorry, I couldn't find that product. Try another name."
        return response

    # Check for availability query
    elif "available" in message or "have" in message:
        products = search_products_by_query(message)
        if products.exists():
            response = "Yes, we have:\n" + "\n".join(p.title for p in products)
        else:
            response = "We don't seem to have that item at the moment."
        return response

    # General fallback product match
    products = search_products_by_query(message)
    if products.exists():
        response = "Here’s what I found:\n"
        response += "\n".join(f"{p.title} - ZMW {p.price}" for p in products)
        return response

    return "I'm not sure how to help with that. Try asking about product prices or availability!"
