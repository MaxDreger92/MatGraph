import React, { useState } from "react"
import { TableRow } from "../../types/workflow.types"

interface WorkflowTableTabsProps {
    progress: number
    currentTableId: string
    setCurrentTableFn: (tableId: string) => void
}

export default function WorkflowTableTabs(props: WorkflowTableTabsProps) {
    const {
        progress,
        currentTableId,
        setCurrentTableFn
    } = props
    const [hoveredTableTab, setHoveredTableTab] = useState<number | null>(null)

    return (
        <div
            style={{
                position: 'absolute',
                display: 'flex',
                flexDirection: 'column',
                height: 'calc(100% - 80px)',
                left: 0,
                top: 80,
                width: 22,
            }}
        >
            {TABLE_TABS.map((tab, index) => {
                if (progress > index) {
                    return (
                        <div
                            onMouseEnter={() => setHoveredTableTab(index)}
                            onMouseLeave={() => setHoveredTableTab(null)}
                            onMouseUp={() => setCurrentTableFn(tab.tabId)}
                            style={{
                                position: 'relative',
                                height: 106,
                                width: 21,
                                left: -1,
                                backgroundColor: hoveredTableTab === index || currentTableId === tab.tabId ? '#2C2E33' : '#212226',
                                border: `1px solid ${currentTableId === tab.tabId ? '#373A40' : '#333'}`,
                                borderRadius: '0 10px 10px 0',
                                cursor: 'pointer',
                                display: 'flex',
                                textAlign: 'center',
                                verticalAlign: 'center',
                                zIndex: 10,
                            }}
                            children={

                                    <span
                                        style={{
                                            fontSize: 11,
                                            writingMode: 'vertical-rl',
                                            textOrientation: 'upright'
                                        }}
                                    >
                                        {tab.tabName}
                                    </span>

                                
                            }
                        />
                    )
                }
                return false
                
            })}

        </div>
    )
}

const TABLE_TABS: {tabName: string, tabId: string}[] = [
    {tabName: 'CSV', tabId: 'csvTable'},
    {tabName: 'LABELS', tabId: 'labelTable'},
    {tabName: 'ATTRS', tabId: 'attributeTable'},
]