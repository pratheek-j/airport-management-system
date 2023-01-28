use AirportWebsite;

CREATE TRIGGER generate_id
before INSERT ON Aircraft
FOR EACH ROW
SET NEW.ID = (select ceiling(RAND()*1000)); 