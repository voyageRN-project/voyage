import "./BusinesFormStyle.css";
import select from "react-dropdown-select";
import React, { useEffect, useState } from "react";
import Select from "react-select";
import axios from "axios";


let HOST_NAME = "http://localhost:8080";

function BusinesForm(){
    const [countryOptions, setCountryOptions] = useState([]);
    const [formData, setFormData] = useState({
      businessName: "",
      businessNumber: "",
      businessType: "",
      businessDescription: "",
      country: "",
      email: "",
      contactPersonName: "",
      contactPersonNumber: "",
      voyageCredit: "",
      latitude: "", // Add latitude field
      longitude: "", // Add longitude field
    });

    useEffect(() => {
        const fetchCountries = async () => {
          try {
            const response = await axios.get("https://countriesnow.space/api/v0.1/countries");
            console.log("Response data:", response.data); // Log the response data
            const countries = response.data.data.map(country => ({
                value: country.country,
                label: country.country
            }));
            console.log("Countries:", countries); // Log the countries
            setCountryOptions(countries);
          } catch (error) {
            console.error("Error fetching countries:", error);
          }
        };
      
        fetchCountries();
      }, []);


      const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({
          ...formData,
          [name]: value,
        });
      };
    
      const handleSelectChange = (selectedOption) => {
        setFormData({
          ...formData,
          country: selectedOption.value,
        });
      };
    
    

      const handleSubmit = async (e) => {
        e.preventDefault();
        try {
          const formDataToSend = new FormData();
          formDataToSend.append('business_name', formData.businessName);
          formDataToSend.append('business_type', formData.businessType);
          formDataToSend.append('business_phone', formData.businessNumber);
          formDataToSend.append('business_email', formData.email);
          formDataToSend.append('business_country', formData.country);
          formDataToSend.append('business_contact_person', formData.contactPersonName);
          formDataToSend.append('business_contact_person_phone', formData.contactPersonNumber);
          formDataToSend.append('credits_bought', formData.voyageCredit); 
          formDataToSend.append('business_match_interest_points', formData.interestPoint); 
          formDataToSend.append('business_description', formData.businessDescription);
        
          // Optionally, add latitude and longitude fields if needed
          formDataToSend.append('business_latitude', formData.latitude);
          formDataToSend.append('business_longitude', formData.longitude);
        
          // Send POST request with formDataToSend
          const response = await axios.post(HOST_NAME + "/api/v1/business_app/add_business", formDataToSend, {
            headers: {
              "Content-Type": "multipart/form-data" // Set Content-Type to multipart/form-data
            }
          });
        
          console.log("Response from backend:", response.data);
          // Optionally, you can reset the form fields after successful submission
          // Reset formData here if needed
        
        } catch (error) {
          console.error("Error submitting form data:", error);
          // Handle error condition
        }
      };

    return(
        <div className="from-container">
            <h1>YOUR BUSINESS | THEIR VOYAGE</h1>
            <p>LET'S START</p>
            <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="businessName"
          placeholder="Business Name"
          value={formData.businessName}
          onChange={handleInputChange}
        />
        <input
          type="text"
          name="businessNumber"
          placeholder="Business Number"
          value={formData.businessNumber}
          onChange={handleInputChange}
        />
                <select
                    className="Business Category"
                    name="interestPoint"
                    value={formData.interestPoint}
                    onChange={handleInputChange}
                >
                    <option value="">Business Category</option>
                    <option value="Art venues">Art venues</option>
                    <option value="Festivals">Festivals</option>
                    <option value="Hiking trails">Hiking trails</option>
                    <option value="Places to stay">Places to stay</option>
                    <option value="Winery">Winery</option>
                    <option value="Nature">Nature</option>
                    <option value="Culinary">Culinary</option>
                </select>
                <select
                    className="Type"
                    name="businessType"
          value={formData.businessType}
          onChange={handleInputChange}
        >
          <option value="">Type</option>
          <option value="Winery">Winery</option>
          <option value="Restaurant">Restaurant</option>
          <option value="Cocktail bar">Cocktail bar</option>
          <option value="Food truck">Food truck</option>
          <option value="Festival">Festival</option>
          <option value="Concert">Concert</option>
          <option value="Gallery">Gallery</option>
          <option value="Museum">Museum</option>
          <option value="Hotel">Hotel</option>
          <option value="Hostel">Hostel</option>
          <option value="Campsite">Campsite</option>
          <option value="farm house">Farm house</option>
        </select>
        <textarea
          name="businessDescription"
          placeholder="Business Description"
          rows="4"
          value={formData.businessDescription}
          onChange={handleInputChange}
        ></textarea>
        <Select
          className="country"
          options={countryOptions}
          placeholder="Country"
          onChange={handleSelectChange}
        />
        <br/>
        <input
          type="text"
          name="latitude"
          placeholder="Latitude"
          value={formData.latitude}
          onChange={handleInputChange}
        />
        <input
          type="text"
          name="longitude"
          placeholder="Longitude"
          value={formData.longitude}
          onChange={handleInputChange}
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleInputChange}
        />
        <input
          type="text"
          name="contactPersonName"
          placeholder="Contact Person Name"
          value={formData.contactPersonName}
          onChange={handleInputChange}
        />
        <input
          type="text"
          name="contactPersonNumber"
          placeholder="Contact Person Number"
          value={formData.contactPersonNumber}
          onChange={handleInputChange}
        />
     
        <input
          type="text"
          name="voyageCredit"
          placeholder="Voyage Credit"
          value={formData.voyageCredit}
          onChange={handleInputChange}
        />
        <br />
        <button type="submit">SEND</button>
      </form>
    </div>
  );
}

export default BusinesForm;