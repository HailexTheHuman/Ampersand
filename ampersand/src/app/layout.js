import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

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

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <header className="py-5 items-center">
          <div className="container mx-auto  items-center">
            <h1 className="text-xl text-center">Ampersand</h1>
            <nav className="flex items-center justify-between text-center max-w-7/10 mx-[25%]">
              <a href="/signup">signup</a>
              <a href="/login">login</a>
              <a href="/logout">logout</a>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
