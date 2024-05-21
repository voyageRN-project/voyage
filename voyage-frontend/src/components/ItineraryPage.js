import React from 'react';

const ItineraryPage = ({ tripData }) => {
  return (
    <div className="itinerary-container">
      {tripData.map((day, index) => (
        <div key={index} className="day-container">
          <h2>Day {day.day}</h2>
          {day.morning_activity && day.morning_activity.length > 0 && (
            <div>
              <h3>Morning Activity</h3>
              <ul>
                {day.morning_activity.map((activity, idx) => (
                  <li key={idx}>
                    <strong>{activity.content_name}</strong> - {activity.content_description}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {day.afternoon_activity && day.afternoon_activity.length > 0 && (
            <div>
              <h3>Afternoon Activity</h3>
              <ul>
                {day.afternoon_activity.map((activity, idx) => (
                  <li key={idx}>
                    <strong>{activity.content_name}</strong> - {activity.content_description}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {day.evening_activity && day.evening_activity.length > 0 && (
            <div>
              <h3>Evening Activity</h3>
              <ul>
                {day.evening_activity.map((activity, idx) => (
                  <li key={idx}>
                    <strong>{activity.content_name}</strong> - {activity.content_description}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {day.restaurant_recommendations && day.restaurant_recommendations.length > 0 && (
            <div>
              <h3>Restaurant Recommendations</h3>
              <ul>
                {day.restaurant_recommendations.map((restaurant, idx) => (
                  <li key={idx}>
                    <strong>{restaurant.restaurant_name}</strong> - {restaurant.restaurant_type}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {day.accommodation_recommendations && day.accommodation_recommendations.length > 0 && (
            <div>
              <h3>Accommodation Recommendations</h3>
              <ul>
                {day.accommodation_recommendations.map((accommodation, idx) => (
                  <li key={idx}>
                    <strong>{accommodation.accommodation_name}</strong> - {accommodation.accommodation_type}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ItineraryPage;
