import React, { useContext, useEffect, useRef, useState } from "react"
import { TableRow } from "../../types/workflow.types"
import WorkflowContext from "./context/WorkflowContext"
import { useMantineColorScheme } from "@mantine/core"

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

    const { tableViewHeight } = useContext(WorkflowContext)

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

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
                                height: '33%',
                                width: 21,
                                left: -1,
                                backgroundColor: hoveredTableTab === index || currentTableId === tab.tabId ? darkTheme ? '#2C2E33' : '#f8f9fa' : darkTheme ? '#212226' : '#d9dadb',
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
                                        {tableViewHeight > 300 ? tab.tabName : tableViewHeight > 200 ? tab.tabAbbr : index}
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

const TABLE_TABS: {tabName: string, tabAbbr: string, tabId: string}[] = [
    {tabName: 'SOURCE', tabAbbr: 'SRC', tabId: 'csvTable'},
    {tabName: 'LABELS', tabAbbr: 'LBL', tabId: 'labelTable'},
    {tabName: 'ATTRS', tabAbbr: 'ATT', tabId: 'attributeTable'},
]