import { useContext } from 'react'
import { Chemical } from '../types/configuration.types'
import { OpentronsContext } from '../context/OpentronsContext'

interface ChemicalListProps {
    wellVolume: number
    chemicals: Chemical[]
    width: number
}

export default function ChemicalList(props: ChemicalListProps) {
    const { wellVolume, chemicals, width } = props

    const { currentConfig, setCurrentConfig } = useContext(OpentronsContext)

    // const addChemical = ()

    return (
        <div
            style={{
                width: '100%',
            }}
        >
            Chemicals
            <table
                style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    textAlign: 'left',
                    marginTop: 10,
                }}
            >
                <thead
                    style={{
                        backgroundColor: '#e3e3e3',
                        height: 35,
                    }}
                >
                    <tr>
                        <th
                            style={{
                                padding: '5px 0 5px 5px',
                                fontWeight: 400,
                                fontSize: 14,
                                width: width < 420 ? '50%' : 190,
                            }}
                        >
                            Name
                        </th>
                        <th
                            style={{
                                padding: '5px 0 5px 5px',
                                fontWeight: 400,
                                fontSize: 14,
                                width: width < 420 ? '50%' : width - 190,
                            }}
                        >
                            Volume
                        </th>
                    </tr>
                </thead>
                <tbody
                    style={{
                        backgroundColor: '#DDD',
                    }}
                >
                    {chemicals.map((chemical, index) => (
                        <tr key={index} style={{ height: 35 }}>
                            <td
                                style={{
                                    // borderBottom: '1px solid #ccc',
                                    padding: '5px 0 5px 5px',
                                    fontWeight: 400,
                                    fontSize: 14,
                                }}
                            >
                                {chemical.name}
                            </td>
                            <td
                                style={{
                                    // borderBottom: '1px solid #ccc',
                                    padding: '5px 0 5px 5px',
                                    fontWeight: 400,
                                    fontSize: 14,
                                }}
                            >
                                {chemical.volume.value} {chemical.volume.unit} / {(chemical.volume.value / wellVolume * 100).toFixed(2)}%
                            </td>
                        </tr>
                    ))}
                    <tr>
                        <td
                            style={{
                                height: 35,
                                padding: '5px 0 5px 5px',
                                fontWeight: 400,
                                fontSize: 14,
                                backgroundColor: '#f5f5f5',
                                boxSizing: 'border-box',
                                border: '2px dashed #DDD',
                            }}
                        >
                            <input
                                type="text"
                                placeholder=''
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    backgroundColor: 'inherit',
                                    border: 'none',
                                    outline: 'none'
                                }}
                            />
                        </td>
                        <td
                            style={{
                                height: 35,
                                padding: '5px 0 5px 5px',
                                fontWeight: 400,
                                fontSize: 14,
                                backgroundColor: '#f5f5f5',
                                boxSizing: 'border-box',
                            }}
                        ></td>
                    </tr>
                </tbody>
            </table>
        </div>
    )
}
