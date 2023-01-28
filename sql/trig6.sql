use AirportWebsite;
CREATE TRIGGER generate_Eid
before INSERT ON Employee
FOR EACH ROW
SET NEW.EID = (select ceiling(RAND()*100000)); 