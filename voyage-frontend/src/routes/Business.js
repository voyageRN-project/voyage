import Hero from "../components/Hero";
import NavBar from "../components/NavBar"
import AboutImg from "../photos/winery.jpg"
import Footer from "../components/Footer";
import BusinesForm from "../components/BusinesForm";


function Business() {
    return(
        <>
        <NavBar/>
        <Hero
        cName="hero-mid"
        heroImg={AboutImg}
        textstyle = "hero-mid-text"
        title = "BUSINESSES"
        btnClass="hide"
        />
        <BusinesForm/>
        <Footer/>
        
        </>
    )
}

export default Business;