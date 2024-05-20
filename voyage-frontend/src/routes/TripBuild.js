import Hero from "../components/Hero";
import NavBar from "../components/NavBar"
import Footer from "../components/Footer";
import Preferences from "../components/Preferences";

function TripBuild() {
    return(
        <>
        <NavBar/>
        <Hero
        cName="hero-Small"
        heroImg="https://i0.wp.com/visitkohtao.org/wp-content/uploads/2021/09/D8255DB0-E910-42E9-AF9F-48A4E6B6DEEE.png?fit=800%2C416&ssl=1"
        textstyle = "hero-Small-text"
        title = "CHOOSE YOUR PREFERENCES "
        text = "BUILD YOUR PERFECT VOYAGE"
        btnClass="hide"
        />
        <Preferences/>
        <Footer/>
        </>
    )
}

export default TripBuild;

