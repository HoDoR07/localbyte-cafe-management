from django.shortcuts import render, redirect, get_object_or_404
from .models import (Category, MenuItem, CafeTable, Reservation, Invoice, Cart,
                      CartItem, Order, OrderItem, OrderInvoice, InventoryItem, 
                      StockTransaction, KitchenStock, CafeSetting, ContactMessage, Payment)

from .forms import RegisterForm, LoginForm, ContactForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Sum
from django.db.models.functions import TruncDate , TruncMonth
from django.http import JsonResponse



# Create your views here.
def home(request):

    cafe = CafeSetting.objects.first()

    if cafe is None:
        return render(
            request,
            "home/home.html",
            {
                "cafe": None,
                "is_open": False,
                "has_special_offer": False,
            }
        )

    current_time = timezone.localtime().time()

    if cafe.opening_time <= cafe.closing_time:

        is_open = (
            cafe.opening_time <= current_time <= cafe.closing_time
        )

    else:

        is_open = (
            current_time >= cafe.opening_time
            or current_time <= cafe.closing_time
        )

    has_special_offer = cafe.special_offer

    return render(
        request,
        "home/home.html",
        {
            "cafe": cafe,
            "is_open": is_open,
            "has_special_offer": has_special_offer,
        }
    )


def menu(request):

    categories = Category.objects.all()

    return render(
        request,
        "home/menu.html",
        {
            "categories": categories
        }
    )


@login_required
def profile(request):
    return render(
        request,
        "home/profile.html"
    )


def menu(request):

    categories = Category.objects.all()

    return render(request, 'home/menu.html', {
        "categories": categories
    })


def userregister(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User(
                username=username,
                email=email
            )
            user.set_password(password)
            user.save()

            login(request, user)

            if request.session.get("table_id"):
                return redirect("reservation_confirmation")

            return redirect('home')

    else:
        form = RegisterForm()

    return render(request, 'home/register.html', {"form": form})


def userlogin(request):

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                username=username,
                password=password
            )

            if user is not None:

                if not user.is_active:
                    form.add_error(
                        None,
                        "Your account is inactive."
                    )

                else:
                    login(request, user)

                    if request.session.get("table_id"):
                        return redirect("reservation_confirmation")

                    return redirect("home")

            else:
                form.add_error(
                    None,
                    "Invalid username or password."
                )

    else:
        form = LoginForm()

    return render(
        request,
        'home/login.html',
        {"form": form}
    )


def userlogout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'home/profile.html')




@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect("home")

    total_orders = Order.objects.count()

    pending_orders = Order.objects.filter(
        status="pending"
    ).count()

    confirmed_orders = Order.objects.filter(
        status="confirmed"
    ).count()

    preparing_orders = Order.objects.filter(
        status="preparing"
    ).count()

    ready_orders = Order.objects.filter(
        status="ready"
    ).count()

    completed_orders = Order.objects.filter(
        status="completed"
    ).count()

    cancelled_orders = Order.objects.filter(
        status="cancelled"
    ).count()

    total_reservations = Reservation.objects.count()

    pending_reservations = Reservation.objects.filter(
        status="pending"
    ).count()

    confirmed_reservations = Reservation.objects.filter(
        status="confirmed"
    ).count()

    cancelled_reservations = Reservation.objects.filter(
        status="cancelled"
    ).count()

    completed_reservations = Reservation.objects.filter(
        status="completed"
    ).count()

    total_customers = User.objects.filter(
        is_superuser=False
    ).count()

    active_customers = User.objects.filter(
        is_active=True,
        is_superuser=False
    ).count()

    customers_with_orders = Order.objects.values(
        "customer"
    ).distinct().count()

    total_revenue = Order.objects.filter(
        payment_status="paid"
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")

    revenue_by_day = Order.objects.filter(
        payment_status="paid"
    ).annotate(
        day=TruncDate("created_at")
    ).values(
        "day"
    ).annotate(
        revenue=Sum("total_amount")
    ).order_by("day")


    revenue_by_month = Order.objects.filter(
        payment_status="paid"
    ).annotate(
        month=TruncMonth("created_at")
    ).values(
        "month"
    ).annotate(
        revenue=Sum("total_amount")
    ).order_by("month")
    

    total_payments = Payment.objects.count()

    paid_payments = Payment.objects.filter(
        payment_status="paid"
    ).count()

    pending_payments = Payment.objects.filter(
        payment_status="pending"
    ).count()

    failed_payments = Payment.objects.filter(
        payment_status="failed"
    ).count()

    top_selling_items = OrderItem.objects.filter(
        order__payment_status="paid"
    ).values(
        "menu_item__name"
    ).annotate(
        total_quantity=Sum("quantity")
    ).order_by(
        "-total_quantity"
    )

    order_chart_data = [
        pending_orders,
        confirmed_orders,
        preparing_orders,
        ready_orders,
        completed_orders,
        cancelled_orders,
    ]


    reservation_chart_data = [
        pending_reservations,
        confirmed_reservations,
        cancelled_reservations,
        completed_reservations,
    ]


    payment_chart_data = [
        paid_payments,
        pending_payments,
        failed_payments,
    ]


    revenue_day_labels = []

    revenue_day_data = []

    for day in revenue_by_day:

        revenue_day_labels.append(
            day["day"].strftime("%d %b %Y")
        )

        revenue_day_data.append(
            float(day["revenue"])
        )


    revenue_month_labels = []

    revenue_month_data = []

    for month in revenue_by_month:

        revenue_month_labels.append(
            month["month"].strftime("%b %Y")
        )

        revenue_month_data.append(
            float(month["revenue"])
        )


    top_selling_labels = []

    top_selling_data = []

    for item in top_selling_items:

        top_selling_labels.append(
            item["menu_item__name"]
        )

        top_selling_data.append(
            item["total_quantity"]
        )    

    inventory_items = InventoryItem.objects.all()

    low_stock_items = []

    for item in inventory_items:

        if item.quantity == 0:
            low_stock_items.append(item)

        elif item.quantity <= item.minimum_stock:
            low_stock_items.append(item)

    total_inventory_items = InventoryItem.objects.count()

    out_of_stock_items = InventoryItem.objects.filter(
        quantity=0
    ).count()

    low_stock_count = len(low_stock_items)

    recent_orders = Order.objects.all().order_by(
        "-created_at"
    )[:5]

    recent_reservations = Reservation.objects.all().order_by(
        "-created_at"
    )[:5]

    recent_payments = Payment.objects.all().order_by(
        "-created_at"
    )[:5]

    return render(
        request,
        "home/admin_dashboard.html",
        {
            "total_orders": total_orders,

            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "preparing_orders": preparing_orders,
            "ready_orders": ready_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,

            "total_reservations": total_reservations,
            "pending_reservations": pending_reservations,
            "confirmed_reservations": confirmed_reservations,
            "cancelled_reservations": cancelled_reservations,
            "completed_reservations": completed_reservations,

            "total_customers": total_customers,
            "active_customers": active_customers,
            "customers_with_orders": customers_with_orders,

            "total_revenue": total_revenue,
            "revenue_by_day": revenue_by_day,
            "revenue_by_month": revenue_by_month,

            "total_payments": total_payments,
            "paid_payments": paid_payments,
            "pending_payments": pending_payments,
            "failed_payments": failed_payments,

            "top_selling_items": top_selling_items,

            "inventory_items": inventory_items,
            "low_stock_items": low_stock_items,

            "recent_orders": recent_orders,
            "recent_reservations": recent_reservations,
            "recent_payments": recent_payments,

            "total_inventory_items": total_inventory_items,
            "low_stock_count": low_stock_count,
            "out_of_stock_items": out_of_stock_items,

            "order_chart_data": order_chart_data,

            "reservation_chart_data": reservation_chart_data,

            "payment_chart_data": payment_chart_data,

            "revenue_day_labels": revenue_day_labels,
            "revenue_day_data": revenue_day_data,

            "revenue_month_labels": revenue_month_labels,
            "revenue_month_data": revenue_month_data,

            "top_selling_labels": top_selling_labels,
            "top_selling_data": top_selling_data,

        }
    )



@login_required
def manager_dashboard(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    recent_orders = Order.objects.all().order_by("-created_at")[:5]

    pending_orders = Order.objects.filter(
        status="pending"
    ).count()

    pending_order_list = Order.objects.filter(
        status="pending"
    ).order_by("-created_at")

    confirmed_orders = Order.objects.filter(
        status="confirmed"
    ).count()

    confirmed_order_list = Order.objects.filter(
        status="confirmed"
    ).order_by("-created_at")

    preparing_orders = Order.objects.filter(
        status="preparing"
    ).count()

    ready_orders = Order.objects.filter(
        status="ready"
    ).count()

    completed_orders = Order.objects.filter(
        status="completed"
    ).count()

    inventory_items = InventoryItem.objects.all()

    low_stock_items = []

    for item in inventory_items:
        if item.quantity == 0:
            low_stock_items.append(item)

        elif item.quantity <= item.minimum_stock:
            low_stock_items.append(item)

    
    reservations = Reservation.objects.all()

    recent_reservations = Reservation.objects.all().order_by("-created_at")[:5]

    pending_reservations = Reservation.objects.filter(
        status = "pending"
    ).count()

    pending_reservation_list = Reservation.objects.filter(
        status="pending"
    ).order_by("-created_at")

    confirmed_reservations = Reservation.objects.filter(
        status = "confirmed"
    ).count()

    confirmed_reservation_list = Reservation.objects.filter(
        status="confirmed"
    ).order_by("-created_at")

    total_payments = Payment.objects.count()

    paid_payments = Payment.objects.filter(
        payment_status="paid"
    ).count()

    pending_payments = Payment.objects.filter(
        payment_status="pending"
    ).count()

    recent_payments = Payment.objects.all().order_by("-created_at")[:5]

    total_customers = User.objects.filter(
        is_superuser=False
    ).count()


    return render(request, "home/manager_dashboard.html", {

        "recent_orders": recent_orders,

        "pending_orders": pending_orders,
        "pending_order_list": pending_order_list,

        "confirmed_orders": confirmed_orders,
        "confirmed_order_list": confirmed_order_list,

        "preparing_orders": preparing_orders,
        "ready_orders": ready_orders,
        "completed_orders": completed_orders,

        "inventory_items": inventory_items,
        "low_stock_items": low_stock_items,

        "recent_reservations": recent_reservations,
        "reservations": reservations,
        "pending_reservations": pending_reservations,
        "pending_reservation_list": pending_reservation_list,

        "confirmed_reservations": confirmed_reservations,
        "confirmed_reservation_list": confirmed_reservation_list,

        "total_payments": total_payments,
        "paid_payments": paid_payments,
        "pending_payments": pending_payments,
        "recent_payments": recent_payments,

        "total_customers": total_customers,
    })



@login_required
def manager_mark_payment_paid(request, payment_id):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    if request.method != "POST":
        return redirect("manager_dashboard")

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    if payment.payment_status == "paid":
        return redirect("manager_dashboard")

    payment.payment_status = "paid"
    payment.save()

    order = payment.order

    order.payment_status = "paid"
    order.save()

    invoice, created = OrderInvoice.objects.get_or_create(
        order=order,
        defaults={
            "invoice_number": f"INV-{order.id}",
            "order": order,
            "customer": order.customer,
            "amount": order.total_amount,
            "payment_method": payment.payment_method,
            "payment_status": payment.payment_status
        }
    )

    return redirect("manager_dashboard")



@login_required
def confirm_order(request, order_id):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    if request.method != "POST":
        return redirect("manager_dashboard")

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if order.payment_status != "paid":
        return redirect("manager_dashboard") 

    if order.status != "pending":
        return redirect("manager_dashboard")

    order.status = "confirmed"
    order.save()

    return redirect("manager_dashboard")




def checkout(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            customer = request.user
        )
    else:
        cart, created = Cart.objects.get_or_create(
            session_key = session_key
        )
    cart_items = cart.items.all()

    if not cart_items.exists():
        return redirect("cart")

    total = 0

    for item in cart_items:
        item.item_subtotal = item.menu_item.price * item.quantity
        total += item.item_subtotal

    cafe_setting = CafeSetting.objects.first()  
    gst_rate = cafe_setting.gst_rate

    gst = total * gst_rate / Decimal("100")
    grand_total = total + gst
    

    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")

        order = Order.objects.create(
            customer = request.user,
            subtotal = total,
            gst_rate=gst_rate,
            gst_amount=gst,
            total_amount=grand_total
        )
        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                quantity=item.quantity,
                price=item.menu_item.price
            )

        Payment.objects.create(
        order=order,
        amount=order.total_amount,
        payment_method="upi",
        payment_status="pending"
        )
                

        return redirect(
            "payment",
            order_id=order.id
        )
        

    return render(request, 'home/checkout.html', {
        "cart": cart,
        "cart_items": cart_items,
        "total": total,
        "gst_rate": gst_rate,
        "gst": gst,
        "grand_total": grand_total
    })




def book_table(request):

    today = timezone.localdate()
    available_table_list = []

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "select_table":

            table_id = request.POST.get("table_id")
            reservation_date = request.POST.get("date")
            reservation_time = request.POST.get("time")
            number_of_guests = request.POST.get("guests")

            if not all([
                table_id,
                reservation_date,
                reservation_time,
                number_of_guests
            ]):
                return redirect("book_table")

            try:
                number_of_guests = int(number_of_guests)
            except (ValueError, TypeError):
                return redirect("book_table")

            if number_of_guests <= 0:
                return redirect("book_table")
            
            try:
                parsed_date = datetime.strptime(
                    reservation_date,
                    "%Y-%m-%d"
                ).date()

                parsed_time = datetime.strptime(
                    reservation_time,
                    "%H:%M"
                ).time()

            except (ValueError, TypeError):
                return redirect("book_table")

            if parsed_date < today:
                return redirect("book_table")

            if parsed_date == today:

                current_time = timezone.localtime().time()

                if parsed_time <= current_time:
                    return redirect("book_table")


            request.session["table_id"] = table_id
            request.session["reservation_date"] = reservation_date
            request.session["reservation_time"] = reservation_time
            request.session["number_of_guests"] = number_of_guests

            if request.user.is_authenticated:
                return redirect("reservation_confirmation")

            return redirect("login")

        else:

            reservation_date = request.POST.get("date")
            reservation_time = request.POST.get("time")
            guests = request.POST.get("guests")

            if not all([
                reservation_date,
                reservation_time,
                guests
            ]):
                return redirect("book_table")

            try:
                number_of_guests = int(guests)
            except (ValueError, TypeError):
                return redirect("book_table")

            if number_of_guests <= 0:
                return redirect("book_table")

            try:
                parsed_date = datetime.strptime(
                    reservation_date,
                    "%Y-%m-%d"
                ).date()

                parsed_time = datetime.strptime(
                    reservation_time,
                    "%H:%M"
                ).time()

            except (ValueError, TypeError):
                return redirect("book_table")

            if parsed_date < today:
                return redirect("book_table")

            if parsed_date == today:

                current_time = timezone.localtime().time()

                if parsed_time <= current_time:
                    return redirect("book_table")

            available_table = CafeTable.objects.filter(
                capacity__gte=number_of_guests,
                table_status="available"
            )

            for table in available_table:

                already_booked = Reservation.objects.filter(
                    table=table,
                    reservation_date=parsed_date,
                    reservation_time=parsed_time
                ).exists()

                if not already_booked:
                    available_table_list.append(table)

    return render(request, 'home/book_table.html', {
        "today": today,
        "available_tables": available_table_list
    })




@login_required
def reservation_confirmation(request):

    table_id = request.session.get("table_id")
    reservation_date = request.session.get("reservation_date")
    reservation_time = request.session.get("reservation_time")
    number_of_guests = request.session.get("number_of_guests")

    if not all([
        table_id,
        reservation_date,
        reservation_time,
        number_of_guests
    ]):
        return redirect("book_table")

    try:
        number_of_guests = int(number_of_guests)
    except (ValueError, TypeError):
        return redirect("book_table")

    if number_of_guests <= 0:
        return redirect("book_table")

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "continue_payment":

            table = get_object_or_404(
                CafeTable,
                id=table_id
            )

            if table.table_status != "available":
                return redirect("book_table")

            if number_of_guests > table.capacity:
                return redirect("book_table")

            already_booked = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                reservation_time=reservation_time
            ).exists()

            if not already_booked:

                try:

                    reservation = Reservation.objects.create(
                        table=table,
                        customer=request.user,
                        reservation_date=reservation_date,
                        reservation_time=reservation_time,
                        number_of_guests=number_of_guests,
                        status="pending"
                    )

                except IntegrityError:

                    return redirect("book_table")

                request.session["reservation_id"] = reservation.id

                return redirect("reservation_payment")

    return render(
        request,
        'home/reservation_confirmation.html',
        {
            "table_id": table_id,
            "reservation_date": reservation_date,
            "reservation_time": reservation_time,
            "number_of_guests": number_of_guests
        }
    )



@login_required
def reservation_payment(request):

    reservation_id = request.session.get("reservation_id")

    if not reservation_id:
        return redirect("book_table")


    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        customer = request.user
    )

    if reservation.status == "cancelled":
        return redirect("my_reservation")

    if reservation.token_payment_status == "paid":
        return redirect(
            "table_invoice",
            reservation_id=reservation.id
        )

    if reservation.status != "pending":
        return redirect("my_reservation")

    if request.method == "POST":

        if reservation.token_payment_status == "paid":
            return redirect(
                "table_invoice",
                reservation_id=reservation.id
            )

        reservation.token_payment_status="paid"
        reservation.status = "pending"
        reservation.save()

        invoice, created = Invoice.objects.get_or_create(
            invoice_number=f"INV-{reservation.id}",
            defaults={
                "reservation": reservation,
                "customer": request.user,
                "amount": reservation.token_amount,
                "payment_method": "UPI",
                "payment_status": "paid"
            }
        )

        request.session["invoice_id"] = invoice.id

        request.session.pop("table_id", None)
        request.session.pop("reservation_date", None)
        request.session.pop("reservation_time", None)
        request.session.pop("number_of_guests", None)
        request.session.pop("reservation_id", None)

        return redirect('table_invoice',reservation_id=reservation.id)

    return render(request, 'home/reservation_payment.html',{
        "reservation": reservation
    })



@login_required
def confirm_reservation(request, reservation_id):
    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect('home')

    if request.method != "POST":
        return redirect("manager_dashboard")

    reservation = get_object_or_404(
        Reservation,
        id = reservation_id
    )

    if reservation.token_payment_status != "paid":
        return redirect("manager_dashboard")

    if reservation.status != "pending":
        return redirect("manager_dashboard")
    
    reservation.status = "confirmed"
    reservation.save()

    return redirect("manager_dashboard")


@login_required
def table_invoice(request, reservation_id):

    

    invoice = get_object_or_404(
        Invoice,
        reservation_id=reservation_id,
        customer = request.user
    )

    return render(request, 'home/invoice.html', {
        "invoice": invoice
    })



@login_required
def my_reservation(request):

    reservations = Reservation.objects.filter(
        customer = request.user
    )

    return render(request, 'home/my_reservation.html', {
        "reservations": reservations
    })



def add_to_cart(request, menu_item_id):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    menu_item = get_object_or_404(
        MenuItem,
        id=menu_item_id
    )

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

    else:

        cart, created = Cart.objects.get_or_create(
            session_key=session_key
        )

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item
    )

    if not item_created:

        cart_item.quantity += 1
        cart_item.save()

    cart_count = 0

    for item in cart.items.all():

        cart_count += item.quantity

    return JsonResponse({
        "success": True,
        "message": f"{menu_item.name} added to cart.",
        "cart_count": cart_count
    })



def cart(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )
    else: 
        cart, created = Cart.objects.get_or_create(
            session_key = session_key
        )

    cart_items = cart.items.all()

    total = 0

    for item in cart_items:
        item.item_subtotal = item.menu_item.price * item.quantity
        total += item.item_subtotal

    return render(
        request,
        "home/cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total": total
        }
    )



def increase_quantity(request, item_id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

    else:

        cart, created = Cart.objects.get_or_create(
            session_key=session_key
        )

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    cart_item.quantity += 1
    cart_item.save()

    item_subtotal = (
        cart_item.menu_item.price *
        cart_item.quantity
    )

    total = 0

    for item in cart.items.all():

        total += (
            item.menu_item.price *
            item.quantity
        )

    return JsonResponse({
        "success": True,
        "quantity": cart_item.quantity,
        "item_subtotal": float(item_subtotal),
        "total": float(total)
    })



def decrease_quantity(request, item_id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

    else:

        cart, created = Cart.objects.get_or_create(
            session_key=session_key
        )

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

    item_subtotal = (
        cart_item.menu_item.price *
        cart_item.quantity
    )

    total = 0

    for item in cart.items.all():

        total += (
            item.menu_item.price *
            item.quantity
        )

    return JsonResponse({
        "success": True,
        "quantity": cart_item.quantity,
        "item_subtotal": float(item_subtotal),
        "total": float(total)
    })



def remove_from_cart(request, item_id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

    else:

        cart, created = Cart.objects.get_or_create(
            session_key=session_key
        )

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    cart_item.delete()

    total = 0

    for item in cart.items.all():

        total += (
            item.menu_item.price *
            item.quantity
        )

    return JsonResponse({
        "success": True,
        "total": float(total)
    })

def clear_cart(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)


    if not request.session.session_key:
        request.session.create()


    session_key = request.session.session_key


    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            customer=request.user
        )

    else:

        cart, created = Cart.objects.get_or_create(
            session_key=session_key
        )


    cart.items.all().delete()


    return JsonResponse({
        "success": True,
        "message": "Cart cleared successfully."
    })



@login_required
def my_orders(request):

    orders = Order.objects.filter(
        customer = request.user
    ).order_by("-created_at")

    return render(request, 'home/my_orders.html',{
        "orders": orders
    })



@login_required
def order_invoice(request, order_id):

    order = get_object_or_404(
        Order,
        id = order_id,
        customer = request.user
    )

    invoice = get_object_or_404(
        OrderInvoice,
        order = order,
        customer = request.user
    )

    order_items = order.items.select_related(
        "menu_item"
    ).all()

    invoice_items = []

    for item in order_items:

        subtotal = item.price * item.quantity

        invoice_items.append({
            "name": item.menu_item.name,
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": subtotal
        })

    return render(request, 'home/order_invoice.html', {
        "order": order,
        "invoice": invoice,
        "invoice_items": invoice_items
    })


@login_required
def order_tracking(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    return render(request, 'home/order_tracking.html', {
        "order": order
    })


@login_required
def kitchen_orders(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    orders = Order.objects.filter(
        status__in = ["confirmed", "preparing", "ready"]
    ).order_by("created_at")

    return render(request, 'home/kitchen_orders.html', {
        "orders": orders
    })


@login_required
def start_preparing(request, order_id):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen_orders")

    order = get_object_or_404(
        Order,
        id = order_id,
    )

    if order.status != "confirmed":
        return redirect("kitchen_orders")

    order.status = "preparing"
    order.save()

    return redirect('kitchen_orders')



@login_required
def mark_ready(request, order_id):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen_orders")

    order = get_object_or_404(
            Order,
            id = order_id,
        )
    

    if order.status != "preparing":
        return redirect("kitchen_orders")
    
    order.status = "ready"
    order.save()

    return redirect('kitchen_orders')



@login_required
def complete_order(request, order_id):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    if request.method != "POST":
        return redirect("kitchen_orders")

    order = get_object_or_404(
            Order,
            id = order_id,
        )
    

    if order.status != "ready":
        return redirect("kitchen_orders")

    order.status = "completed"
    order.save()

    return redirect('kitchen_orders')





@login_required
def inventory(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    inventory_items = InventoryItem.objects.all()

    low_stock_items = []

    for item in inventory_items:

        if item.quantity == 0:
            item.stock_status = "Out of Stock"
            low_stock_items.append(item)

        elif item.quantity <= item.minimum_stock:
            item.stock_status = "Low Stock"
            low_stock_items.append(item)

        else:
            item.stock_status = "In Stock"

    return render(request, 'home/inventory.html',{
        "inventory_items": inventory_items,
        "low_stock_items": low_stock_items
    })


@login_required
def add_stock_transaction(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    if request.method != "POST":
        return redirect("inventory")

    inventory_item_id = request.POST.get("inventory_item")
    transaction_type = request.POST.get("transaction_type")
    quantity = request.POST.get("quantity")

    inventory_item = get_object_or_404(
        InventoryItem,
        id = inventory_item_id
    )

    try:
        quantity = Decimal(quantity)
    except (InvalidOperation, TypeError):
        return redirect("inventory")

    if quantity <= 0:
        return redirect("inventory")


    if transaction_type == "purchase":
        inventory_item.quantity += quantity

    elif transaction_type == "consumption":

        if quantity > inventory_item.quantity:
            return redirect("inventory")
            
        inventory_item.quantity -= quantity

    elif transaction_type == "adjustment":
        inventory_item.quantity = quantity

    else:
        return redirect("inventory")
            

        
    inventory_item.save()

    StockTransaction.objects.create(
        inventory_item = inventory_item,
        transaction_type = transaction_type,
        quantity = quantity
    )

    return redirect("inventory")



@login_required
def stock_transactions(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    transactions = StockTransaction.objects.all().order_by("-created_at")

    return render(request, 'home/stock_transactions.html', {
        "transactions": transactions
    })


@login_required
def issue_stock_to_kitchen(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    if request.method != "POST":
        return redirect("inventory")


    inventory_item_id = request.POST.get("inventory_item")
    quantity = request.POST.get("quantity")

    inventory_item = get_object_or_404(
        InventoryItem,
        id = inventory_item_id
    )

    try:
        quantity = Decimal(quantity)
    except (InvalidOperation, TypeError):
        return redirect("inventory")

    if quantity <= 0:
        return redirect("inventory")

    if quantity > inventory_item.quantity:
        return redirect("inventory")

    kitchen_stock, created = KitchenStock.objects.get_or_create(
        inventory_item = inventory_item
    )

    inventory_item.quantity -= quantity
    kitchen_stock.quantity += quantity

    inventory_item.save()
    kitchen_stock.save()

    StockTransaction.objects.create(
        inventory_item=inventory_item,
        transaction_type="issue",
        quantity=quantity
    )

    return redirect("inventory")
    


@login_required
def kitchen_stock(request):

    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="Manager").exists()
    ):
        return redirect("home")

    kitchen_stocks = KitchenStock.objects.all()

    return render(request, 'home/kitchen_stocks.html', {
        "kitchen_stocks": kitchen_stocks
    })


def contact(request):

    cafe = CafeSetting.objects.first()

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                phone_number=form.cleaned_data["phone_number"],
                message=form.cleaned_data["message"],
            )

            return render(request, "home/contact.html", {
                "form": ContactForm(),
                "success": True,
                "cafe": cafe
            })
    else:
        form = ContactForm()

    return render(request, 'home/contact.html', {
        "form": form,
        "cafe": cafe
    })




@login_required
def payment(request, order_id):

    order = get_object_or_404(
        Order,
        id = order_id,
        customer = request.user
    )

    payment = get_object_or_404(
        Payment,
        order = order
    )

    if order.status == "cancelled":
        return redirect("my_orders")

    if payment.payment_status == "paid":
        return redirect(
            "order_invoice",
            order_id=order.id
        )

    if order.status != "pending":
        return redirect("my_orders")

    if request.method == "POST":

        if payment.payment_status == "paid":
            return redirect(
                "order_invoice",
                order_id=order.id
            )

        payment_method = request.POST.get("payment_method")

        if payment_method not in ["upi", "card", "cash"]:
            return redirect("payment", order_id=order.id)

        payment.payment_method = payment_method

        if payment_method == "cash":

            payment.payment_status = "pending"
            payment.save()

            order.payment_status = "pending"
            order.save()

            return redirect("my_orders")


        payment.payment_status = "paid"
        payment.save()
        order.payment_status = "paid"
        order.save()

        cart = Cart.objects.filter(
            customer=request.user
        ).first()

        if cart:
            cart.items.all().delete()

        invoice, created = OrderInvoice.objects.get_or_create(
            order = order,
            defaults =  {
               "invoice_number" : f"INV-{order.id}",
                "order" : order,
                "customer": request.user,
                "amount" : order.total_amount,
                "payment_method" : payment.payment_method,
                "payment_status" : payment.payment_status
            } 
        )

        return redirect(
            "order_invoice",
            order_id=order.id
        )

    return render(request, 'home/payment.html', {
        "order": order,
        "payment": payment
    })

