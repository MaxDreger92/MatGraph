import { useContext, useRef, useState } from 'react'
import LegalNotice from './LegalNotice'
import PrivacyPolicy from './PrivacyPolicy'
import { UserContext } from '../../common/UserContext'

export default function Legal() {
    const user = useContext(UserContext)
    const [legalTab, setLegalTab] = useState(0)

    const mainRef = useRef<HTMLDivElement>(null)

    const scrollToTop = () => {
        if (mainRef.current) {
            mainRef.current.scrollTo({
                top: 0,
                behavior: 'auto',
            })
        }
    }

    return (
        <div
            style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
            }}
        >
            <div
                style={{
                    position: 'absolute',
                    top: 35,
                    width: '15%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    zIndex: 10,
                    paddingLeft: '7.5%',
                }}
            >
                <p
                style={{
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    transform: 'translate(-50%,0)'
                }}
                    className="custom-link"
                    onClick={() => {
                        setLegalTab(0)
                        scrollToTop()
                    }}
                >
                    Legal Notice
                </p>
                <p
                    style={{
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        transform: 'translate(-50%,0)'
                    }}
                    className="custom-link"
                    onClick={() => {
                        setLegalTab(1)
                        scrollToTop()
                    }}
                >
                    Privacy Policy
                </p>
            </div>
            <main
                ref={mainRef}
                style={{
                    position: 'absolute',
                    top: 30,
                    width: '100%',
                    height: 'calc(100% - 50px)',
                    paddingLeft: 'max(15%,80px)',
                    overflow: 'auto',
                    zIndex: 5,
                }}
            >
                {legalTab === 0 ? (
                    <LegalNotice setLegalTab={setLegalTab} scrollToTop={scrollToTop} />
                ) : (
                    <PrivacyPolicy />
                )}
            </main>
        </div>
    )
}
