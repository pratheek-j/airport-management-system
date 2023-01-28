use AirportWebsite;
create view Ticket_view as
select F.AL_Code as AL_Code, T.*
from R_Seats_view F, Ticket T
where F.TicketID = T.TicketID;