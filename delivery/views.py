from django.core import serializers
import random
from .models import Product
from django.shortcuts import render
import joblib
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import re
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . models import Order, Product, CartItem, OrderItem, Feedback
from django.utils import timezone

@login_required(login_url='login')
def home(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if len(username) < 6:
            messages.error(request, "Username must be at least 6 characters long")
            return redirect('signup')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, "Invalid email address")
            return redirect('signup')

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken")
            return redirect('signup')

        user = User.objects.create_user(
            username=username, email=email, password=password1)
        user.save()
        return redirect('signup')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# Load the trained chatbot model
def load_chatbot_model(model_path='chatbot_model.pkl'):
    model = joblib.load(model_path)
    return model

# Load the intents file
def load_intents(intents_path='intents.json'):
    with open(intents_path) as file:
        intents = json.load(file)
    return intents


# Load the chatbot model and intents
chatbot_model = load_chatbot_model()
intents = load_intents()


def predict_intent(question):
    predicted_intent = chatbot_model.predict([question])[0]
    return predicted_intent


def get_response(intent):
    for i in intents['intents']:
        if i['tag'] == intent:
            return random.choice(i['responses'])


def product_catalog(request):
    products = Product.objects.filter(is_available=True)

    category = request.GET.get('category')
    if category and category != 'All Categories':
        products = products.filter(category=category)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(
            description__icontains=search_query)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_json = serializers.serialize('json', products)
        return JsonResponse({'products': products_json}, safe=False)

    context = {
        'products': products,
        'selected_category': category,
        'search_query': search_query,
    }

    return render(request, 'products.html', context)


def chatbot_response(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "GET":
        user_question = request.GET.get('question', '').strip().lower()

        # Define patterns
        patterns = {
            'price': r"(?:what(?:'s| is| was) the (?:price|cost) of|price of|cost of) (\w+)",
            'availability': r"is (\w+) available",
            'recommendations': r"(?:recommendations for|suggest some|advise on) ([\w\s]+)",
            'details': r"(?:tell me (?:more )?about|details about|information on) ([\w\s]+)",
            'latest': r"what (?:are the latest|is the latest|are the newest|are the most recent) ([\w\s]+)",
            'greeting': r"(hi|hello|hey)",
            'farewell': r"(bye|goodbye|see you)",
            'order_status': r"status of order #?(\d+)",
            'feedback': r"feedback:(.+)"
        }

        response_message = "Sorry, I couldn't understand your question. For any specific queries, please contact our customer support at 123-456-7890."

        # Process each pattern
        for intent, pattern in patterns.items():
            match = re.search(pattern, user_question)
            print(f"Intent: {intent}, Match: {match}")
            if match:
                if intent == 'greeting' or intent == 'farewell':
                    response_message = "Hello! How can I help you today?" if intent == 'greeting' else "Goodbye! Have a great day!"
                elif intent == 'order_status':
                    order_id = match.group(1)
                    response_message = get_order_status(order_id)
                elif intent == 'feedback':
                    feedback_content = match.group(1).strip()
                    save_feedback(feedback_content)
                    response_message = "Thank you for your feedback!"
                else:
                    product_name = match.group(1)
                    response_message = handle_query(intent, product_name)
                break

        return JsonResponse({'response': response_message})

    return JsonResponse({'response': "Invalid request"}, status=400)


def get_order_status(order_id):
    try:
        order = Order.objects.get(id=order_id)
        return f"Order #{order.id} is currently '{order.status}'."
    except Order.DoesNotExist:
        return "Order not found."

def save_feedback(content):
    # Assuming Feedback model has a 'content' field
    Feedback.objects.create(content=content)


def handle_query(intent, product_name):
    try:
        product = Product.objects.get(name__iexact=product_name)
        if intent == 'price':
            return f"The price of {product.name} is ${product.price}."
        elif intent == 'availability':
            return f"{product.name} is currently {'available' if product.available else 'not available'}."
        elif intent == 'details':
            return f"Here are some details about {product.name}: {product.description}"
        elif intent == 'recommendations':
            recommendations = Product.objects.filter(
                category=product.category).exclude(name__iexact=product_name)[:3]
            recommendations_list = ", ".join([p.name for p in recommendations])
            return f"Here are some recommendations in {product.category.name} category: {recommendations_list}"
        elif intent == 'latest':
            latest_products = Product.objects.order_by('-id')[:3]
            latest_list = ", ".join([p.name for p in latest_products])
            return f"The latest products in our catalog are: {latest_list}"
    except Product.DoesNotExist:
        return f"Sorry, I couldn't find any information about {product_name}."


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


@login_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    print("Product ID:", product_id)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect('product_catalog')

    cart_item = CartItem(
        user=request.user,
        product=product,
        product_name=product.name,
        price=product.price,
        image_url=product.image_url
    )
    cart_item.save()

    return redirect('product_catalog')



@login_required
def cart_view(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity'))

        try:
            cart_item = CartItem.objects.get(id=item_id, user=request.user)
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, "Cart updated successfully")
            else:
                cart_item.delete()
                messages.info(request, "Item removed from the cart")
        except CartItem.DoesNotExist:
            messages.error(request, "Item not found in the cart")

        # Replace 'cart_view' with the actual name of your cart view
        return redirect('cart_list')

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.price * item.quantity  # Calculate total price here

    context = {
        'cart_items': cart_items,
    }
    return render(request, 'summary.html', context)

@login_required
def remove_from_cart(request, item_id):
    item = CartItem.objects.get(id=item_id, user=request.user)
    item.delete()
    return redirect('cart')

@csrf_exempt
@login_required
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_quantity = data.get('quantity')
            
            cart_item = CartItem.objects.get(id=item_id, user=request.user)
            cart_item.quantity = new_quantity
            cart_item.save()
            
            return JsonResponse({'success': True}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def process_payment(request):
    if request.method == 'POST':
        # Retrieve payment details from POST data
        card_number = request.POST.get('cardNumber')
        card_holder = request.POST.get('cardHolder')
        exp_month = request.POST.get('expMonth')
        exp_year = request.POST.get('expYear')
        cvv = request.POST.get('cvv')

        # Retrieve address details from POST data
        street_address = request.POST.get('streetAddress')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postalCode')

        # Additional validation and processing logic for these fields

        # Calculate the total amount from the cart
        cart_items = CartItem.objects.filter(user=request.user)
        total_amount = sum(item.price * item.quantity for item in cart_items)

        # Here, you should add the logic to process the payment
        # For example, integrating with a payment gateway like Stripe, PayPal, etc.
        try:
            # Dummy payment processing logic
            # In real scenario, you will integrate with a payment gateway
            payment_is_successful = True  # Replace with actual payment condition

            if payment_is_successful:
                # Create an Order and OrderItem instances after successful payment
                order = Order.objects.create(
                    user=request.user,
                    total_price=total_amount,
                    created_at=timezone.now(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code
                )
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_name=item.product_name,
                        price=item.price,
                        quantity=item.quantity
                    )

                # Clear the cart
                cart_items.delete()

                messages.success(
                    request, "Payment was successful and your order has been placed.")
                # Redirect to a success page or order summary
                return redirect('payment_page', order_id=order.id)
            else:
                messages.error(request, "Payment failed. Please try again.")
                return redirect('payment_page')

        except Exception as e:
            # Handle any exceptions during payment processing
            # messages.error(request, "Payment failed: " + str(e))
            return redirect('payment_page')

    # Redirect to the payment page if not POST
    return redirect('payment_page')


@login_required
def payment_page(request):
    # Calculate total amount for the items in the cart
    cart_items = CartItem.objects.filter(user=request.user)
    total_amount = sum(item.price * item.quantity for item in cart_items)

    context = {
        'total_amount': total_amount,
    }
    return render(request, 'payment_page.html', context)


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})
