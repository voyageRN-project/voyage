import Footer from "../components/Footer";
import Hero from "../components/Hero";
import NavBar from "../components/NavBar"

function Home() {
    return(
        <>
        <NavBar/>
        <Hero
        cName="hero"
        heroImg="https://q-xx.bstatic.com/xdata/images/hotel/max1024x768/312330905.jpg?k=e2689772180e71ecd07a3f7401dfdd661871154c7bee5ab03fedc552244895c1&o="
        textstyle = "hero-text"
        title = "YOUR PERFECT TRIP"
        text = "CHOOSE YOUR PREFERENCES"
        buttonText ="LETS START"
        url="/tripBuild"
        btnClass="show"
        />
        <Footer/>
        </>
    )
}

export default Home;