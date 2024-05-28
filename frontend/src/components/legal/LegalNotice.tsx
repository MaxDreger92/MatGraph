interface LegalNoticeProps {
    setLegalTab: React.Dispatch<React.SetStateAction<number>>
    scrollToTop: () => void
}

export default function LegalNotice(props: LegalNoticeProps) {
    const { setLegalTab, scrollToTop } = props

    return (
        <>
            <h2>Legal Notice</h2>
            <span style={{ fontSize: 14, transform: 'translate(0, -50px)'}}>
                matGraph operates under the same legal framework and notices as
                <br />
                <a href="https://www.fz-juelich.de/en/legal-notice" className="custom-link" style={{ color: '#1971c2' }}>Forschungszentrum Jülich GmbH</a>.
            </span>
            <br />
            <br />
            <p>
                <h5>Forschungszentrum Jülich GmbH</h5>
                <br />
                <span style={{ fontSize: 14 }}>
                    Wilhelm-Johnen-Straße
                    <br />
                    52428 Jülich
                </span>
                <br />
                <span style={{ fontSize: 14 }}>
                    <br />
                    Postal address:
                    <br />
                    52425 Jülich
                </span>
                <br />
                <span style={{ fontSize: 14 }}>
                    <br />
                    Delivery address:
                    <br />
                    Leo-Brandt-Straße
                    <br />
                    52428 Jülich
                </span>
                <br />
                <span style={{ fontSize: 14 }}>
                    <br />
                    Entered in the Commercial Register of the District Court of Düren, Germany: No.
                    HR B 3498
                    <br />
                    Value Added Tax ID No. in accordance with § 27 a of the German VAT Law
                    <br />
                    (Umsatzsteuergesetz): DE 122624631 Tax No.: 213/5700/0033
                </span>
            </p>
            <p>
                <span style={{ fontSize: 14 }}>
                    <br />
                </span>
                <h5>Board of Directors</h5>
                <br />
                <span style={{ fontSize: 14 }}>
                    <ul>
                        <li>Prof. Dr. Astrid Lambrecht (Chair of the Board of Directors)</li>
                        <li>Karsten Beneke (Vice-Chairman)</li>
                        <li>Dr. Ir. Pieter Jansens</li>
                    </ul>
                </span>
            </p>
            <p>
                <span style={{ fontSize: 14 }}>
                    <br />
                </span>
                <h5>Supervisory Board</h5>
                <br />
                <span style={{ fontSize: 14 }}>
                    Ministerialdirektor Stefan Müller
                </span>
                <br />
                <br />
            </p>
            <p>
                <h5>
                        Responsible in the sense of § 18, Abs. 2, Medienstaatsvertrag (MStV)
                    </h5>
                <br />
                <span style={{ fontSize: 14 }}>
                    Dr. Anne Rother
                    <br />
                    Forschungszentrum Jülich
                    <br />
                    Leiterin Unternehmenskommunikation
                    <br />
                    Wilhelm-Johnen-Straße, 52428 Jülich
                </span>
                {/* <span style={{ fontSize: 14 }}>
                    <br />
                    &nbsp; &nbsp; - Prof. Dr. rer. nat. Michael Eikerling
                </span>
                <br />
                <span style={{ fontSize: 14 }}>
                    <br />
                    Institute of Energy and Climate Research (IEK)
                </span>
                <br />
                <span style={{ fontSize: 14 }}>
                    Theory and Computation of Energy Materials (IEK-13)
                </span>
                <br />
                <br />
                <span style={{ fontSize: 14 }}>Forschungszentrum Jülich GmbH</span>
                <br />
                <span style={{ fontSize: 14 }}>Wilhelm-Johnen-Straße</span>
                <br />
                <span style={{ fontSize: 14 }}>52428 Jülich</span> */}
            </p>
            <p>
                <span style={{ fontSize: 14 }}>
                    <br />
                </span>
                <h5>Contact</h5>
                <br />
                <span style={{ fontSize: 14 }}>
                    General inquiries: +49 2461 61-0
                    <br />
                    General fax no.: +49 2461 61-8100
                    <br />
                    <br />
                    Internet:{' '}
                    <a data-fr-linked="true" href="http://www.fz-juelich.de">
                        http://www.fz-juelich.de
                    </a>
                    <br />
                    Email address:{' '}
                    <a data-fr-linked="true" href="mailto:info@fz-juelich.de">
                        info@fz-juelich.de
                    </a>
                </span>
            </p>
            <p>
                <span style={{ fontSize: 14 }}>
                    <br />
                </span>
                <h5>Copyright</h5>
                <br />
                <span style={{ fontSize: 14 }}>
                    Copyright and all other rights concerning this website are held by
                    Forschungszentrum Jülich
                    <br />
                    GmbH. Use of the information contained on the website, including excerpts, is
                    permitted for
                    <br />
                    educational, scientific or private purposes, provided the source is quoted
                    (unless otherwise
                    <br />
                    expressly stated on the respective website). Use for commercial purposes is not
                    permitted unless
                    <br />
                    explicit permission has been granted by Forschungszentrum Jülich.
                    <br />
                    <br />
                    For further information, contact: <a href="https://www.fz-juelich.de/en/press/contact-corporate-communications" style={{color: '#1971c2'}} className="custom-link">Corporate Communications</a>
                </span>
            </p>
            <p>
                <span style={{ fontSize: 14 }}>
                    <br />
                </span>
                <h5>Disclaimer</h5>
                <br />
                <h6>Contents of this Website </h6>
                <br />
                <span style={{ fontSize: 14 }}>
                    This website has been compiled with due diligence.
                    However,
                    <br />
                    Forschungszentrum Jülich neither guarantees nor accepts liability for the
                    information being
                    <br />
                    continual up-to-date, complete or accurate.
                </span>
            </p>
            <p>
                <span style={{ fontSize: 14 }}>
                    <br />
                </span>
                <h6>Links to External Websites</h6>
                <br />
                <span style={{ fontSize: 14 }}>
                    This website may contain links to external third-party websites. These links to
                    third party sites do
                    <br />
                    not imply approval of their contents. Responsibility for the content of these
                    websites lies solely
                    <br />
                    with the respective provider or operator of the site. Illegal contents were not
                    recognizable at the
                    <br />
                    time of setting the link. We do not accept any liability for the continual
                    accessibility or up-to-
                    <br />
                    dateness, completeness or correctness of the contents of such websites. If we
                    become aware of
                    <br />
                    any infringements of the law, we will remove such links immediately.
                </span>
            </p>
            <p>
                <span style={{ fontSize: 14 }}>
                    <br />
                </span>
                <h6>Data protection</h6>
                <br />
                <span style={{ fontSize: 14 }}>
                    Every time a user accesses a website hosted by Forschungszentrum Jülich GmbH and
                    every
                    <br />
                    time a file is requested, data connected to these processes are stored in a log.
                    These data do not
                    <br />
                    contain personal information; we are unable to trace which user accessed what
                    information.
                    <br />
                    Personal user profiles therefore cannot be created. The data that is saved and
                    will be used for
                    <br />
                    statistical purposes only. This information will not be disclosed to third
                    parties.
                    <br />
                </span>
            </p>
            <p
                style={{ color: '#1971c2' }}
                className="custom-link"
                onClick={() => {
                    setLegalTab(1)
                    scrollToTop()
                }}
            >
                Further information on data protection
            </p>
        </>
    )
}
