use AirportWebsite;
CREATE TRIGGER generate_FLid
before INSERT ON FlightLeg
FOR EACH ROW
SET NEW.FL_ID = (select ceiling(RAND()*10000)); 