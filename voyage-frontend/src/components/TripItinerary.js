import React, {useEffect } from "react";
import { useLocation } from "react-router-dom";
import "./TripItineraryStyles.css"

function TripItinerary() {

  
  const location = useLocation();

  // Extract tripItinerary data from location state
  const tripItinerary = location.state && location.state.tripItinerary;

  if (!tripItinerary || tripItinerary.length === 0) {
    return <div>No trip itinerary available</div>;
  }



  return (
    <div className="trip-container">
      {tripItinerary.map((day, index) => (
        <div key={index} className="day-container">
          <h2>Day {day.day}</h2>
          <div className="activity-container">
            <div className="morning">
              <h3>Morning Activity</h3>
              {day.morning_activity.map((activity, idx) => (
                <div key={idx} className="activity">
                  <h4>{activity.content_name}</h4>
                  <p>{activity.content_description}</p>
                </div>
              ))}
            </div>
            <div className="afternoon">
              <h3>Afternoon Activity</h3>
              {day.afternoon_activity.map((activity, idx) => (
                <div key={idx} className="activity">
                  <h4>{activity.content_name}</h4>
                  <p>{activity.content_description}</p>
                </div>
              ))}
            </div>
            <div className="evening">
              <h3>Evening Activity</h3>
              {day.evening_activity.map((activity, idx) => (
                <div key={idx} className="activity">
                  <h4>{activity.content_name}</h4>
                  <p>{activity.content_description}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="recommendations">
            <h3>Restaurants Recommendations</h3>
            <ul>
              {day.restaurants_recommendations.map((restaurant, idx) => (
                <li key={idx}>{restaurant.restaurant_name} ({restaurant.restaurant_type})</li>
              ))}
            </ul>
            <h3>Accommodation Recommendations</h3>
            <ul>
              {day.accommodation_recommendations.map((accommodation, idx) => (
                <li key={idx}>{accommodation.accommodation_name} ({accommodation.accommodation_type})</li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}

export default TripItinerary;
