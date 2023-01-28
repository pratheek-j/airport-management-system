use AirportWebsite;
create view Flight_List as
select F.*, AP.Name
from FlightLeg F JOIN Airport AP 
on F.ARR_AP = AP.Unique_code;

create view ConFlight_List as
select F.*, AP.Name, AP.Name as INT_Name
from FlightLeg F JOIN Airport AP 
on F.ARR_AP = AP.Unique_code
and F.INT_AP = AP.Unique_code;