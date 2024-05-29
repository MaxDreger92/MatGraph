interface LegalNoticeProps {
    setLegalTab: React.Dispatch<React.SetStateAction<number>>
    scrollToTop: () => void
}

export default function LegalNotice(props: LegalNoticeProps) {
    const { setLegalTab, scrollToTop } = props

    return (
        <div
            style={{
                maxWidth: 750,
            }}
        >
            <h2>Legal Notice</h2>
            <p style={{ fontSize: 15, transform: 'translate(0, -0px)' }}>
                matGraph operates under the same legal framework and notices as{' '}
                <a
                    href="https://www.fz-juelich.de/en/legal-notice"
                    className="custom-link"
                    style={{ color: '#1971c2' }}
                >
                    Forschungszentrum Jülich GmbH
                </a>
                . (Effective 05.28.24)
            </p>
            <br />
            <h5>Forschungszentrum Jülich GmbH</h5>
            <br />
            <p>
                Wilhelm-Johnen-Straße
                <br />
                52428 Jülich
                <br />
                <br />
                Postal address:
                <br />
                52425 Jülich
                <br />
                <br />
                Delivery address:
                <br />
                Leo-Brandt-Straße
                <br />
                52428 Jülich
                <br />
                <br />
                Entered in the Commercial Register of the District Court of Düren, Germany: No. HR B
                3498
                <br />
                Value Added Tax ID No. in accordance with § 27 a of the German VAT Law
                <br />
                (Umsatzsteuergesetz): DE 122624631 Tax No.: 213/5700/0033
            </p>
            <br />
            <h5>Board of Directors</h5>
            <br />
            <p>
                <ul>
                    <li>Prof. Dr. Astrid Lambrecht (Chair of the Board of Directors)</li>
                    <li>Karsten Beneke (Vice-Chairman)</li>
                    <li>Dr. Ir. Pieter Jansens</li>
                </ul>
            </p>
            <br />
            <h5>Supervisory Board</h5>
            <br />
            <p>Ministerialdirektor Stefan Müller</p>
            <br />
            <h5>Responsible in the sense of § 18, Abs. 2, Medienstaatsvertrag (MStV)</h5>
            <br />
            <p>
                Dr. Anne Rother
                <br />
                Forschungszentrum Jülich
                <br />
                Leiterin Unternehmenskommunikation
                <br />
                Wilhelm-Johnen-Straße, 52428 Jülich
            </p>
            <br />
            <h5>Contact</h5>
            <br />
            <p>
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
            </p>
            <br />
            <h5>Copyright</h5>
            <br />
            <p>
                Copyright and all other rights concerning this website are held by Forschungszentrum
                Jülich GmbH. Use of the information contained on the website, including excerpts, is
                permitted for educational, scientific or private purposes, provided the source is
                quoted (unless otherwise expressly stated on the respective website). Use for
                commercial purposes is not permitted unless explicit permission has been granted by
                Forschungszentrum Jülich.
                <br />
                <br />
                For further information, contact:{' '}
                <a
                    href="https://www.fz-juelich.de/en/press/contact-corporate-communications"
                    style={{ color: '#1971c2' }}
                    className="custom-link"
                >
                    Corporate Communications
                </a>
            </p>
            <br />
            <h5>Disclaimer</h5>
            <br />
            <h6>Contents of this Website </h6>
            <br />
            <p>
                This website has been compiled with due diligence. However, Forschungszentrum Jülich
                neither guarantees nor accepts liability for the information being continual
                up-to-date, complete or accurate.
            </p>
            <br />
            <h6>Links to External Websites</h6>
            <br />
            <p>
                This website may contain links to external third-party websites. These links to
                third party sites do not imply approval of their contents. Responsibility for the
                content of these websites lies solely with the respective provider or operator of
                the site. Illegal contents were not recognizable at the time of setting the link. We
                do not accept any liability for the continual accessibility or up-to-dateness,
                completeness or correctness of the contents of such websites. If we become aware of
                any infringements of the law, we will remove such links immediately.
            </p>
            <br />
            <h6>Data protection</h6>
            <br />
            <p>
                Every time a user accesses a website hosted by Forschungszentrum Jülich GmbH and
                every time a file is requested, data connected to these processes are stored in a
                log. These data do not contain personal information; we are unable to trace which
                user accessed what information. Personal user profiles therefore cannot be created.
                The data that is saved and will be used for statistical purposes only. This
                information will not be disclosed to third parties.
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
        </div>
    )
}
