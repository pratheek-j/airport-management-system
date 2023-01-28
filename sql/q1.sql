select F.*, B.*, T.*
from FlightLeg F, books B, Ticket T
where F.FL_ID = B.FL_ID
and T.BookingID = B.BookingID
and B.BookingID = 278922;