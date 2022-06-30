#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
from datetime import datetime
from datetime import date
import hashlib

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='Pial@124578',
                       db='7projecttest',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for customer login
@app.route('/Customer-Login')
def customerLogin():
	return render_template('Customer-Login.html')

#Define route for register
@app.route('/Customer-Registration')
def customer_register():
	return render_template('Customer-Registration.html')

#Authenticates the register
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	name = request.form['name']
	phone = request.form['phone']
	email = request.form['email']
	password = request.form['password']
	buildingNumber = request.form['building-number']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	passportNumber = request.form['passport-number']
	passportExp = request.form['passport-expiration']
	passportCountry = request.form['passport-country']
	dateOfBirth = request.form['date-of-birth']
	print(request.form)
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	noDupEmailQuery = 'SELECT CustomerEmail FROM customer WHERE CustomerEmail = %s'
	cursor.execute(noDupEmailQuery, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		print('here')
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('Customer-Registration.html', error = error)
	else:
		#password = hashlib.md5(password.encode())
		ins = 'INSERT INTO customer VALUES(%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (name, email, password, int(buildingNumber), street, city, state, phone, passportNumber,passportExp, passportCountry, dateOfBirth))
		conn.commit()
		cursor.close()
		return render_template('index.html')


def isSessionLoggedIn(): 
	if len(session) > 0: 
		print(session)
		return True 
	return False

#Authenticates the login
@app.route('/CustomerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	#grabs information from the forms
	username = request.form['customer-username']
	password = request.form['customer-password']
	#username, password = get_cust_credentials()
	#print(username)
	#print(password)
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT CustomerEmail, CustomerPassword FROM customer WHERE CustomerEmail = %s and CustomerPassword = md5(%s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	
	sessionRunning = isSessionLoggedIn()
	if (sessionRunning == True): 
		error = 'Other users signed in. Please sign out of current session.'
		return render_template('Customer-Login.html', error=error)
	
	if(data):
		#print('data found')
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		#session['role'] = 'customer'
		return render_template('Customer-Home.html', name = username)
		#return redirect(url_for('Customer-Home'))
	else:
		#print("here")
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('Customer-Login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('username')
	#session.pop('role')
	print(session)
	return redirect('/')
	#return render_template('index.html')

@app.route('/Customer-Home')
def customerHome(): 
	username = session['username']
	return render_template('Customer-Home.html', name = session['username'])

@app.route('/View-Customer-Flights') #needs a query for this!!
def viewCustomerFlights():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus FROM Flight NATURAL JOIN updates NATURAL JOIN purchasedfor NATURAL JOIN ticket NATURAL JOIN customer WHERE CustomerEmail = %s AND DepartureDate > CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME) ORDER BY DepartureDate'
	cursor.execute(query, (username))
	data1 = cursor.fetchall() 
	for each in data1:
		print(each['AirlineName'])
		cursor.close()
	return render_template('View-Customer-Flights.html', custFlights=data1)

@app.route('/View-Customer-Flights-Variation')
def viewPastFlights(): 
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus FROM Flight NATURAL JOIN updates NATURAL JOIN purchasedfor NATURAL JOIN ticket NATURAL JOIN customer WHERE CustomerEmail = %s AND DepartureDate < CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime < CURRENT_TIME) ORDER BY DepartureDate'
	cursor.execute(query, (username))
	data1 = cursor.fetchall() 
	for each in data1:
		print(each['AirlineName'])
		cursor.close()
	return render_template('View-Customer-Flights-Variation.html', custFlights=data1)

@app.route('/Customer-Search-Flights') #needs a query for this!! 
def searchCustomerFlights(): 
	return render_template('Customer-Search-Flights.html')

@app.route('/Rate-my-Flights')
def rateCustomerFlights(): 
	return render_template('Rate-my-Flights.html')

@app.route('/RateFlightAuth', methods=['GET', 'POST'])
def rateFlightAuth(): 
	customerEmail = session['username']
	custTicketID = request.form['ticket-number']
	custRate = request.form['rate']
	custComment = request.form['comment']
	cursor = conn.cursor(); 
	print(request.form)
	checkCustFlightExist = 'SELECT FlightNumber, DepartureDate, DepartureTime FROM ticket NATURAL JOIN purchasedfor NATURAL JOIN customer WHERE CustomerEmail = %s AND TicketID = %s AND (CURRENT_DATE > DepartureDate OR (CURRENT_DATE = DepartureDate AND CURRENT_TIME > DepartureTime))'
	cursor.execute(checkCustFlightExist,(customerEmail, custTicketID))
	data1 = cursor.fetchone()
	print(data1)
	checkNoRate = 'SELECT FlightNumber, DepartureDate, DepartureTime, TicketID FROM suggested NATURAL JOIN ticket WHERE CustomerEmail = %s AND TicketID = %s'
	cursor.execute(checkNoRate, (customerEmail, custTicketID))
	data2 = cursor.fetchone()
	print(data2)
	print(data2)
	if(data1 and not(data2)): #customer was on the flight and there was no rating written 
		custFlightNum = data1['FlightNumber']
		custDeptDate = data1['DepartureDate']
		custDeptTime = data1['DepartureTime']
		ins = 'INSERT INTO suggested VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (customerEmail, custFlightNum, custDeptDate, custDeptTime, custComment, custRate))
		conn.commit()
		cursor.close()
		message = "Submitted Successfully! Click the back button to go home!"
		return render_template('Rate-my-Flights.html', message = message)
	elif (data2): 
		error = "Flight already given a rating"
		return render_template('Rate-my-Flights.html', error=error)
	else: 
		error = "Ticket ID does not exist or Departure Date in the Future"
		return render_template('Rate-my-Flights.html', error=error)
	
@app.route('/Customer-Track-Spending')
def customerTrackSpending(): 
	username = session['username']
	cursor = conn.cursor()
	getCustYearlySpending = 'SELECT SUM(SoldPrice) AS spend FROM ticket NATURAL JOIN purchasedfor WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR'
	cursor.execute(getCustYearlySpending, (username))
	yearSpend = cursor.fetchone()['spend']
	getCustMonthlySpending = 'SELECT MONTHNAME(PurchaseDate) AS month, SUM(soldPrice) as spent FROM ticket NATURAL JOIN purchasedfor WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 6 MONTH GROUP BY MONTHNAME(PurchaseDate)'
	cursor.execute(getCustMonthlySpending, (username))
	custMonthlySpending = cursor.fetchall() 
	labels = []
	months = {1:'January', 2: 'February', 3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
	from datetime import date
	currMonth = date.today().month
	earliest = currMonth-5
	for i in range(earliest,currMonth+1): 
		if i>0 and i<13: 
			labels.append(months[i])
		elif i < 1: 
			i += 12
			labels.append(months[i])
	values = []
	for elem in labels:
		added = False
		for i in range (len(custMonthlySpending)): 
			if custMonthlySpending[i]['month'] == elem: 
				values.append(custMonthlySpending[i]['spent'])
				added = True
				break
		if added == False: 
			values.append(0)
	maximumValue = max(values) + 10
	return render_template('Customer-Track-Spending.html', labels = labels, values = values, yearSpend = yearSpend, max = maximumValue)

@app.route('/Customer-Track-Spending-Custom', methods = ['GET', 'POST'])
def customerSpendingCustom(): 
	cursor = conn.cursor()
	#print(request.form)
	username = session['username']
	start_date = request.form['start-date1']
	#print(request.form)
	end_date = request.form['end-date1']
	getCustMonthlySpending = 'SELECT MONTHNAME(PurchaseDate) AS month, YEAR(PurchaseDate) AS year, SUM(soldPrice) as spent FROM ticket NATURAL JOIN purchasedfor WHERE CustomerEmail = %s AND PurchaseDate >= %s AND PurchaseDate <= %s GROUP BY MONTHNAME(PurchaseDate)'
	cursor.execute(getCustMonthlySpending, (username, start_date, end_date))
	custMonthlySpending = cursor.fetchall() 
	labels = []
	values = []
	for elem in custMonthlySpending: 
		date = str(elem['month']) + " " +str(elem['year'])
		labels.append(date)
		values.append(elem['spent'])
	maximumValue = max(values) + 10
	return render_template('Customer-Track-Spending-Custom.html', labels = labels, values = values, max = maximumValue)

@app.route('/View-Flights')
def viewFlightsPublic():
    #username = session['username']
    cursor = conn.cursor()
    query = 'SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, FlightStatus FROM Flight AS f NATURAL JOIN updates ORDER BY DepartureDate'
    cursor.execute(query)
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['AirlineName'])
    cursor.close()
    return render_template('View-Flights.html', flights=data1)

@app.route('/Customer-Search-Purchase-Flights', methods = ['GET', 'POST'])
def searchCustOneWayFlights(): 
	return render_template('Customer-Search-Flights.html')

@app.route('/Customer-View-One-Way-Flight-Search-Results', methods = ['GET', 'POST'])
def viewCustOneWayFlights(): 
	source_city = request.form['source-city-one']
	source_air = request.form['source-airport-one']
	dest_city = request.form['destination-city-one']
	dest_air = request.form['destination-airport-one']
	dept_date = request.form['departure-date-one']
	
	cursor = conn.cursor()
	oneWayFlights = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN updates AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport WHERE f.FlightNumber NOT IN (SELECT FlightNumber from flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND a1.AirportCity = %s AND f.DepartureAirport = %s AND a2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus HAVING booked < NumberOfSeats'
	cursor.execute(oneWayFlights, (source_city, source_air, dest_city, dest_air, dept_date))
	data1 = cursor.fetchall()
	print(data1)
	cursor.close()
	from datetime import date
	today = date.today()
	if dept_date < str(today): 
		error = "Date is in the past"
		data1 = ''
		return render_template('Customer-View-One-Way-Flights.html',flights=data1, error = error)
	elif (data1):
		return render_template('Customer-View-One-Way-Flights.html', flights=data1)
	else: 
		error = "No Flights Available"
		return render_template('Customer-View-One-Way-Flights.html',flights=data1, error = error)

@app.route('/Customer-View-Two-Way-Flight-Search-Results', methods = ['GET', 'POST'])
def viewCustTwoWayFlights(): 
	source_city = request.form['source-city-two']
	source_air = request.form['source-airport-two']
	dest_city = request.form['destination-city-two']
	dest_air = request.form['destination-airport-two']
	dept_date = request.form['departure-date-two']
	ret_date = request.form['return-date-two']
	
	cursor = conn.cursor()
	twoWayFlights = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f3.DepartureDate AS ReturnDate, f.DepartureTime, f3.DepartureTime AS ReturnTime, f.ArrivalDate, FlightStatus, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN updates AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport INNER JOIN flight AS f3 ON f.FlightNumber = f3.FlightNumber AND f.ArrivalAirport = f3.DepartureAirport WHERE f.FlightNumber IN (SELECT FlightNumber FROM flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND f3.DepartureDate > f.DepartureDate AND a1.AirportCity = %s AND f.DepartureAirport = %s AND a2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s AND f3.DepartureDate = %s GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.ArrivalDate, FlightStatus, ReturnDate, ReturnTime HAVING COUNT(ticketID) < NumberOfSeats'
	cursor.execute(twoWayFlights, (source_city, source_air, dest_city, dest_air, dept_date, ret_date))
	data1 = cursor.fetchall()
	cursor.close()
	from datetime import date
	today = date.today()
	print(data1)
	if dept_date < str(today): 
		error = "Date is in the past"
		data1 = ''
		return render_template('Customer-View-Two-Way-Flights.html',flights=data1, error = error)
	elif (data1):
		#print(data1)
		#booked = data1['booked']
		#numSeats = data1['numberOfSeats']
		return render_template('Customer-View-Two-Way-Flights.html', flights=data1)#, booked = booked, numSeats = numSeats)
	else: 
		error = "No Flights Available"
		return render_template('Customer-View-Two-Way-Flights.html',flights=data1, error = error)

@app.route('/Customer-Purchase-One-Way-Flight', methods = ['GET', 'POST'])
def custPurchaseOneWayFlight(): 
	flight_number = request.form['flight-number']
	dept_date = request.form['departure-date']
	dept_time = request.form['departure-time']
	cursor = conn.cursor()
	checkFlightHasSeats = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.BasePrice, f.ArrivalDate, f.ArrivalTime, f.ArrivalAirport, f.DepartureAirport, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN updates AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport WHERE f.FlightNumber NOT IN (SELECT FlightNumber from flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND f.DepartureDate = %s AND f.DepartureTime = %s AND f.FlightNumber = %s GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus HAVING booked < NumberOfSeats'
	cursor.execute(checkFlightHasSeats, (dept_date, dept_time, flight_number))
	data = cursor.fetchone()
	print(request.form)
	print(data)
	airline, arrival_date, arrival_airport, dept_air, arr_time = data['AirlineName'], data['ArrivalDate'], data['ArrivalAirport'], data['DepartureAirport'], data['ArrivalTime']
	totalBooked = data['booked']
	totalSeats = data['numberOfSeats']
	basePrice = data['BasePrice']
	if totalBooked/totalSeats >= 0.7: 
		basePrice *= 1.2 
	round_trip = "N/A"
	return render_template('Customer-Purchase-Tickets.html', airline = airline, flight_num = flight_number, dept_date = dept_date, dept_time = dept_time, arr_date = arrival_date, arr_time = arr_time, arr_air = arrival_airport, dept_air = dept_air, baseprice = basePrice, f1price = basePrice, round_trip = round_trip, bookingAgent = "NULL")

@app.route('/Customer-Purchase-Two-Way-Flight', methods = ['GET', 'POST'])
def custPurchaseTwoWayFlight(): 
	flight_number = request.form['flight-number']
	dept_date = request.form['departure-date']
	dept_time = request.form['departure-time']
	return_date = request.form['return-date']
	return_time = request.form['return-time']
	#num_seats = request.form['numSeats']
	#booked = request.form['booked']
	print(request.form)
	cursor = conn.cursor()
	#finding the number of flights booked, and total num of seats on each plane
	print("before Check Flight Seat")
	checkFlightSeats = 'SELECT f.FlightNumber, f.DepartureDate, f.DepartureTime, COUNT(ticketID) AS booked, numberOfSeats FROM flight AS f NATURAL JOIN airplane LEFT JOIN purchasedfor AS p ON f.DepartureDate = p.DepartureDate AND f.DepartureTime = p.DepartureTime AND f.FlightNumber = p.FlightNumber WHERE f.flightNumber = %s AND f.departureDate = %s AND f.departureTime = %s GROUP BY  f.FlightNumber, f.DepartureDate, f.DepartureTime, numberOfSeats'
	cursor.execute(checkFlightSeats, (flight_number, dept_date, dept_time))
	
	flight1Seats = cursor.fetchone()
	print(flight1Seats)
	flight1SeatsBooked, flight1TotalSeats = flight1Seats['booked'], flight1Seats['numberOfSeats']
	from datetime import date
	if flight1SeatsBooked/flight1TotalSeats == 1 or flight1Seats['DepartureDate'] < date.today(): 
		error = "Flight fully booked or Departure Date is in the Past"
		return render_template('Customer-Purchase-Tickets.html', error = error)
	cursor.execute(checkFlightSeats, (flight_number, return_date, return_time))
	flight2Seats = cursor.fetchone()
	flight2SeatsBooked, flight2TotalSeats = flight2Seats['booked'], flight2Seats['numberOfSeats']

	#don't need the check flights has seats, because we checked in the previous query
	checkFlightPrice = 'SELECT * FROM flight WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime =%s'
	cursor.execute(checkFlightPrice, (flight_number, dept_date, dept_time))
	flight1Price = cursor.fetchone()
	airline, arrival_date, arr_time, arr_air = flight1Price['AirlineName'], flight1Price['ArrivalDate'], flight1Price['ArrivalTime'], flight1Price['ArrivalAirport']
	basePrice1 = flight1Price['BasePrice']
	cursor.execute(checkFlightPrice, (flight_number, return_date, return_time))
	flight2Price = cursor.fetchone()
	dept_air = flight2Price['DepartureAirport']
	basePrice2 = flight2Price['BasePrice']
	#airline, arrival_date, arrival_airport, dept_air, arr_time = data['AirlineName'], data['ArrivalDate'], data['ArrivalAirport'], data['DepartureAirport'], data['ArrivalTime']
	if flight1SeatsBooked/flight1TotalSeats >= 0.7: 
		basePrice1 *= 1.2 
	if flight2SeatsBooked/flight2TotalSeats >= 0.7: 
		basePrice2 *= 1.2 
	basePrice = basePrice1 + basePrice2
	round_trip = "Returning Flight: \nReturn Date: " + str(return_date) + "\nReturn Time: " + str(return_time)
	return render_template('Customer-Purchase-Tickets.html', airline = airline, flight_num = flight_number, dept_date = dept_date, dept_time = dept_time, arr_date = arrival_date, arr_time = arr_time, arr_air = arr_air, dept_air = dept_air, baseprice = basePrice, f1price = basePrice1, f2price = basePrice2, round_trip = round_trip, bookingAgent = "NULL")

@app.route('/Customer-Enter-Card-Info', methods = ['GET', 'POST'])
def custEnterCardInfo(): 
	username = session['username'] 
	card_num = request.form['card-number']
	card_name = request.form['card-name']
	exp_month = request.form['card-month']
	exp_year = request.form['card-year']
	card_type = request.form['card-type']
	cust_username = request.form['cust-username']
	if cust_username == username: 
		cust_username = username
		booking_agent = 'NULL'
	else: 
		booking_agent = username
	import datetime
	cursor = conn.cursor()
	#card_exp = "01-" + str(exp_month) + "-" + str(exp_year)
	card_exp = str(exp_year) + "-" + str(exp_month) + "-01"
  	#datetime.datetime.strptime(card_exp, '%d-%m-%y')
	checkCardExists = 'SELECT * FROM cardinfo WHERE cardNumber = %s'
	print(card_exp)
	#cursor = conn.cursor()
	cursor.execute(checkCardExists, (card_num))
	data = cursor.fetchone()
	if (data): 
		print('Card in system. Just add the flight info + ticket')
	else: 
		insCard = 'INSERT INTO cardinfo VALUES(%s, %s, %s, %s)'
		cursor.execute(insCard, (card_num, card_type, card_name, card_exp))
		insPersonalInfo = 'INSERT INTO providespersonalinfo VALUES (%s, %s)'
		cursor.execute(insPersonalInfo, (card_num, cust_username))
	#finding the max ticket number from sql so we can generate another new ticket number 

	findMaxTicketNumber = 'SELECT MAX(CAST(TicketID AS INT)) AS currTicket FROM ticket'
	cursor.execute(findMaxTicketNumber)
	maxTicket = cursor.fetchone()['currTicket']
	print(maxTicket)
	if maxTicket == None: 
		maxTicket = 0
	ticketNumber = int(maxTicket) + 1

	#finding airline name, flight number, sold price, which is stored in session
	#print(request.form)
	print(request.form)
	airline = request.form['airline']
	flight_number = request.form['flight-number']
	price = request.form['price']
	dept_date = request.form['dept-date']
	dept_time = request.form['dept-time']
	round_trip = request.form['round-trip']
	#booking_agent = request.form['bookingagent']
	base_price_1 = request.form['base-price-1']
	base_price_2 = request.form['base-price-2']
	from datetime import date
	from datetime import datetime
	today = date.today()
	now = datetime.now()
	print("compared dates")
	insTicket = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(insTicket, (ticketNumber, cust_username, airline, flight_number, base_price_1, today, now, booking_agent))
	print("ins ticket")
	#ins into payment method
	insPaymentMethod = 'INSERT INTO paymentmethod VALUES (%s, %s)'
	cursor.execute(insPaymentMethod, (card_num, ticketNumber))
	insPurchasedFor = 'INSERT INTO purchasedfor VALUES (%s, %s, %s, %s)'
	print(flight_number,dept_date,dept_time)
	cursor.execute(insPurchasedFor, (ticketNumber, flight_number, dept_date, dept_time))
	if booking_agent != "NULL": 
		insCommission = 'INSERT INTO creates VALUES (%s, %s, %s)'
		comAmount = float(base_price_1) * 0.1
		cursor.execute(insCommission, (booking_agent, ticketNumber, comAmount))

	#check if this is a round trip flight
	if round_trip != "N/A": #that means that this is a round trip flight 

		ticketNumber += 1 #ticket number will be unique so we will increment 1
		insRoundTripTicket = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(insTicket, (ticketNumber, cust_username, airline, flight_number, base_price_2, today, now, booking_agent))
		#ins into payment method
		insPaymentMethod = 'INSERT INTO paymentmethod VALUES (%s, %s)'
		cursor.execute(insPaymentMethod, (card_num, ticketNumber))
		#query for round trip (flight 2)
		queryRoundTripFlight = 'SELECT * FROM flight WHERE FlightNumber = %s AND (DepartureDate <> %s OR DepartureTime <> %s)'
		cursor.execute(queryRoundTripFlight, (flight_number, dept_date, dept_time))
		complement = cursor.fetchone()
		print(flight_number, dept_date, dept_time)
		print(complement)
		roundDeptDate = complement['DepartureDate']
		roundDeptTime = complement['DepartureTime']
		#ins into purchased for
		insPurchasedFor = 'INSERT INTO purchasedfor VALUES (%s, %s, %s, %s)'
		cursor.execute(insPurchasedFor, (ticketNumber, flight_number, roundDeptDate, roundDeptTime))
		if booking_agent != "NULL": 
			insCommission = 'INSERT INTO creates VALUES (%s, %s, %s)'
			comAmount = float(base_price_2) * 0.1
			cursor.execute(insCommission, (booking_agent, ticketNumber, comAmount))

	conn.commit()
	if booking_agent == "NULL": 
		return render_template('Customer-Home.html', name = cust_username)
	else: 
		return render_template('Booking-Agent-Home.html', username = username)
	#MIGHT NOT BE DONE

@app.route('/Search-One-Way-Flights-Public', methods = ['GET', 'POST'])
def viewOneWayFlightsPublic(): 
	source_city = request.form['source-city-one']
	source_air = request.form['source-airport-one']
	dest_city = request.form['destination-city-one']
	dest_air = request.form['destination-airport-one']
	dept_date = request.form['departure-date-one']
	
	cursor = conn.cursor()
	oneWayFlights = 'SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, FlightStatus FROM Flight AS f NATURAL JOIN updates INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport WHERE a1.AirportCity = %s AND f.DepartureAirport = %s AND a2.AirportCity = %s AND f.ArrivalAirport = %s AND DepartureDate = %s AND DepartureDate > CURRENT_DATE AND f.FlightNumber NOT IN (SELECT FlightNumber FROM flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1)'
	cursor.execute(oneWayFlights, (source_city, source_air, dest_city, dest_air, dept_date))
	data1 = cursor.fetchall()
	cursor.close()
	return render_template('Customer-View-One-Way-Flights.html', flights=data1, public = 'true')

@app.route('/Search-Round-Trip-Public', methods = ['GET', 'POST'])
def viewRoundTripFlightsPublic(): 
	source_city = request.form['source-city-two']
	source_air = request.form['source-airport-two']
	dest_city = request.form['destination-city-two']
	dest_air = request.form['destination-airport-two']
	dept_date = request.form['departure-date-two']
	ret_date = request.form['return-date-two']
	
	cursor = conn.cursor()
	twoWayFlights = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f3.DepartureDate AS ReturnDate, f.DepartureTime, f3.DepartureTime AS ReturnTime, f.ArrivalDate, FlightStatus, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN updates AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport INNER JOIN flight AS f3 ON f.FlightNumber = f3.FlightNumber AND f.ArrivalAirport = f3.DepartureAirport WHERE f.FlightNumber IN (SELECT FlightNumber FROM flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND f3.DepartureDate > f.DepartureDate AND a1.AirportCity = %s AND f.DepartureAirport = %s AND a2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s AND f3.DepartureDate = %s AND f.DepartureDate > CURRENT_DATE GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.ArrivalDate, FlightStatus, ReturnDate, ReturnTime HAVING COUNT(ticketID) < NumberOfSeats'
	cursor.execute(twoWayFlights, (source_city, source_air, dest_city, dest_air, dept_date, ret_date))
	data1 = cursor.fetchall()
	cursor.close()
	from datetime import date
	today = date.today()
	if dept_date < str(today): 
		error = "Date is in the past"
		data1 = ''
		return render_template('Public-Two-Way-FLights.html',flights=data1, error = error)
	elif (data1):
		#print(data1)
		#booked = data1['booked']
		#numSeats = data1['numberOfSeats']
		return render_template('Public-Two-Way-FLights.html', flights=data1)#, booked = booked, numSeats = numSeats)
	else: 
		error = "No Flights Available"
		return render_template('Public-Two-Way-FLights.html',flights=data1, error = error)
	pass 

@app.route('/Search-Flights-Public')
def searchFlights():
	return render_template('Search-Flights-Public.html')

#Define route for booking agent login
@app.route('/Booking-Agent-Login')
def bookingAgentlogin():
	return render_template('Booking-Agent-Login.html')

@app.route('/BookingAgentLoginAuth', methods=['GET', 'POST'])
def bookingAgentLoginAuth():
	#grabs information from the forms
	username = request.form['agent-email-login']
	password = request.form['agent-password']
	agent_id = request.form['agent-id']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT AgentEmail, AgentPassword, AgentID FROM bookingagent WHERE AgentEmail = %s and AgentPassword = md5(%s) AND AgentID = %s'
	cursor.execute(query, (username, password, agent_id))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	
	sessionRunning = isSessionLoggedIn()
	if (sessionRunning == True): 
		error = 'Other users signed in. Please sign out of current session.'
		return render_template('Booking-Agent-Login.html', error=error)
	
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		#session['role'] = 'booking agent'
		return render_template('Booking-Agent-Home.html', username = session['username'])
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('Booking-Agent-Login.html', error=error)

@app.route('/Booking-Agent-Home', methods=['GET', 'POST'])
def bookingAgentHome(): 
	username = session['username']
	return render_template('Booking-Agent-Home.html', username = session['username'])

@app.route('/Booking-Agent-View-Customer-Flights-first')
def bookingAgentViewCustFlights(): 
	'''
	username = 0
	cursor = conn.cursor()
	#executes query
	query = 'SELECT AirlineName, FlightNumber, DepartureDate, ArrivalDate, FlightStatus FROM ticket NATURAL JOIN purchasedfor NATURAL JOIN customer NATURAL JOIN flight NATURAL JOIN updates WHERE CustomerEmail = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data1 = cursor.fetchall() #this should be empty 
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	'''
	return render_template('Booking-Agent-View-Customer-Flights-first.html')

@app.route('/Booking-Agent-View-Customer-Flights-second', methods=['GET','POST'])
def bookingAgentViewCustFlightssecond(): 
	#print("here")
	username = request.form['customer-username']
	print(username)
	cursor = conn.cursor()
	queryUser = 'SELECT customeremail FROM customer WHERE customeremail = %s'
	cursor.execute(queryUser, (username))
	userData = cursor.fetchone()
	#executes query
	print(userData)
	if(userData): 
		print("user data found")
		query = 'SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus FROM ticket NATURAL JOIN purchasedfor NATURAL JOIN customer NATURAL JOIN flight NATURAL JOIN updates WHERE CustomerEmail = %s'
		cursor.execute(query, (username))
		#stores the results in a variable
		data1 = cursor.fetchall()
		print(data1) 
		#use fetchall() if you are expecting more than 1 data row
		cursor.close()
		error = None
		return render_template('Booking-Agent-View-Customer-Flights-second.html', flights=data1, error = error)
	else:
		data1= ""
		#print("here error")
		error = "User does not exist" 
		return render_template('Booking-Agent-View-Customer-Flights-second.html', flights = data1, error = error)#, flights=data1, error = error)


@app.route('/Booking-Agent-Registration')
def booking_agent_register():
	return render_template('Booking-Agent-Registration.html')

@app.route('/BookingAgentRegisterAuth', methods=['GET', 'POST'])
def bookingAgentRegisterAuth():
	#grabs information from the forms
	agent_id= request.form['agent-id']
	email = request.form['email']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	noExistingUserQuery = 'SELECT AgentEmail FROM bookingagent WHERE AgentEmail = %s'
	cursor.execute(noExistingUserQuery, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('Booking-Agent-Registration.html', error = error)
	else:
		ins = 'INSERT INTO bookingagent VALUES(%s, md5(%s), %s)'
		cursor.execute(ins, (email, password, agent_id))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/Booking-Agent-Top-Customers')
def topCusts(): 
	username = session['username']
	cursor = conn.cursor()
	#topCusts = 'SELECT customerEmail, SUM(CommissionAmount) AS commission FROM customer NATURAL JOIN ticket NATURAL JOIN creates WHERE agentemail = %s GROUP BY customerEmail ORDER BY commission DESC LIMIT 5'
	topCustsTicket = 'SELECT customerEmail, COUNT(ticketID) AS tickets FROM customer NATURAL JOIN ticket NATURAL JOIN creates WHERE agentemail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 6 MONTH  GROUP BY customerEmail ORDER BY COUNT(ticketID) DESC LIMIT 5'
	cursor.execute(topCustsTicket, (username))
	custsByTicket = cursor.fetchall()
	#print(custsByTicket)
	labels = [] 
	values = []
	for elem in custsByTicket: 
		key = elem['customerEmail']
		#for key in elem: 
		labels.append(key)
		value = elem['tickets']
		values.append(value)
	print(labels,values)

	topCustsCommission = 'SELECT customerEmail, SUM(commissionAmount) AS commission FROM customer NATURAL JOIN ticket NATURAL JOIN creates WHERE agentemail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR  GROUP BY customerEmail ORDER BY SUM(commissionAmount) DESC LIMIT 5'
	cursor.execute(topCustsCommission, (username))
	custsByCommission = cursor.fetchall()
	custs = []
	commission = []
	for elem in custsByCommission: 
		key = elem['customerEmail']
		custs.append(key)
		coms = elem['commission']
		commission.append(coms)
	print(custs, commission)

	cursor.close()
	return render_template('Booking-Agent-Top-Customers.html',  title='Top Customers by Commission', max=50, labels=labels, values=values, custs = custs, commission = commission, max1= 200)

@app.route('/View-Commissions')
def view_commissions_main(): 
	username = session['username']
	cursor = conn.cursor() 
	statistics = 'SELECT SUM(commissionAmount) AS totalcom, SUM(commissionAmount)/COUNT(*) as avgcom, COUNT(ticketID) AS numtickets FROM creates NATURAL JOIN ticket WHERE AgentEmail = %s AND CURRENT_DATE - 30 <= purchaseDate'
	cursor.execute(statistics, (username))
	comStats = cursor.fetchone() 
	print(comStats)
	cursor.close()
	return render_template("View-Commissions.html", stats = comStats)

@app.route('/Booking-Agent-Date-Coms', methods=['GET', 'POST'])
def bookingAgentDatesCommissions(): 
	start_date = request.form['start-date']
	end_date = request.form['end-date']
	username = session['username']
	cursor = conn.cursor() 
	statistics = 'SELECT SUM(commissionAmount) AS totalcom, SUM(commissionAmount)/COUNT(*) as avgcom, COUNT(ticketID) AS numtickets FROM creates NATURAL JOIN ticket WHERE AgentEmail = %s AND PurchaseDate >= %s AND PurchaseDate <= %s'
	cursor.execute(statistics, (username, start_date, end_date))
	comStats = cursor.fetchone() 
	cursor.close()
	return render_template('Booking-Agent-Date-Coms.html', stats = comStats, given_start_date = start_date, given_end_date = end_date)

@app.route('/Airline-Staff-Login')
def AirlineStafflogin():
	return render_template('Airline-Staff-Login.html')

@app.route('/AirlineStaffLoginAuth', methods=['GET', 'POST'])
def AirlineStaffLoginAuth():
	#grabs information from the forms
	username = request.form['airline-staff-username']
	password = request.form['airline-staff-password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT Username, StaffPassword FROM airlinestaff WHERE Username = %s and StaffPassword = md5(%s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	
	sessionRunning = isSessionLoggedIn()
	if (sessionRunning == True): 
		error = 'Other users signed in. Please sign out of current session.'
		return render_template('Airline-Staff-Login.html', error=error)
	
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		#session['role'] = 'airline staff'
		return render_template('Airline-Staff-Home.html')
		#return redirect(url_for('Airline-Staff-Home'))
		#return redirect(url_for('viewFlightsPublic'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('Airline-Staff-Login.html', error=error)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/Airline-Staff-Home')
def airline_staff_home(): 
	username = session['username']
	return render_template('Airline-Staff-Home.html')
	#return redirect(url_for('Airline-Staff-Home'))

@app.route('/Airline-Staff-Registration')
def airline_staff_register():
	return render_template('Airline-Staff-Registration.html')

#Authenticates the register
@app.route('/AirlineStaffRegisterAuth', methods=['GET', 'POST'])
def airlineStaffRegisterAuth():
	print(request.form)
	#grabs information from the forms
	fname = request.form['first-name']
	lname = request.form['last-name']
	username = request.form['username']
	password = request.form['password']
	dob = request.form['date-of-birth']
	airline = request.form['airline']
	phone_numbers = request.form['phone-numbers']
	staffPhoneNumbersList = phone_numbers.split(";")
	print(staffPhoneNumbersList)

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	noExistingUserQuery = 'SELECT username FROM airlinestaff WHERE username = %s'
	cursor.execute(noExistingUserQuery, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('Airline-Staff-Registration.html', error = error)
	else:
		ins = 'INSERT INTO airlinestaff VALUES(%s, md5(%s), %s, %s, %s, %s)'
		cursor.execute(ins, (username, password, fname, lname, dob, airline))
		for elem in staffPhoneNumbersList: 
			getPhoneNumber = 'SELECT * FROM phonenumber WHERE Username = %s AND AirlineStaffPhoneNumber = %s'
			cursor.execute(getPhoneNumber, (username, elem.strip()))
			data = cursor.fetchone()
			if(data): 
				pass 
			else: 
				insPhoneNumber = 'INSERT INTO phonenumber VALUES (%s, %s)'
				cursor.execute(insPhoneNumber, (username, elem.strip()))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/Airline-Staff-View-Flights', methods = ['GET','POST'])
def airline_staff_view_flights(): 
	username = session['username']
	cursor = conn.cursor() 
	findAirlineName = 'SELECT AirlineName FROM airlinestaff WHERE Username = %s'
	cursor.execute(findAirlineName, (username))
	airlineName = cursor.fetchone()
	currAirlineName = airlineName['AirlineName']
	findFlights = 'SELECT DISTINCT FlightNumber, DepartureDate, DepartureTime, DepartureAirport, ArrivalDate, ArrivalTime FROM airlinestaff NATURAL JOIN flight WHERE AirlineName = %s AND (DepartureDate <= CURRENT_DATE + INTERVAL 30 DAY AND (DepartureDate > CURRENT_DATE)) OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME) ORDER BY DepartureDate ASC'
	cursor.execute(findFlights, (currAirlineName))
	data = cursor.fetchall()
	cursor.close()
	return render_template('Airline-Staff-View-Flights.html', flights = data)

@app.route('/Airline-Staff-View-Flights-Custom-Date', methods = ['GET','POST'])
def view_flights_custom_date(): 
	start_date = request.form['start-date']
	end_date = request.form['end-date']
	cursor = conn.cursor() 
	username = session['username']
	findAirlineName = 'SELECT AirlineName FROM airlinestaff WHERE Username = %s'
	cursor.execute(findAirlineName, (username))
	airlineName = cursor.fetchone()['AirlineName']
	findFlights = 'SELECT FlightNumber, DepartureDate, DepartureTime FROM flight WHERE airlineName = %s AND (DepartureDate > %s AND DepartureDate < %s OR DepartureDate = %s)'
	cursor.execute(findFlights, (airlineName, start_date, end_date, start_date))
	data = cursor.fetchall()
	cursor.close()
	if (data): 
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data)
	else: 
		error = "No flights found"
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data, error = error)

@app.route('/Airline-Staff-View-Flights-Custom-City',methods = ['GET','POST'])
def view_flights_custom_city(): 
	city = request.form['city-name']
	username = session['username']
	cursor = conn.cursor()
	findAirlineName = 'SELECT AirlineName FROM airlinestaff WHERE Username = %s'
	cursor.execute(findAirlineName, (username))
	airlineName = cursor.fetchone()['AirlineName']
	findFlights = 'SELECT FlightNumber, DepartureDate, DepartureTime FROM flight AS f INNER JOIN airport AS a ON f.ArrivalAirport = a.AirportName INNER JOIN airport AS a2 ON f.DepartureAirport = a2.AirportName WHERE airlineName = %s AND (a.airportCity = %s OR a2.airportCity = %s) ORDER BY arrivalDate'
	cursor.execute(findFlights, (airlineName, city, city))
	data = cursor.fetchall()
	cursor.close()
	if data: 
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data)
	else: 
		error = "No flights found"
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data, error = error)

@app.route('/Airline-Staff-View-Flights-Custom-Source-Airport', methods = ['GET', 'POST'])
def view_flights_source_airport(): 
	source_airport = request.form['source-airport']
	username = session['username']
	cursor = conn.cursor()
	findAirlineName = 'SELECT AirlineName FROM airlinestaff WHERE Username = %s'
	cursor.execute(findAirlineName, (username))
	airlineName = cursor.fetchone()['AirlineName']
	findSourceAirport = 'SELECT FlightNumber, DepartureDate, DepartureTime FROM flight WHERE airlineName = %s AND DepartureAirport = %s'
	cursor.execute(findSourceAirport, (airlineName, source_airport))
	data = cursor.fetchall()
	cursor.close()
	if data: 
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data)
	else: 
		error = "No flights found"
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data, error = error)

@app.route('/Airline-Staff-View-Flights-Custom-Destination-Airport', methods = ['GET', 'POST'])
def view_flights_destination_airport(): 
	destination_airport = request.form['destination-airport']
	username = session['username']
	cursor = conn.cursor()
	findAirlineName = 'SELECT AirlineName FROM airlinestaff WHERE Username = %s'
	cursor.execute(findAirlineName, (username))
	airlineName = cursor.fetchone()['AirlineName']
	findDestinationAirport = 'SELECT FlightNumber, DepartureDate, DepartureTime FROM flight WHERE airlineName = %s AND ArrivalAirport = %s'
	cursor.execute(findDestinationAirport, (airlineName, destination_airport))
	data = cursor.fetchall()
	cursor.close()
	if data: 
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data)
	else: 
		error = "No flights found"
		return render_template('Airline-Staff-View-Flights-Custom.html', flights = data, error = error)

@app.route('/Airline-Staff-View-Flight-Customers', methods = ['GET', 'POST'])
def airline_staff_view_flight_customers(): 
	username = session['username']
	cursor = conn.cursor()
	flightNumber = request.form['flight-number']
	departure_date = request.form['departure-date']
	departure_time = request.form['departure-time']
	findAirlineName = 'SELECT AirlineName FROM airlinestaff WHERE Username = %s'
	cursor.execute(findAirlineName, (username))
	airlineName = cursor.fetchone()['AirlineName']
	findCustomers = 'SELECT DISTINCT customerEmail FROM ticket NATURAL JOIN purchasedfor WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s AND AirlineName = %s'
	cursor = conn.cursor()
	cursor.execute(findCustomers, (flightNumber, departure_date, departure_time, airlineName))
	customers = cursor.fetchall()
	cursor.close()
	return render_template('Airline-Staff-View-Customer-On-Flight.html', customers = customers, flightNumber = flightNumber, dept_date = departure_date, dept_time = departure_time)

@app.route('/Airline-Staff-Top-Agents-Frequent-Customers')
def top_agent_frequent_cust(): 
	cursor = conn.cursor()
	findTopAgentMonth = 'SELECT AgentEmail, COUNT(*) AS ticketSold FROM ticket NATURAL JOIN creates WHERE purchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH GROUP BY AgentEmail ORDER BY COUNT(AgentID) DESC LIMIT 5'
	cursor.execute(findTopAgentMonth)
	topAgentMonth = cursor.fetchall()
	findTopAgentYear = 'SELECT AgentEmail, COUNT(*) AS ticketSold FROM ticket NATURAL JOIN creates WHERE purchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR GROUP BY AgentEmail ORDER BY COUNT(AgentID) DESC LIMIT 5'
	cursor.execute(findTopAgentYear)
	topAgentYear = cursor.fetchall()
	findTopAgentComsYear = 'SELECT AgentEmail, SUM(commissionAmount) AS commission FROM ticket NATURAL JOIN creates WHERE purchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR GROUP BY AgentEmail ORDER BY commission DESC LIMIT 5'
	cursor.execute(findTopAgentComsYear)
	topAgentYearComs = cursor.fetchall()
	username = session['username']
	staffAirline = 'SELECT AirlineName FROM airlinestaff WHERE username = %s'
	cursor.execute(staffAirline, (username))
	staffAirlineName = cursor.fetchone()['AirlineName']
	print(staffAirlineName)
	findTopCustomer = 'SELECT CustomerEmail, COUNT(*) AS numFlights FROM ticket WHERE AirlineName = %s AND purchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR GROUP BY CustomerEmail ORDER BY numFlights DESC LIMIT 1'
	cursor.execute(findTopCustomer, (staffAirlineName))
	topCustomer = cursor.fetchone()
	cursor.close()
	return render_template('Airline-Staff-Top-Agents-Frequent-Customers.html', topAgentMonth = topAgentMonth, topAgentYear = topAgentYear, topAgentYearComs = topAgentYearComs, topCustomer = topCustomer)

@app.route('/Airline-Staff-View-Customer-Flights', methods = ["GET", 'POST'])
def airline_staff_view_cust_flights(): 
	custEmail = request.form["customer-email"]
	cursor = conn.cursor()
	username = session['username']
	staffAirline = 'SELECT AirlineName FROM airlinestaff WHERE username = %s'
	cursor.execute(staffAirline, (username))
	staffAirlineName = cursor.fetchone()['AirlineName']
	getFlights = 'SELECT FlightNumber, DepartureDate, DepartureTime FROM Flight NATURAL JOIN updates NATURAL JOIN purchasedfor NATURAL JOIN ticket NATURAL JOIN customer WHERE CustomerEmail = %s AND airlineName = %s ORDER BY DepartureDate'
	cursor.execute(getFlights, (custEmail, staffAirlineName))
	custFlights = cursor.fetchall()
	cursor.close()
	if custFlights: 
		return render_template('Airline-Staff-View-Customer-Flights.html', custFlights = custFlights, custEmail = custEmail)
	else: 
		error = "Customer Not Found, please go back to homepage"
		return render_template('Airline-Staff-View-Customer-Flights.html', error = error)

@app.route('/Airline-Staff-Create')
def airline_staff_create(): 
	return render_template('Airline-Staff-Create.html')


@app.route('/Airline-Staff-Create-Flight', methods = ['GET', 'POST'])
def airline_staff_create_flight(): 
	airline_name = request.form["fl-airline-name"]
	flight_number = request.form["fl-flight-number"]
	departure_air = request.form["fl-dept-airport"]
	departure_date = request.form["fl-dept-date"]
	departure_time = request.form["fl-dept-time"] #input type = 'time'
	arrival_air = request.form["fl-arr-airport"]
	arrival_date = request.form["fl-arr-date"]
	arrival_time = request.form["fl-arr-time"]
	base_price = request.form["price"]
	airplane_id = request.form["fl-airplane-id"]
	
	#primary key for flight is deptDate, deptTime, flightNum
	cursor = conn.cursor() 
	noExistFlight = 'SELECT * FROM flight WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(noExistFlight, (flight_number, departure_date, departure_time))
	data = cursor.fetchone()

	if(data): #if exists
		error = "Flight not added. Flight Already Exists"
		return render_template('Failure.html', error = error)
	else: 
		ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (airline_name, departure_date, departure_time, flight_number, departure_air, arrival_air, arrival_date, arrival_time, base_price, airplane_id))
		#conn.commit()
		insArrives = 'INSERT INTO arrives VALUES (%s, %s, %s, %s)'
		cursor.execute(insArrives, (arrival_air, flight_number, departure_date, departure_time))
		#conn.commit() 
		insDeparts = 'INSERT INTO departs VALUES (%s, %s, %s, %s)'
		cursor.execute(insDeparts, (departure_air, flight_number, departure_date, departure_time))
		#conn.commit()
		username = session['username']
		insUpdates = 'INSERT INTO updates VALUES (%s, %s, %s, %s, %s)'
		cursor.execute(insUpdates, (username, flight_number, departure_date, departure_time, 'On Time'))
		conn.commit()
		cursor.close()
		error = "Flight successfully added."
		return render_template('Success.html', error = error)

@app.route('/Update-Flight-Status', methods = ['GET', 'POST'])
def update_flight_status():
	username = session['username'] 
	flight_number = request.form['up-flight-number']
	departure_date = request.form['up-dept-date']
	departure_time = request.form['up-dept-time']
	flight_status = request.form['up-flight-status']

	cursor = conn.cursor()
	flightExists = 'SELECT * FROM updates WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(flightExists, (flight_number, departure_date, departure_time))
	data = cursor.fetchone()
	if(data): 
		updateFlight = 'UPDATE updates SET FlightStatus = %s, Username = %s WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
		cursor.execute(updateFlight, (flight_status, username, flight_number, departure_date, departure_time))
		conn.commit() 
		cursor.close()
		error = "Flight Status Updated Successfully"
		return render_template("Success.html", error = error)
	else: 
		error = 'Update Flight Status Failed. Flight does not exist'
		return render_template("Failure.html", error = error)

@app.route('/Add-Airplane', methods = ['GET', 'POST'])
def add_airplane(): 
	airline_name = request.form['air-airline-name']
	airplane_id = request.form['air-airplane-ID']
	num_seats = request.form['air-num-seats']

	cursor = conn.cursor() 
	airplaneDNE = 'SELECT * FROM airplane WHERE AirlineName = %s AND AirplaneID = %s'
	cursor.execute(airplaneDNE, (airline_name, airplane_id))
	data = cursor.fetchone()
	if(data): 
		error = 'Airplane not added. Airplane already exists'
		return render_template('Failure.html', error=error)
	else: 
		addAirplane = 'INSERT INTO airplane VALUES(%s, %s, %s)'
		cursor.execute(addAirplane, (airline_name, airplane_id, num_seats))
		getAirplanes = 'SELECT * FROM airplane WHERE airlineName = %s'
		cursor.execute(getAirplanes, (airline_name))
		airplanes = cursor.fetchall()
		conn.commit()
		cursor.close()
		error = "Airplane added successfully"
		return render_template('Airplanes-in-Airline.html', airline_name = airline_name, airplanes = airplanes, airlineName = airline_name)

@app.route('/Add-Airport', methods = ['GET', 'POST'])
def add_airport(): 
	airport_name = request.form['airport-name']
	airport_city = request.form['airport-city']

	cursor = conn.cursor()
	airportDNE = 'SELECT * FROM airport WHERE AirportName = %s'
	cursor.execute(airportDNE, (airport_name))
	data = cursor.fetchone()
	if(data): 
		error = 'Airport not added. Airport already exists'
		return render_template('Failure.html', error = error)
	else: 
		addAirport = 'INSERT INTO airport VALUES(%s, %s)'
		cursor.execute(addAirport, (airport_name, airport_city))
		conn.commit()
		cursor.close()
		error = 'Airport successfully added'
		return render_template('Success.html', error = error)

@app.route('/Airline-Staff-Rating-Destination-Revenue')
def rate_dest_rev():
	username = session['username']
	cursor = conn.cursor()
	getAirlineName = 'SELECT AirlineName FROM airlinestaff WHERE username = %s'
	cursor.execute(getAirlineName, (username))
	airline_name = cursor.fetchone()
	getAvgRatings = 'SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, AVG(Rate) as averageRating FROM suggested NATURAL JOIN Flight WHERE AirlineName = %s GROUP BY AirlineName, FlightNumber, DepartureDate, DepartureTime' 
	cursor.execute(getAvgRatings, (airline_name['AirlineName']))
	avgRatings = cursor.fetchall()
	conn.commit()

	getTopThreeDest = 'SELECT AirportCity FROM ticket NATURAL JOIN purchasedfor NATURAL JOIN flight INNER JOIN airport ON arrivalAirport = airport.AirportName WHERE AirlineName = %s AND arrivalDate >= CURRENT_DATE - INTERVAL 3 MONTH  GROUP BY AirportName ORDER BY COUNT(airportName) DESC LIMIT 3'
	cursor.execute(getTopThreeDest, (airline_name['AirlineName']))
	topThreeDests = cursor.fetchall()
	conn.commit() 
	if len(topThreeDests) < 3: 
		n1 = len(topThreeDests)
	else: 
		n1 = 3

	getTopDestYear = 'SELECT AirportCity FROM ticket NATURAL JOIN purchasedfor NATURAL JOIN flight INNER JOIN airport ON arrivalAirport = airport.AirportName WHERE AirlineName = %s AND arrivalDate >= CURRENT_DATE - INTERVAL 1 YEAR GROUP BY AirportName ORDER BY COUNT(airportName) DESC LIMIT 3'
	cursor.execute(getTopDestYear, (airline_name['AirlineName']))
	topDestYear = cursor.fetchall()
	conn.commit()
	cursor.close()
	if len(topDestYear) < 3: 
		n2 = len(topDestYear)
	else: 
		n2 = 3
	return render_template('Airline-Staff-Rating-Destination-Revenue.html', avgRatings = avgRatings, topThreeDests = topThreeDests, n1 = int(n1), n2 = int(n2), topDestYear = topDestYear)

@app.route('/Airline-Staff-View-Flight-Rating', methods = ['GET', 'POST'])
def view_specific_flight_rating(): 
	flight_number = request.form['flight-number']
	dept_date = request.form['dept-date']
	dept_time = request.form['dept-time']
	cursor = conn.cursor()
	getFlightRatingComments = 'SELECT Rate, CustomerComment FROM suggested WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
	cursor.execute(getFlightRatingComments, (flight_number, dept_date, dept_time))
	data = cursor.fetchall()
	print("Fetched Data")
	if(data): 
		print("ifdata")
		print(data)
		return render_template('Airline-Staff-View-Flight-Rating.html', flights = data, flight = flight_number, date = dept_date, time = dept_time)
	else: 
		print("nodata")
		data = ""
		error = "Flight does not exist, or has no ratings"
		return render_template('Airline-Staff-View-Flight-Rating.html', flights = data, error = error, flight= flight_number, date = dept_date, time = dept_time)

@app.route('/Airline-Staff-Compare-Revenue')
def airlineStaffRevenue(): 
	cursor = conn.cursor()
	#returns indirect, direct
	getRevenueMonth = 'SELECT SUM(SoldPrice) as sale FROM ticket WHERE AgentID <> %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH UNION SELECT SUM(SoldPrice) as sale FROM ticket WHERE AgentID = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH'
	null = 'NULL'
	cursor.execute(getRevenueMonth, (null, null))
	monthSales = cursor.fetchall()
	print("sales:",monthSales)
	set = []

	monthIndirectSales = monthSales[0]['sale']
	monthDirectSales = monthSales[1]['sale']

	data1 = ['indirect sale', monthIndirectSales, 'green']
	data2 = ['direct sale', monthDirectSales, 'blue']
	set.append(data1)
	set.append(data2)
	#print(set)

	getRevenueYear = 'SELECT SUM(SoldPrice) as sale FROM ticket WHERE AgentID <> %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR UNION SELECT SUM(SoldPrice) as sale FROM ticket WHERE AgentID = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR'
	yearSet = []
	cursor.execute(getRevenueYear, (null, null))
	yearSales = cursor.fetchall()
	yearIndirectSales = yearSales[0]['sale']
	yearDirectSales = yearSales[1]['sale']

	year1 = ['indirect sale', yearIndirectSales, 'green']
	year2 = ['direct sale', yearDirectSales, 'blue']
	yearSet.append(year1)
	yearSet.append(year2)

	return render_template('Airline-Staff-Compare-Revenue.html', set = set, max = 100, yearSet = yearSet)

@app.route('/Airline-Staff-View-Reports')
def airlineViewReport(): 
	cursor = conn.cursor()
	getAmountTicketLastMonth = 'SELECT COUNT(TicketID) AS tickets, MONTHNAME(PurchaseDate) AS month FROM ticket WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH GROUP BY month'
	cursor.execute(getAmountTicketLastMonth)
	lastMonth = cursor.fetchone()
	labels, values = [lastMonth['month']], [lastMonth['tickets']]
	getAmountTicketLastYear = 'SELECT COUNT(TicketID) AS tickets, MONTHNAME(PurchaseDate) AS month FROM ticket WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR GROUP BY month'
	cursor.execute(getAmountTicketLastYear)
	ticketLastYear = cursor.fetchall()
	months = {1:'January', 2: 'February', 3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
	from datetime import date
	currMonth = date.today().month
	earliest = currMonth-12 #for graphing years
	labels1 = []
	for i in range(earliest,currMonth): 
		if i>0 and i<13: 
			labels1.append(months[i])
		elif i < 1: 
			i += 12
			labels1.append(months[i])
	values1 = []
	for elem in labels1:
		added = False
		for i in range (len(ticketLastYear)): 
			if ticketLastYear[i]['month'] == elem: 
				values1.append(ticketLastYear[i]['tickets'])
				added = True
				break
		if added == False: 
			values1.append(0)
	maximumValue = max(values1) + 1

	return render_template('Airline-Staff-View-Reports.html', labels = labels, values = values, labels1 = labels1, values1 = values1, max = 10, max1 = maximumValue)

@app.route('/Airline-Staff-View-Report-Custom', methods = ['GET', 'POST'])
def airlineStaffViewReportCustom(): 
	print(request.form)
	start_date = request.form['start-date']
	end_date = request.form['end-date']
	cursor = conn.cursor()
	getTicketAmount = 'SELECT COUNT(TicketID) AS tickets, MONTHNAME(PurchaseDate) AS month, YEAR(PurchaseDate) AS year FROM ticket WHERE PurchaseDate >= %s AND PurchaseDate <= %s GROUP BY month, year'
	cursor.execute(getTicketAmount, (start_date, end_date))
	data = cursor.fetchall()
	labels = []
	values = []
	for elem in data: 
		date = str(elem['month']) + " " + str(elem['year'])
		labels.append(date)
		values.append(elem['tickets'])
		
	maximumValue = max(values) + 1
	return render_template('Airline-Staff-View-Reports-Custom.html', labels = labels, values = values, max = maximumValue)

'''
@app.route('/Airline-Staff-View-Agents-Customers')
def airline_staff_view_people():
	return render_template('Airline-Staff-View-Agents-Customers.html')

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO user VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

'''
	
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
