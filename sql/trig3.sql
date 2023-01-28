use AirportWebsite;

delimiter //
CREATE PROCEDURE update_flight_status()
BEGIN
    DECLARE cur_date TIMESTAMP;
    DECLARE done INT DEFAULT FALSE;
    DECLARE flight_id INT;
    DECLARE departure_time TIMESTAMP;
    DECLARE arrival_time TIMESTAMP;
    DECLARE int_departure_time TIMESTAMP;
    DECLARE int_arrival_time TIMESTAMP;
    DECLARE status VARCHAR(255);
    DECLARE cur CURSOR FOR SELECT FL_ID, DEP_DT, ARR_DT, INT_ARR_DT, INT_DEP_DT FROM FlightLeg;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SET cur_date = NOW();
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO flight_id, departure_time, arrival_time, int_arrival_time, int_departure_time;
        IF done THEN
            LEAVE read_loop;
        END IF;
        IF cur_date < departure_time THEN
            SET status = 'Scheduled';
        ELSEIF cur_date BETWEEN departure_time AND arrival_time THEN
            SET status = 'In-flight';
		ELSEIF cur_date BETWEEN int_arrival_time AND int_departure_time THEN
			SET status = 'Transit';
        ELSE
            SET status = 'Completed';
        END IF;
        UPDATE FlightLeg SET Status = status WHERE FL_ID = flight_id;
    END LOOP;
    CLOSE cur;
END //

delimiter ;