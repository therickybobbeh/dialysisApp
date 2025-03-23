import { Geist, Geist_Mono } from "next/font/google";
import Navbar from "../components/Navbar";
import "../globals.css"; //  Corrected path

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <Navbar /> {/* Ensure navigation is visible */}
        {children}
      </body>
    </html>
  );
}
