// TODO:
// - profile pic
// - decide on menu structure (inner tabs, animation?)

// Settings:
// - dont scale nodes on hover
// - show /hide name/institution etc. on uploads ..

// import { useEffect, useContext, useState } from "react"
// import { useNavigate } from "react-router-dom"
import { useMutation, useQuery } from "react-query"
import {MDB_IUser as IUser} from "../types/user.type"
import client from "../client"
// import { userContext } from "../common/userContext"
import { toast } from "react-hot-toast"
import { useForm } from "@mantine/form"
import { useQueryClient } from "react-query"
import {
  Paper,
  PaperProps,
  TextInput,
  Button,
  PasswordInput,
  useMantineColorScheme,
} from "@mantine/core"

import { PiLock, PiLockOpen } from "react-icons/pi"
import { RiImageEditLine } from "react-icons/ri"
import { useEffect, useRef, useState } from "react"
import { useSpring, animated } from "react-spring"
import user_img from "../img/user.png"
import user_img_light from "../img/user_light.png"

export default function Profile(props: PaperProps) {
  const queryClient = useQueryClient()
  const { data: currentUser } = useQuery<IUser | null | undefined>(
    "getCurrentUser",
    client.getCurrentUser
  )
  const [passwordLocked, setPasswordLocked] = useState(true)
  const [showUnlockPasswordForm, setShowUnlockPasswordForm] = useState(false)
  const [lockHovered, setLockHovered] = useState(false)
  const [imgHovered, setImgHovered] = useState(false)
  const emailRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  // shows new password form when current password could be authenticated
  const togglePasswordLock = () => {
    setShowUnlockPasswordForm(false)
    setPasswordLocked(false)
  }

  // shows current password form when clicking the lock
  const toggleUnlockPasswordForm = () => {
    if (passwordLocked) {
      setShowUnlockPasswordForm((prev) => !prev)
    } else {
      updateForm.setFieldValue("oldPassword", "")
      setShowUnlockPasswordForm(false)
      setPasswordLocked(true)
    }
  }

  const handleImgClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const img = files[0]
      updateImgMutation.mutate(img)
    }
  }

  // Form Setup #####################################

  type FormValues = typeof updateForm.values

  const updateForm = useForm({
    initialValues: {
      name: currentUser?.name || "",
      username: currentUser?.username || "",
      institution: currentUser?.institution || "",
      email: currentUser?.email || "",
      confirmEmail: "",
      password: "",
      confirmPassword: "",
      oldPassword: "",
    },

    validate: {
      email: (val, values) =>
        showUnlockPasswordForm
          ? null
          : val === currentUser?.email
          ? val === values.confirmEmail
            ? "Email is unchanged."
            : null
          : /^\S+@\S+$/.test(val)
          ? null
          : "Invalid email.",
      confirmEmail: (value, values) =>
        showUnlockPasswordForm
          ? null
          : value.length > 0
          ? value === values.email // check if confirmEmail == email
            ? null
            : "Emails do not match."
          : values.email !== currentUser?.email
          ? "Emails do not match."
          : null,
      password: (val) =>
        showUnlockPasswordForm
          ? null
          : val.length > 1 && val.length < 6
          ? "Password should include at least 6 characters"
          : null,
      confirmPassword: (value, values) =>
        showUnlockPasswordForm
          ? null
          : value === values.password
          ? null
          : "Passwords do not match.",
      oldPassword: (val) =>
        showUnlockPasswordForm && val.length < 1 ? "Password invalid." : null,
    },
  })


  useEffect(() => {
    if (currentUser)
      updateForm.setValues({
        name: currentUser.name || "",
        username: currentUser.username || "",
        institution: currentUser.institution || "",
        email: currentUser.email || "",
        confirmEmail: "",
        password: "",
        confirmPassword: "",
        oldPassword: "",
      })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUser])

  // Submit Handler #############################################

  const handleSubmit = (formValues: FormValues) => {
    if (showUnlockPasswordForm) {
      unlockPasswordMutation.mutate(formValues)
      return
    } else {
      // call mutations if needed

      if (formValues.name !== "") {
        if (formValues.name !== currentUser?.name) {
          nameMutation.mutate(formValues)
        }
      }

      if (formValues.username !== "") {
        if (formValues.username !== currentUser?.username) {
          usernameMutation.mutate(formValues)
        }
      }

      if (formValues.institution !== currentUser?.institution) {
        institutionMutation.mutate(formValues)
      }

      if (
        formValues.email !== currentUser?.email &&
        formValues.confirmEmail.length > 0
      ) {
        mailMutation.mutate(formValues)
      }

      if (formValues.password.length > 5) {
        passwordMutation.mutate(formValues)
      }
    }
  }

  // Mutations ###############################################

  const nameMutation = useMutation("updateName", updateName, {
    onSuccess: (data) => {
      queryClient.invalidateQueries("getCurrentUser")
      toast.success(data.message)
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  const usernameMutation = useMutation("updateUsername", updateUsername, {
    onSuccess: (data) => {
      queryClient.invalidateQueries("getCurrentUser")
      toast.success(data.message)
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  const institutionMutation = useMutation(
    "updateInstitution",
    updateInstitution,
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries("getCurrentUser")
        toast.success(data.message)
      },
      onError: (err: any) => {
        toast.error(err.message)
      },
    }
  )

  const mailMutation = useMutation("updateMail", updateMail, {
    onSuccess: (data) => {
      queryClient.invalidateQueries("getCurrentUser")
      toast.success(data.message)
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  const passwordMutation = useMutation("updatePassword", updatePassword, {
    onSuccess: (data) => {
      queryClient.invalidateQueries("getCurrentUser")
      toast.success(data.message)
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  const unlockPasswordMutation = useMutation("unlockPassword", unlockPassword, {
    onSuccess: (data) => {
      togglePasswordLock()
      toast.success(data.message)
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  const updateImgMutation = useMutation("updateImg", updateImg, {
    onSuccess: (data) => {
      queryClient.invalidateQueries("getCurrentUser")
      toast.success(data.message)
    },
    onError: (err: any) => {
      toast.error(err.message)
    },
  })

  // Async function calls ########################################

  async function updateName(credentials: FormValues) {
    try {
      const { name } = credentials

      const response = await client.updateName(name)

      return response.data
    } catch (err: any) {
      throw new Error(err.message)
    }
  }

  async function updateUsername(credentials: FormValues) {
    try {
      const { username } = credentials

      const response = await client.updateUsername(username)

      return response.data
    } catch (err: any) {
      throw err
    }
  }

  async function updateInstitution(credentials: FormValues) {
    try {
      const { institution } = credentials

      const response = await client.updateInstitution(institution)

      return response.data
    } catch (err: any) {
      throw err
    }
  }

  async function updateMail(credentials: FormValues) {
    try {
      const { email } = credentials

      // Calling the API and getting the response
      const response = await client.updateMail(email)

      return response.data
    } catch (err: any) {
      throw err
    }
  }

  async function updatePassword(credentials: FormValues) {
    try {
      const { oldPassword, password } = credentials

      const response = await client.updatePassword(password, oldPassword)

      return response.data
    } catch (err: any) {
      throw err
    }
  }

  async function unlockPassword(credentials: FormValues) {
    try {
      const { oldPassword } = credentials

      const response = await client.authenticatePassword(oldPassword)

      return response.data
    } catch (err: any) {
      throw err
    }
  }

  async function updateImg(img: File) {
    try {
      const response = await client.updateUserImg(img)

      return response.data
    } catch (err: any) {
      throw new Error(err.message)
    }
  }

  // Animations #############################################

  const lockAnim = useSpring({
    left: passwordLocked ? (showUnlockPasswordForm ? 22 : 260) : 22,
    // opacity: showUnlockPasswordForm ? 1 : 1,
    scale: passwordLocked ? (showUnlockPasswordForm ? 1.1 : 1.5) : 1.1,
  })

  const unlockPassInputAnim = useSpring({
    opacity: showUnlockPasswordForm ? 1 : 0,
  })

  const imgIconAnim = useSpring({
    opacity: imgHovered ? 1 : 0,
    config: {
      tension: 1000,
      friction: 80,
    },
  })

  // Colors ##################################################

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'

  return (
    <div
      style={{
        backgroundColor: darkTheme ? "transparent" : "#f8f9fa"
      }}
    >
      {currentUser && (
        <div className="profile-wrap">
          <div className="profile-paper-img">
            <Paper
              radius="md"
              p="xl"
              withBorder
              {...props}
              style={{
                // padding: "0 20px 0 20px",
                width: "340px",
                height: "340px",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <img
                src={currentUser.imgurl ? currentUser.imgurl : darkTheme ? user_img : user_img_light}
                alt="User"
                className="profile-img-user"
                style={{
                  width: "260px",
                  height: "260px",
                  borderRadius: "50%",
                  position: "absolute",
                }}
              />
              <animated.div
                onMouseEnter={() => setImgHovered(true)}
                onMouseLeave={() => setImgHovered(false)}
                onClick={(e) => handleImgClick()}
                style={{
                  position: "absolute",
                  backgroundColor: "#A6A7AB",
                  width: 260,
                  height: 260,
                  borderRadius: "50%",
                  opacity: imgHovered ? 0.55 : 0,
                  cursor: imgHovered ? "pointer" : "default",
                }}
              />
              <animated.div
                children={
                  <RiImageEditLine
                    style={{
                      position: "absolute",
                      width: 80,
                      height: 80,
                      transform: "translate(-50%,-50%)",
                      pointerEvents: "none",
                    }}
                  />
                }
                style={{
                  ...imgIconAnim,
                }}
              />
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                style={{ display: "none" }} // hide the input element
              />
            </Paper>
          </div>
          {/* Main Profile Page  ########################## */}
          <div className="profile-paper-main" >
            <Paper
              radius="md"
              p="xl"
              withBorder
              {...props}
              style={{
                padding: "0 0 0 0px",
              }}
            >
              <div className="profile-header-wrap">
                <h3 className="profile-header-h3">User Profile</h3>
              </div>
              <form
                onSubmit={updateForm.onSubmit(handleSubmit)}
                style={{
                  paddingBottom: 20,
                }}
              >
                {/* Full Name and Username ##########################*/}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    flexDirection: "row",
                  }}
                >
                  <TextInput
                    label="Full Name"
                    placeholder={
                      currentUser.name ? currentUser.name : "Your name"
                    }
                    value={updateForm.values.name}
                    onChange={(event) =>
                      updateForm.setFieldValue(
                        "name",
                        event.currentTarget.value
                      )
                    }
                    radius="md"
                    style={{
                      width: 200,
                      marginBottom: 20,
                      marginRight: 40,
                    }}
                  />
                  <TextInput
                    label="Username"
                    placeholder={currentUser.username}
                    value={updateForm.values.username}
                    onChange={(event) =>
                      updateForm.setFieldValue(
                        "username",
                        event.currentTarget.value
                      )
                    }
                    radius="md"
                    style={{
                      width: 200,
                    }}
                  />
                </div>
                {/* Institution ########################## */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    flexDirection: "row",
                  }}
                >
                  <TextInput
                    label="Institution"
                    placeholder={
                      currentUser.institution
                        ? currentUser.institution
                        : "Your institution"
                    }
                    value={updateForm.values.institution}
                    onChange={(event) =>
                      updateForm.setFieldValue(
                        "institution",
                        event.currentTarget.value
                      )
                    }
                    radius="md"
                    style={{
                      width: 440,
                      marginBottom: 20,
                      marginLeft: 0,
                    }}
                  />
                </div>
                {/* Email and Email Confirmation ########################## */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    flexDirection: "row",
                  }}
                  ref={emailRef}
                >
                  <TextInput
                    label="Email Address"
                    // placeholder={currentUser.email}
                    value={updateForm.values.email}
                    onChange={(event) =>
                      updateForm.setFieldValue(
                        "email",
                        event.currentTarget.value
                      )
                    }
                    error={updateForm.errors.email}
                    radius="md"
                    style={{
                      width: 200,
                      marginBottom: 20,
                      marginRight: 40,
                    }}
                  />
                  <TextInput
                    label="Confirm Email Address"
                    placeholder={currentUser.email}
                    value={updateForm.values.confirmEmail}
                    onChange={(event) =>
                      updateForm.setFieldValue(
                        "confirmEmail",
                        event.currentTarget.value
                      )
                    }
                    error={updateForm.errors.confirmEmail}
                    radius="md"
                    style={{
                      width: 200,
                    }}
                  />
                </div>
                <div style={{ position: "relative", height: 100 }}>
                  {/* Password and Password Confirmation ########################## */}
                  <div
                    style={{
                      position: "relative",
                      display: "flex",
                      justifyContent: "center",
                      flexDirection: "row",
                      filter: passwordLocked ? "blur(1.5px)" : "none",
                    }}
                  >
                    <PasswordInput
                      disabled={passwordLocked}
                      label="New Password"
                      placeholder={"Your new password"}
                      value={updateForm.values.password}
                      onChange={(event) =>
                        updateForm.setFieldValue(
                          "password",
                          event.currentTarget.value
                        )
                      }
                      radius="md"
                      style={{
                        width: 200,
                        marginBottom: 20,
                        marginRight: 40,
                      }}
                      error={updateForm.errors.password}
                    />
                    <PasswordInput
                      disabled={passwordLocked}
                      label="Confirm New Password"
                      placeholder={"Password confirmation"}
                      value={updateForm.values.confirmPassword}
                      onChange={(event) =>
                        updateForm.setFieldValue(
                          "confirmPassword",
                          event.currentTarget.value
                        )
                      }
                      error={updateForm.errors.confirmPassword}
                      radius="md"
                      style={{
                        width: 200,
                      }}
                    />
                  </div>
                  {/* PW Overlay begin ########################## */}
                  {passwordLocked && (
                    <div
                      className="profile-pw-overlay"
                      style={{
                        // transform: "translate(-50%,-100px)",
                        position: "absolute",
                      }}
                    >
                      {/* PW Overlay Background ########################## */}
                      <div
                        className="profile-pw-background"
                        style={{
                          width: 500,
                          height: 100,
                          left: 10,
                          position: "absolute",
                          backgroundColor: darkTheme ? "#1a1b1e" : "#fff",
                          opacity: showUnlockPasswordForm ? 1 : 0.5,
                        }}
                      />

                      {/* PW Unlock form ########################## */}
                      {showUnlockPasswordForm && (
                        <animated.div
                          style={{
                            position: "relative",
                            width: 440,
                            height: 100,
                            top: 0,
                            ...unlockPassInputAnim,
                          }}
                        >
                          <TextInput
                            autoFocus
                            type="password"
                            label="Current Password"
                            placeholder="Your password"
                            disabled={!showUnlockPasswordForm}
                            value={updateForm.values.oldPassword}
                            onChange={(event) =>
                              updateForm.setFieldValue(
                                "oldPassword",
                                event.currentTarget.value
                              )
                            }
                            radius="md"
                            style={{
                              position: "absolute",
                              top: 0,
                              width: 440,
                            }}
                          />
                          <button type="submit" style={{ display: "none" }} />
                        </animated.div>
                      )}
                    </div>
                  )}{" "}
                  {/* PW Overlay end */}
                  {/* PW Lock button   */}
                  <animated.div
                    style={{
                      position: "absolute",
                      transform: "translate(-50%,-50px)",
                      ...lockAnim,
                    }}
                  >
                    <button
                      onMouseEnter={() => setLockHovered(true)}
                      onMouseLeave={() => setLockHovered(false)}
                      onClick={toggleUnlockPasswordForm}
                      type="button"
                      style={{ background: "none", border: "none" }}
                    >
                      {passwordLocked ? (
                        lockHovered ? (
                          <PiLockOpen color="#c1c2c5" />
                        ) : (
                          <PiLock color="#c1c2c5" />
                        )
                      ) : lockHovered ? (
                        <PiLock color="#c1c2c5" />
                      ) : (
                        <PiLockOpen color="#c1c2c5" />
                      )}
                    </button>
                  </animated.div>
                </div>{" "}
                {/* Password end */}
                {/* Confirmation button ########################## */}
                <div
                  style={{
                    marginTop: 20,
                    marginRight: 40,
                    marginBottom: 15,
                    position: "relative",
                    display: "flex",
                    justifyContent: "right",
                  }}
                >
                  <Button type="submit" radius="xl">
                    Confirm changes
                  </Button>
                </div>
              </form>
            </Paper>
          </div>
        </div>
      )}
    </div>
  )
}
