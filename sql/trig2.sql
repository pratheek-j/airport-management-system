use AirportWebsite;
CREATE TRIGGER update_age
BEFORE INSERT ON Employee
FOR EACH ROW
    SET NEW.age = YEAR(CURDATE()) - YEAR(NEW.DOB);
