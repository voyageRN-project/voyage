import Hero from "../components/Hero";
import NavBar from "../components/NavBar"
import AboutImg from "../photos/boat.jpg"
import Footer from "../components/Footer";

function Contact() {
    return(
        <>
             <NavBar/>
        <Hero
        cName="hero-mid"
        heroImg={AboutImg}
        textstyle = "hero-mid-text"
        title = "CONTACT"
        btnClass="hide"
        />
        <Footer/>
        </>
    )
}

export default Contact;
