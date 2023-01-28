create view emp as
select E.*, C.FL_ID
from Employee E, Crew C
where E.EID = C.EID;