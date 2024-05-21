import Hero from "../components/Hero";
import NavBar from "../components/NavBar"
import AboutImg from "../photos/newyork.jpg"
import Footer from "../components/Footer";

function SignIn() {
    return(
        <>
        <NavBar/>
        <Hero
        cName="hero-mid"
        heroImg={AboutImg}
        textstyle = "hero-mid-text"
        title = "SIGN IN"
        btnClass="hide"
        />
        <Footer/>
        </>
    )
}

export default SignIn;