import { useEffect, useState } from "react"
import { useMutation, useQueryClient } from "react-query"
import { userContext } from "../common/userContext"
import { useContext } from "react"
import { toast } from "react-hot-toast"
import { useNavigate } from "react-router-dom"
import { useToggle, upperFirst } from "@mantine/hooks"
import { useForm } from "@mantine/form"
import {
  TextInput,
  PasswordInput,
  Text,
  Paper,
  Group,
  PaperProps,
  Button,
  Checkbox,
  Anchor,
  Stack,
} from "@mantine/core"
import logo from "../img/logo.png"

import IUser from "../types/user.type"
import client from "../client"

// export interface AuthenticationFormValues {
//     email: string,
//     name: string,
//     password: string,
//     terms: boolean,
// }

interface AuthenticationFormProps {
  setTab: (tab: string) => void
}

export default function AuthenticationForm(props: AuthenticationFormProps) {
  const { setTab } = props
  const queryClient = useQueryClient()
  const currentUser = useContext(userContext)
  const navigate = useNavigate()
  const [message, setMessage] = useState("")

  useEffect(() => {
    if (currentUser) {
      navigate("/") //manually navigate home if user is already logged in
    }
  })

  const loginMutation = useMutation("login", login, {
    onSuccess: () => {
      queryClient.prefetchQuery<IUser | null | undefined>('getCurrentUser', client.getCurrentUser)
      toast.success("User logged in successfully!")
      setTab("")
      navigate("/")
    },
    onError: () => {
      toast.error("User could not be logged in!")
    },
  })

  const registerMutation = useMutation(register, {
    onSuccess: () => {
      toast.success("User created successfully!")
      toggle()
    },
    onError: () => {
      toast.error("User could not be created.")
    },
  })

  const [type, toggle] = useToggle(["login", "register"])

  const form = useForm({
    initialValues: {
      name: "",
      email: "",
      password: "",
      terms: true,
    },

    validate: {
      email: (val) => (/^\S+@\S+$/.test(val) ? null : "Invalid email"),
      password: (val) =>
        val.length < 6
          ? "Password should include at least 6 characters"
          : null,
    },
  })

  type FormValues = typeof form.values

  const handleSubmit = (formValues: FormValues) => {
    if (type === "login") {
      loginMutation.mutate(formValues)
      return
    }
    if (formValues.terms) {
      registerMutation.mutate(formValues)
      return
    }
    //Throw Error
  }

  async function login(credentials: FormValues) {
    try {
      const { email, password } = credentials
      const response = await client.login(email, password)
      const token = response.data.token

      if (token) {
        document.cookie = `token=${token}`
      }
      return
    } catch (err: any) {
      setMessage(
        (err.response && err.response.data && err.response.data.message) ||
          err.message ||
          err.toString()
      )
      throw new Error("Login failed")
    }
  }

  async function register(credentials: FormValues) {
    try {
      const { name, email, password } = credentials
      const response = await client.register(name, email, password)
      return response.data
      // setMessage(response.data.message);
    } catch (err: any) {
      // setMessage(
      //   (err.response &&
      //     err.response.data &&
      //     err.response.data.message) ||
      //     err.message ||
      //     err.toString()
      // );
      throw new Error("Registration failed")
    }
  }

  return (
    <div className="wrap-login">
      <Paper radius="md" p="xl" withBorder {...props}>
        <img src={logo} alt="matGraphAI Logo" className="login-logo" />
        {/* <Text size="lg" weight={500}>
          Welcome to matGraphAI, {type} with
        </Text> */}

        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            {type === "register" && (
              <TextInput
                label="Name"
                placeholder="Your name"
                value={form.values.name}
                onChange={(event) =>
                  form.setFieldValue("name", event.currentTarget.value)
                }
                radius="md"
              />
            )}

            <TextInput
              required
              label="Email"
              placeholder="hello@matGraph.AI"
              value={form.values.email}
              onChange={(event) =>
                form.setFieldValue("email", event.currentTarget.value)
              }
              error={form.errors.email && "Invalid email"}
              radius="md"
            />

            <PasswordInput
              required
              label="Password"
              placeholder="Your password"
              value={form.values.password}
              onChange={(event) =>
                form.setFieldValue("password", event.currentTarget.value)
              }
              error={
                form.errors.password &&
                "Password should include at least 6 characters"
              }
              radius="md"
            />

            {type === "register" && (
              <Checkbox
                label="I accept terms and conditions"
                checked={form.values.terms}
                onChange={(event) =>
                  form.setFieldValue("terms", event.currentTarget.checked)
                }
              />
            )}
          </Stack>

          <Group position="apart" mt="xl">
            <Anchor
              component="button"
              type="button"
              color="dimmed"
              onClick={() => toggle()}
              size="xs"
            >
              {type === "register"
                ? "Already have an account? Login"
                : "Don't have an account? Register"}
            </Anchor>
            <Button type="submit" radius="xl">
              {upperFirst(type)}
            </Button>
          </Group>
        </form>
      </Paper>
    </div>
  )
}