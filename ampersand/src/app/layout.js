import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { cookies } from "next/headers"
import { getCookie, hasCookie } from "cookies-next/server";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Ampersand",
  description: "Track front history, leave notes for eachother, and ask for a prediction of who you are.",
};
export const instant = false;

export default async function RootLayout({ children }) {
  let store = await cookies()
  const storeBought = store.get("username")?.value
  console.log("layout storeBought ", storeBought)
  
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-[20%] flex flex-col max-h-[100%] h-[97%]">
        <header className="py-5 items-center">
          <div className="container mx-auto  items-center">
            <h1 className="text-5xl text-center">Ampersand</h1>
            {/* <nav className="flex items-center justify-between text-center max-w-7/10 mx-[25%]"> */}
            <nav className="">
              {
                storeBought && 
                <div className="flex items-center justify-between text-center max-w-7/10 ml-[85%]">
                  <a href="/profile">profile</a>
                  <a href="/notes">notes</a>
                  <a href="/fronthistory">front history</a>
                  <a href="/logout">logout</a>
                </div>
              }
              {
                !storeBought && 
                <div className="flex items-center justify-between text-center max-w-7/10 ml-[85%]">
                  <a href="/login">login</a>
                  <a href="/signup">signup</a>
                </div>
              }
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
