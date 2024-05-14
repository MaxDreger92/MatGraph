import toast from 'react-hot-toast'
import client from '../../client'
import { saveBlobAsFile } from '../../common/workflowHelpers'
import { useSpring, animated } from 'react-spring'
import { useState } from 'react'
import { Button, Checkbox, Flex, Select } from '@mantine/core'
import { useForm } from '@mantine/form'

interface WorkflowSearchProps {
    workflow: string | null
    darkTheme: boolean
}

export default function WorkflowSearch(props: WorkflowSearchProps) {
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
            className="workflow-search"
            style={{
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                alignItems: 'center',
                width: '100%',
                height: 'auto',
                padding: '0 10px 0 10px',
                paddingBottom: showAdvanced ? 10 : 0,
                borderBottom: `1px solid ${darkTheme ? '#333' : '#ced4da'}`,
            }}
        >
            <Button
                onClick={() => handleSubmit}
                type="submit"
                radius="sm"
                style={{
                    alignSelf: 'center',
                    marginBottom: 25,
                    width: 170,
                    height: 60,
                    marginTop: 25,
                    fontSize: 14,
                }}
            >
                {'Search Database'}
            </Button>
            <animated.p
                onClick={() => setShowAdvanced((prev) => !prev)}
                onMouseEnter={() => setAdvancedHovered(true)}
                onMouseLeave={() => setAdvancedHovered(false)}
                style={{
                    fontSize: 13,
                    height: 10,
                    marginBottom: springProps.advancedMarginBottom,
                    // color: advancedHovered ? (darkTheme ? '#ced4da' : '#c1c2c5') : (darkTheme ? '#' : '#000'),
                    textDecoration: showAdvanced || advancedHovered ? 'underline' : 'none',
                    cursor: 'pointer',
                }}
            >
                Advanced Search
            </animated.p>
            <animated.div
                style={{
                    // boxShadow: 'inset 0px 1px 3px rgba(0,0,0,0.3)',
                    // width: springProps.width,
                    width: "100%",
                    height: springProps.height,
                    // backgroundColor: darkTheme ? '#212226' : '#f8f9fa',
                    display: 'flex',
                    flexDirection: 'column',
                    // alignItems: 'center',
                    // justifyContent: 'center',
                    overflow: showAdvanced ? "visible" : "hidden",
                }}
            >

                {/* Output format row*/}
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'row',
                        position: "relative",
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
                        labelPosition='right'
                            checked={searchForm.values.zip}
                            onChange={(e) =>
                                searchForm.setFieldValue('zip', e.currentTarget.checked)
                            }
                            style={{
                                position: "relative",
                                marginLeft: 30,
                                paddingTop: 40,
                            }}
                            sx={{
                                label: {
                                    position: "relative",
                                    top: -8,
                                    left: -5,
                                }
                            }}
                        />
                        {/* <p style={{ height: 25, marginBottom: 10, fontSize: 15 }}>Zip:</p> */}
                </div>
            </animated.div>
        </animated.div>
    )
}
