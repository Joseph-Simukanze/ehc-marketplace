from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import spacy
import json

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Render chatbot UI
def chatbot_ui(request):
    # Initialize session for conversation history
    if 'conversation' not in request.session:
        request.session['conversation'] = []
    return render(request, 'chatbot/chat.html')

# Handle bot response logic
@csrf_exempt
def bot_response(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    message = request.GET.get('message', '').lower().strip()
    if not message:
        return JsonResponse({'response': 'Please send a message.'}, status=400)

    # Process message with spaCy
    doc = nlp(message)
    
    # Extract intents and entities
    intents = detect_intent(doc)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Get conversation history from session
    conversation = request.session.get('conversation', [])
    conversation.append({'user': message, 'bot': ''})  # Placeholder for bot response

    # Response logic based on intents
    reply = generate_response(request, intents, entities, message)

    # Update conversation history
    conversation[-1]['bot'] = reply
    request.session['conversation'] = conversation[-10:]  # Keep last 10 exchanges
    request.session.modified = True

    return JsonResponse({'response': reply})


    return JsonResponse({'response': reply})

def detect_intent(doc):
    """Detect intents based on message content."""
    intents = []
    message = doc.text.lower()

    # Keyword-based intent detection
    if any(word in message for word in ["hello", "hi", "muli bwanji", "shani"]):
        intents.append("greeting")
    if "product" in message:
        intents.append("product_inquiry")
    if any(word in message for word in ["payment", "kulipila"]):
        intents.append("payment_inquiry")
    if any(word in message for word in ["bye", "goodbye"]):
        intents.append("farewell")
    
    # Entity-based intent detection
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "MONEY"]:
            intents.append("product_inquiry" if ent.label_ == "PRODUCT" else "payment_inquiry")

    return intents if intents else ["unknown"]
from datetime import datetime
import re
from chatbot.utils import search_products_by_query  # Ensure this works with your project
from chatbot.chat_helpers import handle_chat_message  # If you keep handle_chat_message separate

def generate_response(request, intents, entities, message):
    """Generate a response based on intents, entities, and conversation context for EHC Marketplace."""
    # Retrieve and trim conversation history
    conversation = request.session.get('conversation', [])[-10:]
    response_message = None

    # Check for non-English input
    non_english_keywords = ['muli', 'bwino', 'chifukwa', 'ndine', 'mukufuna']
    if any(keyword in message.lower() for keyword in non_english_keywords):
        response_message = "Please use English to ask about the EHC Marketplace. How can I help you today?"

    # Process known intents
    if not response_message:
        for intent in intents:
            if intent == "greeting":
                response_message = "Hi there! Welcome to the EHC Marketplace. How can I assist you with buying or selling today? 😊"
                break
            elif intent == "product_inquiry":
                if 'category' in entities:
                    category = entities['category'].capitalize()
                    response_message = f"Looking for {category}? Browse our {category} section on the home page or ask for specific items!"
                else:
                    response_message = "You can find all products on our home page. Want to explore Electronics, Books, Clothing, or something else?"
                break
            elif intent == "payment_inquiry":
                if 'payment_method' in entities:
                    method = entities['payment_method'].capitalize()
                    response_message = f"We support {method} for secure payments. Would you like help with the payment process?"
                else:
                    response_message = "We offer Cash, MTN, Airtel, and Payment on Delivery. Which payment method are you interested in?"
                break
            elif intent == "subscription_inquiry":
                response_message = "To sell items, you need a subscription. Visit the 'Subscribe' page to start selling for a small monthly fee!"
                break
            elif intent == "delivery_inquiry":
                response_message = "We provide delivery with location tracking and reasonable fees. Want details on delivery for a specific item?"
                break
            elif intent == "account_inquiry":
                response_message = "Need help with your account? You can register, log in, or manage your profile on the EHC Marketplace website."
                break
            elif intent == "category_inquiry":
                response_message = "We have categories like Electronics, Books, Clothing, Furniture, and more. Which category are you interested in?"
                break
            elif intent == "offer_inquiry":
                response_message = "Check out our latest offers, like discounts on Electronics or free shipping! Visit the home page for current deals."
                break
            elif intent == "farewell":
                response_message = "Thanks for chatting! Visit the EHC Marketplace anytime to buy or sell. 👋"
                break

    # Fallback: Try product-based lookup if message may refer to a product
    if not response_message:
        # Try to interpret message as a product search
        product_matches = search_products_by_query(message)
        if product_matches.exists():
            product_lines = "\n".join(f"{p.title} - ZMW {p.price}" for p in product_matches[:5])
            response_message = f"Here are some products that match your search:\n{product_lines}"
        else:
            # Check conversation context to offer better suggestions
            recent_context = " ".join(msg['user'].lower() for msg in conversation[-5:])
            if any(word in recent_context for word in ['product', 'item', 'buy', 'sell']):
                response_message = "Still exploring products? Try browsing our categories or ask about a specific item!"
            elif any(word in recent_context for word in ['payment', 'pay', 'cash', 'mtn', 'airtel']):
                response_message = "Need more info on payments? We support Cash, MTN, Airtel, and Payment on Delivery. What's your question?"
            elif any(word in recent_context for word in ['subscription', 'subscribe', 'sell']):
                response_message = "Interested in selling? Get a subscription on our 'Subscribe' page to list your items!"
            elif any(word in recent_context for word in ['delivery', 'shipping', 'location']):
                response_message = "Curious about delivery? We offer tracking and affordable fees. Ask for more details!"
            else:
                response_message = f"Sorry, I couldn't find anything related to '{message}'. Try asking about products, payments, subscriptions, or delivery!"

    # Store conversation
    conversation.append({
        'user': message,
        'bot': response_message,
        'timestamp': datetime.now().isoformat()
    })
    request.session['conversation'] = conversation

    return response_message

   
