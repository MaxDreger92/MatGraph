export default interface IUser {
  id: number
  name?: string | undefined
  email: string
  password: string
  roles?: Array<string> | undefined
  image?: string | undefined
}
