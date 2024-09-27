import { useContext, useEffect, useState } from 'react'
import { Chemical } from '../types/configuration.types'
import { OpentronsContext } from '../context/OpentronsContext'
import Select from 'react-select'
import { chemicalData } from '../data/chemicals.data'

interface ChemicalListProps {
    wellVolume: number
    chemicals: Chemical[]
    width: number
}

interface OptionType {
    value: string
    label: string
}

export default function ChemicalList(props: ChemicalListProps) {
    const { wellVolume, chemicals, width } = props
    const [selectOptions, setSelectOptions] = useState<OptionType[]>([])

    const { currentConfig, setCurrentConfig } = useContext(OpentronsContext)

    useEffect(() => {
        setSelectOptions(() => {
            const newOptions: OptionType[] = Object.keys(chemicalData).map(key => ({
                value: key,
                label: key
            }))
            return newOptions
        })
    }, [])

    const selectOptionsFromChemicalData = (data: { [key: string]: string }) => {
        return Object.keys(data).map(key => ({
            value: key,
            label: key,
        }))
    }

    // const addChemical = ()

    return (
        <div
            style={{
                position: 'relative',
                width: '100%',
            }}
        >
            {/* Table Header */}
            Chemicals
            <table
                style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    textAlign: 'left',
                    marginTop: 10,
                }}
            >
                {/* Header Row */}
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
                {/* Content Rows */}
                <tbody
                    style={{
                        backgroundColor: '#DDD',
                    }}
                >
                    {/* Chemicals */}
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
                                {chemical.volume.value} {chemical.volume.unit} /{' '}
                                {((chemical.volume.value / wellVolume) * 100).toFixed(2)}%
                            </td>
                        </tr>
                    ))}

                    {/* New Chemical Row */}
                    <tr>
                        {/* New Chemical Name */}
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
                            {/* <input
                                type='text'
                                placeholder=''
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    backgroundColor: 'inherit',
                                    border: 'none',
                                    outline: 'none',
                                }}
                            /> */}
                            <Select<OptionType>
                                defaultValue={null}
                                isClearable
                                isSearchable
                                name='chemical'
                                options={selectOptions}
                                menuPosition='fixed'
                                menuPortalTarget={document.body}
                                styles={SELECT_STYLES}
                            />
                        </td>

                        {/* New Chemical Volume */}
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
                                type='text'
                                placeholder=''
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    backgroundColor: 'inherit',
                                    border: 'none',
                                    outline: 'none',
                                }}
                            />
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    )
}

const SELECT_STYLES = {
    control: (base: any, state: any) => ({
        ...base,
        border: 'none',
        backgroundColor: 'transparent',
        boxShadow: 'none',
    }),
    menu: (base: any) => ({
        ...base,
        backgroundColor: '#f5f5f5',
        color: '#333'
    }),
    option: (base: any, state: any) => ({
        ...base,
        backgroundColor: state.isSelected
            ? '#ff9519'
            : state.isFocused
            ? '#DDD'
            : 'transparent',
        color: '#333',
        '&:active': {
            backgroundColor: '#ffdcb2',
        },
    })
}
