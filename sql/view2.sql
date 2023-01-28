use AirportWebsite;
create view R_Seats_view as
select F.AL_Code as AL_Code, R.*
from FlightLeg F, R_Seats R
where F.FL_ID = R.FL_ID; 