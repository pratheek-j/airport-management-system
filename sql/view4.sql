use AirportWebsite;
create view agent_view as
select E.FName, F.*
from Employee E, FlightLeg F, Crew C
where C.FL_ID = F.FL_ID
and E.EID = C.EID
and E.JobType = 'Pilot';