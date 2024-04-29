import React, { useEffect, useState } from "react"
import {
    FiChevronDown,
    FiChevronUp,
  } from "react-icons/fi"

import Claims from "./Claims"


export default function Home() {
    const [activePage, setActivePage] = useState(0)

    const displayActivePage = () => {
        return AVAILABLE_PAGES[activePage]
    }

    useEffect(() => {
        const handleScroll = (e: WheelEvent) => {
            e.preventDefault()

            const delta = Math.sign(e.deltaY)
            if (delta > 0) {
                // Scrolling down
                if (AVAILABLE_PAGES.length > activePage + 1) {
                    setActivePage((prevActivePage) => prevActivePage + 1);
                }
            } else if (delta < 0) {
                // Scrolling up
                if (activePage > 0) {
                    setActivePage((prevActivePage) => prevActivePage - 1);
                }
            }
        };

        window.addEventListener("wheel", handleScroll);

        return () => {
            window.removeEventListener("wheel", handleScroll);
        };
    }, [activePage]);

    return (
        <div
            style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                width: '100%',
                height: '100%',
                overflow: 'hidden',
            }}
        >
            {displayActivePage()}
            
        </div>
    )
}

const AVAILABLE_PAGES: React.ReactNode[] = [
    <Claims/>
]