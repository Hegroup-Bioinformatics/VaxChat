import Chats from "./components/Chats";
import Footer from "./components/Footer";
import Header from "./components/Header";

function App() {

  return (
    <div className="flex flex-col min-h-screen overflow-hidden h-full">
      <Header />
      <main className="flex-grow bg-slate-800 flex justify-center h-[90%] overflow-hidden">
        <Chats />
      </main>
      <Footer />
    </div>
  )
}

export default App
