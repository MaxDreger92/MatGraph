import { Group, Text, useMantineTheme, rem } from "@mantine/core"
import { IconUpload, IconPhoto, IconX, IconFileTypeCsv } from "@tabler/icons-react"
import { Dropzone, DropzoneProps, FileWithPath, IMAGE_MIME_TYPE } from "@mantine/dropzone"

interface WorkspaceTableDropzoneProps {
  handleFileSelect: (file: File) => void
}

export default function WorkspaceTableDropzone(
  props: WorkspaceTableDropzoneProps
) {
  const { handleFileSelect } = props

  const theme = useMantineTheme()

  const handleFileSelectLocal = (files: FileWithPath[]) => {
    handleFileSelect(files[0])
  }

  return (
    <div
      className="workspace-table-dropzone"
      style={{
        position: "relative",
        width: "40%",
        top: "50%",
        left: "50%",
        transform: "translate(-50%,-50%)"
      }}
    >
      <Dropzone
        onDrop={(files) => handleFileSelectLocal(files)}
        maxSize={1 * 1024 ** 2}
        maxFiles={1}
        accept={{
          'text/csv': ['.csv'] 
        }}
      >
        <Group
          position="center"
          spacing="xl"
          style={{ minHeight: 200, pointerEvents: "none" }}
        >
          <Dropzone.Accept>
            <IconUpload
              size="3.2rem"
              stroke={1.5}
              color={
                theme.colors[theme.primaryColor][
                  theme.colorScheme === "dark" ? 4 : 6
                ]
              }
            />
          </Dropzone.Accept>
          <Dropzone.Reject>
            <IconX
              size="3.2rem"
              stroke={1.5}
              color={theme.colors.red[theme.colorScheme === "dark" ? 4 : 6]}
            />
          </Dropzone.Reject>
          <Dropzone.Idle>
            <IconFileTypeCsv size="3.2rem" stroke={1.5} />
          </Dropzone.Idle>

          <div>
            <Text size="xl" inline>
              Drag here or click to select file
            </Text>
            {/* <Text size="sm" color="dimmed" inline mt={7}>
              Attach as many files as you like, each file should not exceed 5mb
            </Text> */}
          </div>
        </Group>
      </Dropzone>
    </div>
  )
}
