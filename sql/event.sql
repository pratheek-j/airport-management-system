CREATE EVENT minutely_event
ON SCHEDULE
  EVERY 10 MINUTE
  DO
  CALL update_flight_status();