import { useEffect, useContext } from "react"
import { useNavigate } from "react-router-dom"
import { useMutation, useQuery } from "react-query"
import IUser from "../types/user.type"
import client from "../client"
import { userContext } from "../common/userContext"
import { toast } from "react-hot-toast"
import { useForm } from "@mantine/form"
import {
  Paper,
  PaperProps,
  TextInput,
  Button
} from "@mantine/core"

export default function Account(props: PaperProps) {
  const currentUser = useContext(userContext)

  const nameMutation = useMutation("updateName", updateName, {
    onSuccess: () => {
      toast.success("Update name successful.")
    },
    onError: () => {
      toast.error("Name could not be updated.")
    }
  })

  const mailMutation = useMutation("updateMail", updateMail, {
    onSuccess: () => {
      toast.success("Update email successful.")
    },
    onError: () => {
      toast.error("Email could not be updated.")
    }
  })

  const passwordMutation = useMutation("updatePassword", updatePassword, {
    onSuccess: () => {
      toast.success("Update password succesful.")
    },
    onError: () => {
      toast.error("Password could not be updated.")
    }
  })

  const nameForm = useForm({
    initialValues: {
      name: ""
    },
  })

  const mailForm = useForm({
    initialValues: {
      email: ""
    },
  })

  const passwordForm = useForm({
    initialValues: {
      oldPass: "",
      newPass: "",
      confirmNewPass: ""
    },

    validate: {
      confirmNewPass: (value, values) => 
        value !== values.newPass ? "Passwords do not match." : null,
    }
  })

  type NameFormValues = typeof nameForm.values
  type MailFormValues = typeof mailForm.values
  type PasswordFormValues = typeof passwordForm.values

  const handleNameSubmit = (formValues: NameFormValues) => {
    nameMutation.mutate(formValues)
  }

  const handleMailSubmit = (formValues: MailFormValues) => {
    mailMutation.mutate(formValues)
  }

  const handlePasswordSubmit = (formValues: PasswordFormValues) => {
    passwordMutation.mutate(formValues)
  }

  async function updateName(credentials: NameFormValues) {
    try {
      const { name } = credentials
      const response = await client.updateName(name)
      return
    } catch (err:any) {

    }
  }

  async function updateMail(credentials: MailFormValues) {
    try {
      const { email } = credentials
      const response = await client.updateMail(email)
    } catch (err: any) {

    }
  }

  async function updatePassword(credentials: PasswordFormValues) {
    try {
      const { oldPass, newPass} = credentials
      const response = await client.updatePassword(newPass, oldPass)
    } catch (err: any) {

    }
  }

  return (

    <div className="wrap-account">
      {currentUser && (
        <Paper radius="md" p="xl" withBorder {...props}>
        <h3>Account</h3>
        <form onSubmit={nameForm.onSubmit(handleNameSubmit)}>
          <TextInput
            label="Name"
            placeholder={currentUser.name}
            value={nameForm.values.name}
            onChange={(event) =>
              nameForm.setFieldValue("name", event.currentTarget.value)
            }
            radius="md"
          />
          <Button type="submit" radius="xl">
            Update name
          </Button>
        </form>
        <form onSubmit={mailForm.onSubmit(handleMailSubmit)}>
          <TextInput
            label="Email"
            // placeholder={currentUser.email}
            value={currentUser.email}
            onChange={(event) =>
              nameForm.setFieldValue("email", event.currentTarget.value)
            }
            radius="md"
          />
          <Button type="submit" radius="xl">
            Update email
          </Button>
        </form>
        <form onSubmit={passwordForm.onSubmit(handlePasswordSubmit)}>

        </form>
      </Paper>
      )}
    </div>


    // <div className="container">
    //   {currentUser && (
    //     <div>
    //       {/* <header className="jumbotron"> */}
    //         <h3>
    //           {currentUser.name && (
    //             <strong>{currentUser.name}</strong>
    //           )}
    //            <strong>'s Account</strong>
    //         </h3>
    //       {/* </header> */}
    //       <p>
    //         <strong>Id:</strong> {currentUser.id}
    //       </p>
    //       <p>
    //         <strong>Email:</strong> {currentUser.email}
    //       </p>
    //       <strong>Authorities:</strong>
    //       <ul>
    //         {currentUser.roles &&
    //           currentUser.roles.map((role, index) => (
    //             <li key={index}>{role}</li>
    //           ))}
    //       </ul>
    //     </div>
    //   )}
    // </div>
  )
}
