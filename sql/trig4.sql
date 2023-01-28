use AirportWebsite;
delimiter //

CREATE FUNCTION calculate_layover_time(departure_time TIMESTAMP, arrival_time TIMESTAMP)
RETURNS INT
BEGIN
    DECLARE layover_time INT;
    SET layover_time = TIMESTAMPDIFF(MINUTE, arrival_time, departure_time);
    RETURN layover_time;
END //

CREATE TRIGGER calculate_layover_time_before_insert
BEFORE INSERT ON FlightLeg
FOR EACH ROW
BEGIN
    SET NEW.Layover = calculate_layover_time(NEW.INT_DEP_DT, NEW.INT_ARR_DT);
END //

CREATE TRIGGER calculate_layover_time_after_update
BEFORE UPDATE ON FlightLeg
FOR EACH ROW
BEGIN
    SET NEW.Layover = calculate_layover_time(NEW.INT_DEP_DT, NEW.INT_ARR_DT);
END //
