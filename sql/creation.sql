use AirportWebsite;

create table Airport ( 
 Unique_code	char(3)		primary key, 
 Name		varchar(1000), 
 Country 	varchar(100), 
 State 		varchar(100), 
 City 		varchar(100) 
);

create table Airline (
 AL_Code 	varchar(3) 	primary key,
 AL_Name 	varchar(100)
);

create table Aircraft ( 
 ID 		smallint 	primary key  	DEFAULT 0, 
 AL_Code 	varchar(3), 
 FOREIGN KEY (AL_Code) REFERENCES Airline(AL_Code) 
);

create table Employee ( 
 EID 		int 		primary key	 DEFAULT 0, 
 FName 		varchar(100), 
 LName 		varchar(100), 
 Address 	varchar(100), 
 Gender 	char(1), 
 Salary 	int, 
 Phone 		bigint, 
 Age 		smallint default 0,
 DOB 		date, 
 AL_Code 	varchar(3), 
 JobType 	varchar(20),
 FOREIGN KEY (AL_Code) REFERENCES Airline(AL_Code) 
);

create table FlightLeg (
 FL_ID 		smallint 	primary key	 DEFAULT 0, 
 Status 	varchar(20) default '', 	
 Fare 		int, 
 DEP_DT  	timestamp,  
 ARR_DT 	timestamp, 
 INT_ARR_DT timestamp NULL,
 INT_DEP_DT timestamp NULL,
 Duration 	smallint default 0, 
 Gate 		varchar(5), 
 Layover 	int default 0, 
 AL_Code 	varchar(3), 
 FL_TYPE	varchar(200),
 ARR_AP 	char(3),
 INT_AP 	char(3), 
 AircraftID 	smallint,
 INTAircraftID 	smallint NULL,
 FOREIGN KEY (ARR_AP) REFERENCES Airport(Unique_code), 
 FOREIGN KEY (INT_AP) REFERENCES Airport(Unique_code), 
 FOREIGN KEY (AircraftID) REFERENCES Aircraft(ID), 
 FOREIGN KEY (INTAircraftID) REFERENCES Aircraft(ID) 
);

create table Crew ( 
 EID 	int,
 FL_ID 	smallint, 
 FOREIGN KEY (EID) REFERENCES Employee(EID) ON DELETE CASCADE, 
 FOREIGN KEY (FL_ID) REFERENCES FlightLeg(FL_ID) ON DELETE CASCADE 
);

create table Passenger (
 PassportID 	varchar(10) 	primary key, 
 DOB 		date, 
 Fname 		varchar(50),
 Lname 		varchar(50),
 Phone 		bigint,
 Gender 	char(1),
 BookingID 	int
);

create table books (
 BookingID 	int 		primary key	 DEFAULT 0,
 FL_ID 		smallint,
 Date 		date,
 STATUS 	varchar(30) default '', 
 FOREIGN KEY (FL_ID) REFERENCES FlightLeg(FL_ID) ON DELETE CASCADE
);

create table Ticket ( 
 TicketID 	int 		primary key	 DEFAULT 0, 
 BaggageID 	int,
 PassengerID 	varchar(10), 
 Price 		int, 
 BookingID 	int, 
 Seat	 	varchar(5),
 FOREIGN KEY (BookingID) REFERENCES books(BookingID) ON DELETE CASCADE,  
 FOREIGN KEY (PassengerID) REFERENCES Passenger(PassportID) 
);

create table R_Seats (
 FL_ID 		smallint,
 Seat	 	varchar(5),
 TicketID 	int,
 FOREIGN KEY (TicketID) REFERENCES Ticket(TicketID) ON DELETE CASCADE,
 FOREIGN KEY (FL_ID) REFERENCES FlightLeg(FL_ID) ON DELETE CASCADE,
 PRIMARY KEY (Seat, TicketID, FL_ID)
);