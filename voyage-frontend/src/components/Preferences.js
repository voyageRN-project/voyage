import "./PreferencesStyle.css"
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Select from "react-select";
import { useNavigate } from "react-router-dom";

let HOST_NAME = "http://localhost:8080";

function Preferences() {
  const [countryOptions, setCountryOptions] = useState([]);
  const [preferences, setPreferences] = useState({
        budget: "",
        season: "",
        participants: "",
        duration: "",
        country: "",
        accommodation:"",
        interests: "",
      });
  const [loading, setLoading] = useState(false);  
      const handleInputChange = (event) => {
        const { name, value } = event.target;
        setPreferences({
          ...preferences,
          [name]: value
        });
      };
    
      const handleCheckboxChange = (event) => {
        const { name, checked, value } = event.target;
        if (checked) {
          setPreferences({
            ...preferences,
            interests: [...preferences.interests, value]
          });
        } else {
          setPreferences({
            ...preferences,
            interests: preferences.interests.filter(interest => interest !== value)
          });
        }
      };
    
      const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        try {
          const interestsString = preferences.interests.join(",");
          
          // Create FormData object and append data
          const formData = new FormData();
          formData.append("budget", preferences.budget);
          formData.append("season", preferences.season);
          formData.append("participants", preferences.participants);
          formData.append("duration", `${preferences.duration} days`);
          formData.append("country-code", preferences.country);
          formData.append("interest-points", interestsString);
          formData.append("accommodation_type", preferences.accommodation);
      
          // Construct URL
          const url = HOST_NAME + "/api/v1/users_app/build_trip";
      
          // Create request options
          const requestOptions = {
            method: "POST",
            body: formData
          };
      
          // Send GET request
          const response = await fetch(url, requestOptions);
      
          // Check response status
          if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
          }

          
          const data = await response.json();
          setLoading(false);
          // Navigate to the next page with the response data
          navigate('/yourVoyage', { state: { tripItinerary: data.trip_itinerary } });
          console.log('Response from backend:', data);

        } catch (error) {
          console.error('Error submitting preferences:', error);
          // Handle error condition
        }
      };
      

      useEffect(() => {
          const fetchCountries = async () => {
            try {
              const response = await axios.get("https://countriesnow.space/api/v0.1/countries");
              console.log("Response data:", response.data); // Log the response data
              const countries = response.data.data.map(country => ({
                  value: country.country,
                  label: country.country,
                  code: country.iso2
              }));
              console.log("Countries:", countries); // Log the countries
              setCountryOptions(countries);
            } catch (error) {
              console.error("Error fetching countries:", error);
            }
          };
        
          fetchCountries();
        }, []);

        const navigate = useNavigate();


    return(
        <div className="pv">
           {loading ? ( // Conditional rendering based on loading state
           <div className="loading">
           <div className="loading-text">In a few seconds your perfect journey will be displayed...</div>
         </div>
      ) : (
        <form onSubmit={handleSubmit}>
      <label>Budget:</label>

      <select
          className="budget catgory"
          name="budget"
          value={preferences.budget}
          onChange={handleInputChange}
        >
          <option value="">Select a budget</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      <br />

      <label>Season:
        <select name="season" value={preferences.season} onChange={handleInputChange}>
          <option value="">Select a season</option>
          <option value="summer">Summer</option>
          <option value="winter">Winter</option>
          <option value="autumn">Autumn</option>
          <option value="spring">Spring</option>
        </select>
      </label>
      <br />

      <label>Participants:
        <select name="participants" value={preferences.participants} onChange={handleInputChange}>
          <option value="">Select participants</option>
          <option value="family">Family</option>
          <option value="couple">Couple</option>
          <option value="individual">Individual</option>
        </select>
      </label>
      <br />
      <label>Choose your destination:
      <Select classNames="country"
                 options={countryOptions}
                 className="country"
                 onChange={(selectedOption) => setPreferences({ ...preferences, country: selectedOption.code })}
                 placeholder="Country"
                />
                </label>
                <br />
                
      <label>Duration of the trip (days):
        <input
          type="number"
          name="duration"
          value={preferences.duration}
          onChange={handleInputChange}
        />
      </label>
      <br />
      <label>Choose accommodation type:</label>
      <select
          className="accommodation catgory"
          name="accommodation"
          value={preferences.accommodation}
          onChange={handleInputChange}
        >
          <option value="">Select type</option>
          <option value="Hotel">Hotel</option>
          <option value="Hostel">Hostel</option>
          <option value="Campsite">Campsite</option>
          <option value="Farm House">Farm house</option>
        </select>

      <fieldset>
        <legend>Choose your points of interest:</legend>
        <label>
          <input
            type="checkbox"
            name="interests"
            value="Art venues"
            checked={preferences.interests.includes('Art venues')}
            onChange={handleCheckboxChange}
          /> Art venues
        </label>
        <label>
          <input
            type="checkbox"
            name="interests"
            value="Festivals"
            checked={preferences.interests.includes('Festivals')}
            onChange={handleCheckboxChange}
          /> Festivals
        </label>
        <label>
          <input
            type="checkbox"
            name="interests"
            value="Hiking trails"
            checked={preferences.interests.includes('Hiking trails')}
            onChange={handleCheckboxChange}
          /> Hiking trails
        </label>
        <label>
          <input
            type="checkbox"
            name="interests"
            value="Places to stay"
            checked={preferences.interests.includes('Places to stay')}
            onChange={handleCheckboxChange}
          /> Places to stay
        </label>
        <label>
          <input
            type="checkbox"
            name="interests"
            value="Culinary"
            checked={preferences.interests.includes('Culinary')}
            onChange={handleCheckboxChange}
          /> Culinary
        </label>
      </fieldset>
      <br />
      <button type="submit">Submit Preferences</button>
    
    </form>
    )}
    </div>
    );
}

export default Preferences;



 
  