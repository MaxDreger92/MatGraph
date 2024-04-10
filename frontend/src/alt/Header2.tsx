import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { IconLogout, IconSettings, IconChevronDown, IconUser } from "@tabler/icons-react";
import logo_sm from "../img/logo_nodes.png";
import { userContext } from "../common/userContext";
import { useLocation } from "react-router-dom";
import React from "react";
import { Planet } from "react-planet";

interface HeaderProps {
  handleHeaderLinkClick: (key: string) => void
  handleLogout: () => void
  activeTab: string | null
  setActiveTab: React.Dispatch<React.SetStateAction<string | null>>
  pathname: string
}

export default function Header(props: HeaderProps) {
  const {
    handleHeaderLinkClick,
    handleLogout,
    activeTab,
    setActiveTab,
    pathname
  } = props;
  const [userMenuOpened, setUserMenuOpened] = useState(false);
  const user = useContext(userContext);

  return (
    <div className={"header-wrap"}
      style={{
        position:"absolute",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: 80,
        width: "100%",
        // backgroundColor: pathname === "/" ? "#1a1b1e" : "#25262b",
        // backgroundColor: "#1a1b1e"
      }}
    >
      {/* Logo (left corner) */}
      <div
        style={{
          position: "absolute",
          left: 17,
        }}
      >
        <Link to="/" onClick={() => setActiveTab("")}>
          <img
            src={logo_sm}
            alt="matGraphAI"
            className="logo-sm"
          />
        </Link>
      </div>

      {/* Tabs (middle) */}
      <HeaderTabs handleHeaderLinkClick={handleHeaderLinkClick}/>

      {/* Menu (right corner) */}
      <HeaderMenu handleHeaderLinkClick={handleHeaderLinkClick} handleLogout={handleLogout} /> 
    </div>
  )
}

interface HeaderMenuProps {
  handleHeaderLinkClick:  (key: string) => void
  handleLogout: () => void
}

function HeaderMenu(props: HeaderMenuProps) {
  const {
    handleHeaderLinkClick,
    handleLogout
  } = props
  const [menuOpen, setMenuOpen] = useState(false)

  const handlePlanetOpen = () => {
    console.log(!menuOpen)
    setMenuOpen((prev) => !prev)
  }

  return (
    <div
      style={{
        position: "absolute",
        top: 200,
        left: 500,
      }}
    >
      <Planet
        centerContent={
          <div
            onMouseDown={(e: React.MouseEvent) => e.stopPropagation()}
            onMouseUp={handlePlanetOpen}
            style={{
              position: "absolute",
              width: 66,
              height: 66,
              borderRadius: "50%",
              backgroundColor: "#25262b",
              transform: "translate(-50%, -50%)",
            }}
          />
        }
        autoClose
        open={menuOpen}
        hideOrbit
        orbitRadius={80}
        rotation={0}
      >
        <div className="ctxt-button"
          onMouseDown={(e: React.MouseEvent) => e.stopPropagation()}
          onMouseUp={handleLogout}
          style={{
            width: 60,
            height: 60,
            backgroundColor: "#25262b",
            filter: "none",
          }}
          children={<IconLogout />}
        />
        <div className="ctxt-button"
          onMouseDown={(e: React.MouseEvent) => e.stopPropagation()}
          onMouseUp={() => handleHeaderLinkClick("profile")}
          style={{
            width: 60,
            height: 60,
            backgroundColor: "#25262b",
            filter: "none",
          }}
          children={
            <IconUser
            />
          }
        />
        <div/>
        <div/>
        <div/>
        <div/>
        <div/>
      </Planet>
    </div>
  )
}

interface HeaderTabsProps {
  handleHeaderLinkClick: (key: string) => void
}

function HeaderTabs(props: HeaderTabsProps) {
  const {
    handleHeaderLinkClick
  } = props

  const handleHeaderLinkClickLocal = (tab: string) => (e: React.MouseEvent) => {
    if (e.button === 2) return
    handleHeaderLinkClick(tab)
  }

  return (
    <div
      style={{
        position: "relative",
        display: "flex",
        justifyContent:"center",
        alignItems:"center",

      }}
    >
      <div
        onClick={handleHeaderLinkClickLocal("search")}
        style={{
          position: "relative",
          width: 66,
          height: 66,
          borderRadius: "50%",
          backgroundColor: "#25262b",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: 5,
        }}
      >
        Search
      </div>
      <div
        onClick={handleHeaderLinkClickLocal("history")}
        style={{
          position: "relative",
          width: 66,
          height: 66,
          borderRadius: "50%",
          backgroundColor: "#25262b",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: 5,
        }}
      >
        History
      </div>
    </div>
  )
}