import Hero from "../components/Hero";
import NavBar from "../components/NavBar"
import Footer from "../components/Footer";
import TripItinerary from "../components/TripItinerary"

function UserVoyage() {
    return(
        <>
        <NavBar/>
        <Hero
        cName="hero-Small"
        heroImg="https://i0.wp.com/visitkohtao.org/wp-content/uploads/2021/09/D8255DB0-E910-42E9-AF9F-48A4E6B6DEEE.png?fit=800%2C416&ssl=1"
        textstyle = "hero-yourV-text"
        title = "YOUR VOYAGE "
        text = "this is your perfect trip... Discover and order"
        url = "/yourVoyage"
        btnClass="hide"
        />
       <TripItinerary/>
        <Footer/>
        </>
    )
}

export default UserVoyage;

