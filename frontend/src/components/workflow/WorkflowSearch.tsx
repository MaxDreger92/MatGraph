import toast from 'react-hot-toast'
import client from '../../client'
import { saveBlobAsFile } from '../../common/workflowHelpers'
import { useSpring, animated } from 'react-spring'
import { useState } from 'react'
import { Button } from '@mantine/core'

interface WorkflowSearchProps {
    workflow: string | null
    darkTheme: boolean
}

export default function WorkflowSearch(props: WorkflowSearchProps) {
    const { workflow, darkTheme } = props
    const [advancedHovered, setAdvancedHovered] = useState(false)
    const [showAdvanced, setShowAdvanced] = useState(false)

    async function workflowSearch() {
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
        height: showAdvanced ? 150 : 0,
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
                onClick={workflowSearch}
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
                    textDecoration: showAdvanced || advancedHovered ? "underline" : "none",
                    cursor: "pointer",
                }}
            >
                Advanced Search
            </animated.p>
            <animated.div
                style={{
                    boxShadow: 'inset 0px 1px 3px rgba(0,0,0,0.3)',
                    width: springProps.width,
                    height: springProps.height,
                    backgroundColor: darkTheme ? '#212226' : '#f8f9fa',
                }}
            ></animated.div>
        </animated.div>
    )
}
