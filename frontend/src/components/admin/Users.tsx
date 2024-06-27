import { useEffect, useState } from "react"
import { MDB_IUser as IUser } from "../../types/user.type"
import client from "../../client"
import toast from "react-hot-toast"
import { useQuery, useQueryClient } from "react-query"
import { TableRow } from "../../types/workflow.types"
import UserTable from "./UserTable"



export default function Users() {
    const { data: userList } = useQuery<Partial<IUser>[] | undefined>(
        "getUserList",
        client.getUserList
    )
    const [tableRows, setTableRows] = useState<TableRow[]>([])

    useEffect(() => {
        if (userList) setTableRows(prev => convertToTableRows(userList))
    }, [userList])

    const convertToTableRows = (userList: Partial<IUser>[]): TableRow[] => {
        return userList.map(user => {
            const tableRow: TableRow = {
                email: user.email || '',
                username: user.username || '',
                roles: user.roles ? user.roles.join(', ') : '',
                confirmed: user.confirmed || false,
                verified: user.verified || false,
            }
            return tableRow 
        })
    }

    const convertToMoreTableRows = (userList: Partial<IUser>[]): TableRow[] => {
        const repeatedUserList: TableRow[] = [];
    
        userList.forEach(user => {
            const tableRow: TableRow = {
                email: user.email || '',
                username: user.username || '',
                roles: user.roles ? user.roles.join(', ') : '',
                confirmed: user.confirmed || false,
                verified: user.verified || false,
            };
    
            for (let i = 0; i < 5; i++) {
                repeatedUserList.push({...tableRow}); // push a copy of tableRow to ensure each entry is distinct
            }
        });
    
        return repeatedUserList;
    };

    return (
        <div
            className="users"
            style={{
                position: "relative",
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 1040,
                height: 340,
                top: 70,
                margin: '0 auto',
                borderRadius: '10px',
                border: '1px solid #373a40',
                padding: 10,
                // outlineWidth: 1,
                // outlineOffset: 20,
                // outlineColor: '#373a40',
                // outlineStyle: 'solid',
                // overflow: 'hidden',
            }}
        >
            {userList &&
                <UserTable tableRows={convertToMoreTableRows(userList)} />
            }
        </div>
    )
}