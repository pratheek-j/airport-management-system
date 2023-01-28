use AirportWebsite;
CREATE TRIGGER update_flight_duration
BEFORE INSERT ON FlightLeg
FOR EACH ROW
    SET NEW.Duration = TIMESTAMPDIFF(MINUTE, NEW.DEP_DT, NEW.ARR_DT);