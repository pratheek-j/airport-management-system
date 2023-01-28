use AirportWebsite;
CREATE TRIGGER generate_TId
before insert on Ticket
for each row
	SET NEW.TicketID = (select ceiling(RAND()*102360)) ;
    
create trigger generate_bag_id
before insert on Ticket
for each row
	set NEW.BaggageID = (select ceiling(RAND()*102360)); 
