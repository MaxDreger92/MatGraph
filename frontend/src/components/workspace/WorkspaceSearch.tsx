import toast from 'react-hot-toast'
import client from '../../client'
import { saveBlobAsFile } from '../../common/workspaceHelpers'
import { useSpring, animated } from 'react-spring'
import { useState } from 'react'
import { Button, Checkbox, Flex, Select } from '@mantine/core'
import { useForm } from '@mantine/form'

interface WorkspaceSearchProps {
    workflow: string | null
    darkTheme: boolean
}

export default function WorkspaceSearch(props: WorkspaceSearchProps) {
    const { workflow, darkTheme } = props
    const [advancedHovered, setAdvancedHovered] = useState(false)
    const [showAdvanced, setShowAdvanced] = useState(false)

    type SearchFormValues = typeof searchForm.values

    const searchForm = useForm({
        initialValues: {
            format: 'csv',
            zip: false,
        },
    })

    const handleSubmit = (formValues: SearchFormValues) => {
        workflowSearch(formValues)
    }

    async function workflowSearch(params: SearchFormValues) {
        try {
            const response = await client.workflowSearch(workflow)
            if (response) {
                saveBlobAsFile(response.data, 'workflows.csv')
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    const springProps = useSpring({
        height: showAdvanced ? 100 : 0,
        width: showAdvanced ? '100%' : '0%',
        advancedMarginBottom: showAdvanced ? 12 : 20,
    })

    return (
        <animated.div
            className="workspace-search"
            style={{
                paddingBottom: showAdvanced ? 10 : 0,
                borderBottom: `1px solid ${darkTheme ? '#333' : '#ced4da'}`,
            }}
        >
            <Button
                onClick={() => handleSubmit(searchForm.values)}
                type="submit"
                radius="xl"
                style={{
                    alignSelf: 'center',
                    marginBottom: 25,
                    width: 160,
                    height: 40,
                    marginTop: 25,
                    fontSize: 14,
                }}
            >
                Search Database
            </Button>
            <animated.p
                onClick={() => setShowAdvanced((prev) => !prev)}
                onMouseEnter={() => setAdvancedHovered(true)}
                onMouseLeave={() => setAdvancedHovered(false)}
                style={{
                    fontSize: 13,
                    height: 10,
                    // marginBottom: springProps.advancedMarginBottom,
                    marginBottom: 16,
                    textDecoration: showAdvanced || advancedHovered ? 'underline' : 'none',
                    cursor: 'pointer',
                    // color: advancedHovered ? (darkTheme ? '#ced4da' : '#c1c2c5') : (darkTheme ? '#' : '#000'),
                }}
            >
                Advanced Search
            </animated.p>
            <animated.div
                style={{
                    boxShadow: 'inset 0px 1px 3px rgba(0,0,0,0.3)',
                    // width: springProps.width,
                    backgroundColor: darkTheme ? '#212226' : '#f8f9fa',
                    width: '100%',
                    height: springProps.height,
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: showAdvanced ? 'visible' : 'hidden',
                }}
            >
                {/* Output format row*/}
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'row',
                        position: 'relative',
                        padding: 10,
                    }}
                >
                    <Select
                        label="Output format:"
                        defaultValue="csv"
                        data={[
                            { value: 'csv', label: 'CSV' },
                            { value: 'json', label: 'JSON' },
                        ]}
                        onChange={(e) => searchForm.setFieldValue('format', e ?? '')}
                        style={{
                            width: 120,
                        }}
                    />

                    <Checkbox
                        label="Zip"
                        labelPosition="right"
                        checked={searchForm.values.zip}
                        onChange={(e) => searchForm.setFieldValue('zip', e.currentTarget.checked)}
                        style={{
                            position: 'relative',
                            marginLeft: 20,
                            paddingTop: 40,
                        }}
                        sx={{
                            label: {
                                position: 'relative',
                                top: -8,
                                left: -5,
                            },
                        }}
                    />
                </div>
            </animated.div>
        </animated.div>
    )
}
