from django.shortcuts import render, redirect
from django.db import connection
from random import randint
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
import json


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def is_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

# Create your views here.


def index(request):

    with connection.cursor() as cursor:
        cursor.execute(
            " delete from FlightLeg where ARR_DT < (select NOW()) ")
        cursor.execute("CALL update_flight_status()")

        cursor.execute(" select BookingID from Passenger ")
        ids = cursor.fetchall()

    if (ids):
        ids = list(ids[0])
    if (ids.__len__() != 0):
        with connection.cursor() as cursor:
            for i in ids:
                cursor.execute(
                    " delete from Passenger where BookingID = %s and %s not in (select BookingID from books)", [i, i])

    return render(request, 'index.html')


@user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def index_flight(request):

    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("Select City, Country from Airport")
            ap_list = dictfetchall(cursor)

    return render(request, 'index-flight.html', {'ap_list': ap_list})


@user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def account_bookings(request):

    if request.method == 'GET':

        user = request.user
        Fname = user.first_name
        Lname = user.last_name

        with connection.cursor() as cursor:
            cursor.execute(
                " delete from FlightLeg where ARR_DT < (select NOW()) ")
            cursor.execute("CALL update_flight_status()")

            cursor.execute(" select BookingID from Passenger ")
            ids = cursor.fetchall()
            print(ids)

        if (ids.__len__() != 0):
            ids = list(ids)
        if (ids.__len__() != 0):
            with connection.cursor() as cursor:
                for i in ids:
                    cursor.execute(
                        " delete from Passenger where BookingID = %s and %s not in (select BookingID from books)", [i, i])

        with connection.cursor() as cursor:

            cursor.execute(
                "select F.*, P.*, T.*, B.* from FlightLeg F, Passenger P, Ticket T, books B where F.FL_ID = B.FL_ID and T.BookingID = P.BookingID and P.PassportID = T.PassengerID and B.BookingID = T.BookingID and B.BookingID = (select BookingID from Passenger where Fname = %s and Lname = %s) ", [Fname, Lname])
            details = dictfetchall(cursor)

        return render(request, 'account-bookings.html', {'details': details})

    if request.method == 'POST':
        booking_id = request.POST.get('bookingID')

        with connection.cursor() as cursor:
            cursor.execute(
                " delete from books where BookingID = %s ", [booking_id])
        return redirect('/account-bookings')


@ user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def account_delete(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        User.objects.filter(username=username).delete()
        return redirect('index')

    return render(request, 'account-delete.html')


@ user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def account_settings(request):
    return render(request, 'account-settings.html')


@ user_passes_test(lambda u: is_in_group(u, 'Airport_admin'))
def add_listing_minimal(request):
    if request.method == 'GET':
        return render(request, 'add-listing-minimal.html')

    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        address = request.POST['address']
        gender = request.POST['gender']
        salary = request.POST['salary']
        phone = request.POST['phone']
        DOB = request.POST['dob']
        dob = f"{DOB[6:]}-{DOB[3:5]}-{DOB[:2]}"
        jobtype = request.POST['jobtype']

        al = request.POST['al']
        if al == 'Blogzine':
            al = 'BL'
        elif al == 'Flyzo':
            al = 'FLY'
        elif al == 'Folio':
            al = 'FO'
        elif al == 'Tulip':
            al = 'TP'
        else:
            al = 'WIZ'

    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Employee (FName, LName, Address, Gender, Salary, Phone, DOB, AL_Code, JobType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [fname, lname, address, gender, salary, phone, dob, al, jobtype]
        )

    return render(request, 'listing-added2.html')


@user_passes_test(lambda u: is_in_group(u, 'Airline_admin'))
def add_listing(request):

    # get fields values
    if request.method == 'GET':

        airline = request.GET.get('airline')

        with connection.cursor() as cursor:
            cursor.execute("Select Name from Airport")
            ap = dictfetchall(cursor)
            cursor.execute(
                " Select FName from Employee where JobType = 'Pilot' and AL_Code = %s", [airline])
            pilot = dictfetchall(cursor)
            cursor.execute(
                " Select FName from Employee where JobType = 'Crew' and AL_Code = %s", [airline])
            crew = dictfetchall(cursor)

        return render(request, 'add-listing.html', {'ap': ap, 'pilot': pilot, 'crew': crew})

    # insert into FlightLeg
    if request.method == 'POST':

        flighttype = request.POST['flighttype']
        arr_ap = request.POST['arr_ap']
        with connection.cursor() as cursor:
            cursor.execute(
                "select Unique_code from Airport where Name = %s", [arr_ap])
            res = cursor.fetchall()
        arr_ap = res[0][0]

        gate = request.POST['gate']
        gate = gate.upper()

        al = request.POST['al']
        if al == 'Blogzine':
            al = 'BL'
        elif al == 'Flyzo':
            al = 'FLY'
        elif al == 'Folio':
            al = 'FO'
        elif al == 'Tulip':
            al = 'TP'
        else:
            al = 'WIZ'

        dep_dt = request.POST['dep_dt']
        arr_dt = request.POST['arr_dt']

        if flighttype == 'International - Connecting':
            int_arr_ap = request.POST['int_arr_ap']
            with connection.cursor() as cursor:
                cursor.execute(
                    "select Unique_code from Airport where Name = %s", [int_arr_ap])
                res = cursor.fetchall()
            int_arr_ap = res[0][0]
            int_arr_dt = request.POST['int_arr_dt']
            int_dep_dt = request.POST['int_dep_dt']

        fare = request.POST['fare']

        with connection.cursor() as cursor:
            cursor.execute(
                "select ID from Aircraft where AL_Code = %s order by RAND() LIMIT 2", [al])
            ids = cursor.fetchall()

        if flighttype == 'International - Connecting':
            aircraftId = ids[0][0]
            int_aircraftId = ids[1][0]
            with connection.cursor() as cursor:
                # put connecting flight statement here
                cursor.execute(
                    "INSERT INTO FlightLeg (FL_TYPE, ARR_AP, Gate, AL_Code, DEP_DT, ARR_DT, Fare,AircraftID, INTAircraftID, INT_ARR_DT, INT_DEP_DT, INT_AP) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [flighttype, arr_ap, gate, al, dep_dt,
                        arr_dt, fare, aircraftId, int_aircraftId, int_arr_dt, int_dep_dt, int_arr_ap]
                )
        else:
            aircraftId = ids[0][0]
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO FlightLeg (FL_TYPE, ARR_AP, Gate, AL_Code, DEP_DT, ARR_DT, Fare, AircraftID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    [flighttype, arr_ap, gate, al, dep_dt, arr_dt, fare, aircraftId]
                )

        # insert into crew table
        pilot = request.POST['pilot']
        crew = request.POST.getlist('crew')
        with connection.cursor() as cursor:
            cursor.execute("select FL_ID from FlightLeg where AircraftID = %s and AL_Code = %s and Fare = %s and ARR_AP = %s", [
                           aircraftId, al, fare, arr_ap])
            fl_id = cursor.fetchall()
            fl_id = fl_id[0][0]
            cursor.execute(
                "select EID from Employee where FName = %s", [pilot])
            pilot = cursor.fetchall()
            pilot = pilot[0][0]
            cursor.execute(
                "insert into Crew values (%s, %s)", [pilot, fl_id])
            for cr in crew:
                cursor.execute(
                    "select EID from Employee where FName = %s", [cr])
                crew = cursor.fetchall()
                crew = crew[0][0]
                cursor.execute(
                    "insert into Crew values (%s, %s)", [crew, fl_id])

        return render(request, 'listing-added.html')


@user_passes_test(lambda u: is_in_group(u, 'Airport_admin'))
def admin_agent_detail(request):

    if request.method == 'POST':

        eid = request.POST.get('eid')

        with connection.cursor() as cursor:
            cursor.execute(" select *from Employee where EID = %s", [eid])
            details = dictfetchall(cursor)[0]
            cursor.execute(" select count(*) from Crew where EID = %s", [eid])
            flight_count = cursor.fetchall()
            cursor.execute(
                " select count(*) from Crew where EID = %s and FL_ID in (select FL_ID from FlightLeg where DEP_DT = (select NOW()))", [eid])
            flights_today = cursor.fetchall()

        flight_count = flight_count[0][0]
        flights_today = flights_today[0][0]
        flights = {'count': flight_count, 'today': flights_today}

    return render(request, 'admin-agent-detail.html', {'emp': details, 'flights': flights})


@user_passes_test(lambda u: is_in_group(u, 'Airport_admin'))
def admin_agent_list(request):

    with connection.cursor() as cursor:
        cursor.execute(" select *from Employee where JobType = 'Pilot'")
        pilots = dictfetchall(cursor)

    return render(request, 'admin-agent-list.html', {'pilots': pilots})


@user_passes_test(lambda u: is_in_group(u, 'Airline_admin'))
def agent_bookings(request):

    user = request.user
    airline = user.username
    with connection.cursor() as cursor:
        cursor.execute(
            " select *from agent_view where AL_Code = %s", [airline])
        flights = dictfetchall(cursor)
        cursor.execute(
            " select count(*) from agent_view where AL_Code = %s", [airline])
        f = cursor.fetchall()

    f = f[0][0]
    f = {'flightCount': f}

    return render(request, 'agent-bookings.html', {'flights': flights, 'f': f})


@user_passes_test(lambda u: is_in_group(u, 'Airline_admin'))
def agent_dashboard(request):

    if request.method == 'GET':

        user = request.user
        airline = user.username

        with connection.cursor() as cursor:
            cursor.execute(
                " select count(*) from flights where AL_Code = %s ", [airline])
            total = list(cursor.fetchall())
            cursor.execute(
                " select count(*) from R_Seats_view where AL_Code = %s ", [airline])
            seats = cursor.fetchall()
            cursor.execute(
                " select Seat from R_Seats_view where AL_Code = %s", [airline])
            r_seats = cursor.fetchall()
            cursor.execute(
                " select max(Fare) from FlightLeg where AL_Code = %s", [airline])
            max_fare = list(cursor.fetchall())
            cursor.execute(
                " select min(Fare) from FlightLeg where AL_Code = %s", [airline])
            min_fare = list(cursor.fetchall())
            cursor.execute(
                " select Price from Ticket_view where AL_Code = %s", [airline])
            fares = cursor.fetchall()

        r_seats = [r_seats[i][0] for i in range(len(r_seats))]
        max_fare = max_fare[0][0]
        min_fare = min_fare[0][0]
        fares = [fares[i][0] for i in range(len(fares))]
        economy = 0
        business = 0
        first = 0
        print(r_seats)
        for i in r_seats:
            if i[0] in ['a', 'b', 'c', 'd']:
                economy += 1
            elif i[0] in ['e', 'f', 'g', 'h']:
                business += 1
            else:
                first += 1

        flight_count = total[0][0]
        total_seats = (72 * flight_count)
        seats_left = total_seats - seats[0][0]

        seats_list = [economy, business, first, seats_left]
        total_fare = 0
        for i in fares:
            total_fare += i
            
        print(seats_list)

        dash_dict = {'countFL': flight_count, 'earning': total_fare,
                     'seats_booked': len(r_seats), 'max': max_fare, 'min': min_fare, 'seats_list': seats_list}

    return render(request, 'agent-dashboard.html', {'dash': dash_dict})


@user_passes_test(lambda u: is_in_group(u, 'Airline_admin'))
def agent_listings(request):
    if request.method == 'POST':

        FL_ID = request.POST.get('fl_id')
        with connection.cursor() as cursor:
            cursor.execute(" delete from FlightLeg where FL_ID = %s ", [FL_ID])

        return redirect('/agent-listings')

    if request.method == 'GET':

        user = request.user
        airline = user.username

        with connection.cursor() as cursor:
            cursor.execute(
                " select count(*) from flights where AL_Code = %s ", [airline])
            total = list(cursor.fetchall())
            cursor.execute(
                " select seats_left from flights where AL_Code = %s ", [airline])
            seats_left_tup = list(cursor.fetchall())
            cursor.execute(
                " select Seat from R_Seats_view where AL_Code = %s", [airline])
            r_seats = list(cursor.fetchall())
            cursor.execute(
                " select max(Fare) from FlightLeg where AL_Code = %s", [airline])
            max_fare = list(cursor.fetchall())
            cursor.execute(
                " select min(Fare) from FlightLeg where AL_Code = %s", [airline])
            min_fare = list(cursor.fetchall())
            cursor.execute(
                " select Price from Ticket_view where AL_Code = %s", [airline])
            fares = list(cursor.fetchall())
            cursor.execute(
                " select * from flights where AL_Code = %s", [airline])
            flights = dictfetchall(cursor)

        max_fare = max_fare[0][0]
        min_fare = min_fare[0][0]
        if (fares):
            fares = fares[0]
        if (r_seats):
            r_seats = list(r_seats[0])
        economy = 0
        business = 0
        first = 0
        for i in r_seats:
            if i[0] in ['a', 'b', 'c', 'd']:
                economy += 1
            elif i[0] in ['e', 'f', 'g', 'h']:
                business += 1
            else:
                first += 1

        flight_count = total[0][0]
        total_seats = (72 * flight_count)
        seats_left_list = []
        if (seats_left_list):
            seats_left_list = list(seats_left_tup[0])
        seats_left = 0
        for i in seats_left_list:
            seats_left += i

        seats = [economy, business, first, seats_left]
        final = []

        for i in seats:
            if (i == 0):
                continue
            else:
                final.append(int((i/total_seats) * 100))

        total_fare = 0
        for i in fares:
            total_fare += i

        dash_dict = {'countFL': flight_count, 'earning': total_fare,
                     'seats_booked': len(r_seats), 'max': max_fare, 'min': min_fare}

        return render(request, 'agent-listings.html', {'dash': dash_dict, 'flights': flights})


@user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def booking_confirm(request, FL_ID, travelers):

    t = travelers
    travelers = {'travelers': travelers}
    # if request.method == 'POST':

    if request.method == 'POST':

        booking_id = request.POST.get('booking_id')

        with connection.cursor() as cursor:
            cursor.execute(
                " select *from books where FL_ID = %s and BookingID = %s", [FL_ID, booking_id])
            booking = dictfetchall(cursor)
            cursor.execute("Select * from FlightLeg where FL_ID = %s", [FL_ID])
            flight = dictfetchall(cursor)

        fare = flight[0].get('Fare')
        total_price = 0

        # generate ticket.

        with connection.cursor() as cursor:
            cursor.execute(
                " select PassportID from Passenger where BookingID = %s ", [booking_id])
            passenger_dict = dictfetchall(cursor)

        passport_ids = [passenger['PassportID']
                        for passenger in passenger_dict]

        booked_seats = request.POST.getlist('seats')
        #booked_seats = booked_seats[:t]

        with connection.cursor() as cursor:
            for index, seat in enumerate(booked_seats):
                if seat[0] in ['a', 'b', 'c', 'd']:
                    price = fare
                elif seat[0] in ['d', 'e', 'f', 'g']:
                    price = (fare+1000)
                else:
                    price = (fare+2000)

                cursor.execute(
                    " insert into Ticket (PassengerID, BookingID, Price, Seat) values (%s, %s, %s, %s)", [passport_ids[index], booking_id, price, seat])
                total_price += price

        total_price_dict = {'total_price': total_price}

        # r_seats
        with connection.cursor() as cursor:
            cursor.execute(
                " select Seat, TicketID from Ticket where BookingID = %s ", [booking_id])
            r_dict = dictfetchall(cursor)
            

        seats = [seats['Seat'] for seats in r_dict]
        T_ids = [T['TicketID'] for T in r_dict]

        with connection.cursor() as cursor:
            for i in range(t):
                cursor.execute(" insert into R_Seats values (%s, %s, %s) ", [
                               FL_ID, seats[i], T_ids[i]])

        return render(request, 'booking-confirm.html', {'booking': booking, 'travelers': travelers, 'total_price': total_price_dict})


@user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def flight_booking(request, FL_ID, travelers):

    seats = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'f1', 'f2', 'f3', 'f4', 'f5',
             'f6', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'j1', 'j2', 'j3', 'j4', 'j5', 'j6', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'l1', 'l2', 'l3', 'l4', 'l5', 'l6']

    if request.method == 'POST':

        passengers = travelers
        travelers_dict = {'travelers': travelers}

        with connection.cursor() as cursor:
            cursor.execute("Select * from FlightLeg where FL_ID = %s", [FL_ID])
            flights = dictfetchall(cursor)
            cursor.execute(
                "Select Seat from R_Seats where FL_ID = %s", [FL_ID])
            Rseats = cursor.fetchall()
            if Rseats:
                Rseats =  [Rseats[i][0] for i in range(len(Rseats))]
            else:
                Rseats = []

        base_fare = flights[0].get('Fare')

        seat_status = dict(
            zip(seats, map(lambda x: "booked" if x in Rseats else "empty", seats),))

        fare_dict = {'economy': base_fare, 'business': (
            base_fare+1000), 'first': (base_fare+2000), 'total': (base_fare*passengers)}

        booking_id = randint(0, 300000)
        booking_id_dict = {'booking_id': booking_id}
        # insert into passengers and books.
        with connection.cursor() as cursor:
            cursor.execute(
                " insert into books values (%s, %s, (select CURDATE()), 'Booked') ", [booking_id, FL_ID])

        for i in range(1, travelers + 1):
            gender = request.POST.get(f'gender{i}')
            fname = request.POST.get(f'fname{i}')
            lname = request.POST.get(f'lname{i}')
            DOB = request.POST.get(f'dob{i}')
            dob = f"{DOB[6:]}-{DOB[3:5]}-{DOB[:2]}"
            phone = request.POST.get(f'phone{i}')
            pn = request.POST.get(f'PN{i}')
            PN = pn.upper()
            with connection.cursor() as cursor:
                cursor.execute(" insert into Passenger (Gender, Fname, Lname, DOB, Phone, PassportID, BookingID) values (%s, %s, %s, %s, %s, %s, %s) ", [
                    gender, fname, lname, dob, phone, PN, booking_id])

        return render(request, 'flight-booking.html', {'booking_id': booking_id_dict, 'flights': flights, 'travelers': travelers_dict, 'fares': fare_dict, 'seat_status': seat_status})


def flight_detail_raw(request):

    if request.method == 'POST':

        booking_id = request.POST.get('bookingID')

        with connection.cursor() as cursor:
            cursor.execute(
                " select F.*, B.* from FlightLeg F, books B where F.FL_ID = B.FL_ID and B.BookingID = %s", [booking_id])
            flights = dictfetchall(cursor)
            cursor.execute(" select *from Airport ")
            airports = dictfetchall(cursor)

        if (flights.__len__() == 0):
            return redirect("error")

        return render(request, 'flight-detail-raw.html', {'flights': flights, 'airports': airports})


@user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def flight_detail(request, FL_ID, travelers):

    if request.method == 'GET':
        passengers = [(i+1) for i in range(travelers)]
        with connection.cursor() as cursor:
            cursor.execute("select * from FlightLeg where FL_ID = %s", [FL_ID])
            flights = dictfetchall(cursor)
            cursor.execute(" select *from Airport ")
            airports = dictfetchall(cursor)

        return render(request, 'flight-detail.html', {'flights': flights, 'airports': airports, 'passengers': passengers})

    if request.method == 'POST':

        return render(request, 'flight-detail.html')


@user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def flight_list(request):

    if request.method == 'POST':

        post_list = [request.POST.get('arr_ap'), request.POST.get('dep_dt')]
        if post_list == ['', '']:
            travelers = request.POST.get('travelers')
            travelers = travelers[0]
            travel_dict = {'travelers': travelers}
            with connection.cursor() as cursor:
                cursor.execute(
                    "select Unique_code from Airport")
                cursor.execute(
                    "select *from flights")
                flights = dictfetchall(cursor)
                cursor.execute(" select *from Airport ")
                airports = dictfetchall(cursor)

        else:
            travelers = request.POST.get('travelers')
            travelers = travelers[0]
            travel_dict = {'travelers': travelers}
            arr_ap = request.POST.get('arr_ap')
            arr_ap = arr_ap.split(', ')
            country = arr_ap[1]
            city = arr_ap[0]
            dep_dt = request.POST.get('dep_dt')
            with connection.cursor() as cursor:
                cursor.execute(
                    "select Unique_code from Airport where Country = %s and City = %s", [country, city])
                arr_AP = cursor.fetchall()
                arr_AP = arr_AP[0][0]
                cursor.execute(
                    "select *from flights where ARR_AP = %s and DEP_DT >= %s order by Fare ASC", [
                        arr_AP, dep_dt]
                )
                flights = dictfetchall(cursor)
                cursor.execute(" select *from Airport ")
                airports = dictfetchall(cursor)

        return render(request, 'flight-list.html', {'flights': flights, 'airports': airports, 'travelers': travel_dict})

    if request.method == "GET":

        travelers = request.GET.get('travelers')
        travelers = travelers[0]
        travel_dict = {'travelers': travelers}
        if not request.GET:
            with connection.cursor() as cursor:
                # flights is a view
                cursor.execute("select *from flights")
                flights = dictfetchall(cursor)
                cursor.execute("select *from Airport")
                airports = dictfetchall(cursor)
            return render(request, 'flight-list.html', {'flights': flights, 'airports': airports})

        get_list = list(request.GET)

        with connection.cursor() as cursor:
            cursor.execute("select *from Airport")
            airports = dictfetchall(cursor)

        with connection.cursor() as cursor:

            if get_list == ['csrfmiddlewaretoken', 'min_fare', 'max_fare']:

                min_fare = request.GET.get('min_fare')
                min_fare = min_fare[:-3]
                max_fare = request.GET.get('max_fare')
                max_fare = max_fare[:-3]
                cursor.execute(
                    "select *from flights where Fare between %s and %s", [min_fare, max_fare])
                flights = dictfetchall(cursor)

            elif get_list == ['csrfmiddlewaretoken', 'fl_type', 'min_fare', 'max_fare']:

                min_fare = request.GET.get('min_fare')
                min_fare = min_fare[:-3]
                max_fare = request.GET.get('max_fare')
                max_fare = max_fare[:-3]
                fl_type = request.GET.get('fl_type')
                if fl_type == 'International - Connecting':
                    cursor.execute(
                        "select *from flights where FL_TYPE = %s and Fare between %s and %s ", [fl_type, min_fare, max_fare])
                    flights = dictfetchall(cursor)
                else:
                    cursor.execute(
                        "select *from flights where FL_TYPE <> 'International - Connecting' and Fare between %s and %s ", [min_fare, max_fare])
                    flights = dictfetchall(cursor)

            elif get_list == ['csrfmiddlewaretoken', 'fl_type', 'min_fare', 'max_fare', 'preferred_airlines']:

                min_fare = request.GET.get('min_fare')
                min_fare = min_fare[:-3]
                max_fare = request.GET.get('max_fare')
                max_fare = max_fare[:-3]
                p_a = request.GET.get('preferred_airlines')
                fl_type = request.GET.get('fl_type')
                if fl_type == 'International - Connecting':
                    cursor.execute(
                        "select *from flights where FL_TYPE = %s and Fare between %s and %s and AL_Code = %s", [fl_type, min_fare, max_fare, p_a])
                    flights = dictfetchall(cursor)
                else:
                    cursor.execute(
                        "select *from flights where FL_TYPE <> 'International - Connecting' and Fare between %s and %s and AL_Code = %s", [fl_type, min_fare, max_fare, p_a])
                    flights = dictfetchall(cursor)

            else:

                min_fare = request.GET.get('min_fare')
                min_fare = min_fare[:-3]
                max_fare = request.GET.get('max_fare')
                max_fare = max_fare[:-3]
                p_a = request.GET.get('preferred_airlines')
                cursor.execute(
                    "select *from flights where AL_Code = %s and Fare between %s and %s ", [p_a, min_fare, max_fare])
                flights = dictfetchall(cursor)

        return render(request, 'flight-list.html', {'flights': flights, 'airports': airports, 'travelers': travel_dict})


def listing_added(request):
    return render(request, 'listing-added.html')


def listing_added2(request):
    return render(request, 'listing-added2.html')


def sign_up(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        password = request.POST.get('password')
        password = make_password(password)

        user = User.objects.create(
            username=username, password=password, first_name=fname, last_name=lname)
        group = Group.objects.get(name='Passenger')
        group.user_set.add(user)
        return redirect('index')

    else:
        return render(request, 'sign-up.html')


def sign_in(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.filter(name='Airport_admin').exists():
                login(request, user)
                return redirect('airport-index')
            elif user.groups.filter(name='Airline_admin').exists():
                login(request, user)
                return redirect('airline-index')
            else:
                login(request, user)
                return redirect('index')
        else:
            # display error message
            context = {'error': 'Invalid credentials'}
            return render(request, 'sign-in.html', context)

    else:
        return render(request, 'sign-in.html')


@user_passes_test(lambda u: is_in_group(u, 'Passenger'))
def account_profile(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')

        User.objects.filter(username=username).update(email=email)
        return redirect('accountprofile')

    return render(request, 'account-profile.html')


@user_passes_test(lambda u: is_in_group(u, 'Airport_admin'))
def admin_dashboard(request):
    with connection.cursor() as cursor:
        cursor.execute(" CALL update_flight_status() ")

    if request.method == 'POST':

        eid = request.POST.get('eid')
        with connection.cursor() as cursor:
            cursor.execute(" delete from Employee where EID = %s ", [eid])
        return redirect('airport-index')

    if request.method == 'GET':

        with connection.cursor() as cursor:
            cursor.execute(" select count(*) from Employee ")
            employee_count = cursor.fetchall()
            cursor.execute(" select count(*) from FlightLeg ")
            flight_count = cursor.fetchall()
            cursor.execute(" select count(*) from R_Seats ")
            seats_count = cursor.fetchall()
            cursor.execute(" select sum(Price) from Ticket ")
            income = cursor.fetchall()
            cursor.execute(
                " select count(*) from flights where Status = 'In-flight' ")
            boarded = cursor.fetchall()
            cursor.execute(
                " select count(*) from flights where Status = 'Scheduled' ")
            scheduled = cursor.fetchall()

            seats_available = (flight_count[0][0] * 72) - (seats_count[0][0])
            seats_sold = seats_count[0][0]
            pie_list = [seats_sold, seats_available]

            dash_dict = {'employees': employee_count[0][0], 'flights': flight_count[0][0],
                         'seats': seats_count[0][0], 'income': income[0][0],
                         'seats_available': seats_available, 'seats_sold': seats_sold,
                         'boarded': boarded[0][0], 'scheduled': scheduled[0][0],
                         'pie_list': pie_list
                         }

        return render(request, 'admin-dashboard.html', {'dash': dash_dict})


@user_passes_test(lambda u: is_in_group(u, 'Airport_admin'))
def admin_guest_list(request):

    with connection.cursor() as cursor:
        cursor.execute(" CALL update_flight_status() ")
        cursor.execute("SELECT * FROM Employee")
        employees = dictfetchall(cursor)
        cursor.execute(" select EID from crew_status ")
        status = list(cursor.fetchall())

        status_list = [i[0] for i in status]

    return render(request, 'admin-guest-list.html', {'employees': employees, 'status': status_list})


@ user_passes_test(lambda u: is_in_group(u, 'Airport_admin'))
def update_listing_minimal(request):
    EID = request.GET.get('eid')

    if request.method == 'GET':

        with connection.cursor() as cursor:
            cursor.execute("Select *from Employee where EID = %s", [EID])
            details = dictfetchall(cursor)[0]

        return render(request, 'update-listing-minimal.html', {'details': details})

    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        address = request.POST['address']
        salary = request.POST['salary']
        phone = request.POST['phone']
        DOB = request.POST['dob']
        dob = f"{DOB[6:]}-{DOB[3:5]}-{DOB[:2]}"

    with connection.cursor() as cursor:
        cursor.execute(
            "Update Employee set FName = %s, LName = %s, Address = %s, Salary = %s, Phone = %s, DOB = %s where EID = %s",
            [fname, lname, address, salary, phone, dob, EID]
        )

    return redirect('emp_list')


def log_out(request):
    logout(request)
    return redirect('index')


def error(request):
    return render(request, "error.html")
