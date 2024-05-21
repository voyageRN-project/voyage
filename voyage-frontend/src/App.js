import "./styles.css";

import { Route, Routes } from "react-router-dom";
import Home from "./routes/Home";
import About from "./routes/About";
import Business from "./routes/Business";
import Contact from "./routes/Contact";
import SignIn from "./routes/SignIn";
import TripBuild from "./routes/TripBuild";
import UserVoyage from "./routes/UserVoyage";


export default function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element = {<Home/>}/>
        <Route path="/about" element = {<About/>}/>
        <Route path="/businesses" element = {<Business/>}/>
        <Route path="/contact" element = {<Contact/>}/>
        <Route path="/signin" element = {<SignIn/>}/>
        <Route path="/tripBuild" element = {<TripBuild/>}/>
        <Route path="/yourVoyage" element = {<UserVoyage/>}/>
      </Routes>
   
   
  
    </div>
  );
}
