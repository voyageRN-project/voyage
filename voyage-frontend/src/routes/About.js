import Hero from "../components/Hero";
import NavBar from "../components/NavBar"
import AboutImg from "../photos/desert1.jpg"
import Footer from "../components/Footer";
import AboutUs from "../components/AboutUs";

function About() {
    return(
        <>
         <NavBar/>
        <Hero
        cName="hero-Small"
        heroImg={AboutImg}
        textstyle = "hero-mid-text"
        title = "ABOUT"
        btnClass="hide"
        />
        <AboutUs/>
        <Footer/>
      
        </>
    )
}

export default About;