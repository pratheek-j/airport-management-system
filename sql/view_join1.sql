use AirportWebsite;
CREATE VIEW flights AS
    SELECT 
        F_leg.*, 
		(72 - COUNT(R_Seats.Seat)) AS seats_left
    FROM 
        FlightLeg F_leg 
    LEFT JOIN 
        R_Seats
    ON 
        F_leg.FL_ID = R_Seats.FL_ID
    GROUP BY 
        F_leg.FL_ID,
        F_leg.AircraftID;