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
  useMantineColorScheme,
} from "@mantine/core"
import logo from "../img/logo.png"
import logo_light from "../img/logo_light.png"

import {MDB_IUser as IUser} from "../types/user.type"
import client from "../client"

// export interface AuthenticationFormValues {
//     email: string,
//     name: string,
//     password: string,
//     terms: boolean,
// }

export default function Authentication() {
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
    onSuccess: (data) => {
      queryClient.prefetchQuery<IUser | null | undefined>('getCurrentUser', client.getCurrentUser)
      toast.success(data.message)
      // setTab("")
      navigate("/")
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  const registerMutation = useMutation(register, {
    onSuccess: (data) => {
      toast.success(data.message)
      toggle()
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  const [type, toggle] = useToggle(["login", "register"])

  const form = useForm({
    initialValues: {
      username: "",
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
      return response.data
    } catch (err: any) {
      throw err
    }
  }

  async function register(credentials: FormValues) {
    try {
      const { username, email, password } = credentials
      const response = await client.register(username, email, password)
      return response.data
    } catch (err: any) {
      throw err
    }
  }

  const { colorScheme, toggleColorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'

  return (
    <div className="wrap-login">
      <Paper radius="md" p="xl" withBorder>
        <img
          src={darkTheme ? logo : logo_light}
          alt="matGraphAI Logo"
          className="login-logo"
          style={{
            filter: `drop-shadow(2px 2px 2px ${darkTheme ? "#111" : "#bbb"})`
          }}
        />
        {/* <Text size="lg" weight={500}>
          Welcome to matGraphAI, {type} with
        </Text> */}

        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            {type === "register" && (
              <TextInput
                label="Username"
                placeholder="Your username"
                value={form.values.username}
                onChange={(event) =>
                  form.setFieldValue("username", event.currentTarget.value)
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
              error={form.errors.email}
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
              error={form.errors.password}
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