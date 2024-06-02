package request

type ContainerRequest struct {
	ContainerID string
}

type ContainerCreateRequest struct {
	ContainerName     string
	ContainerRam      int
	ContainerCore     int
	ContainerPassword string
}

type ContainerUpdateRequest struct {
	ContainerID string
	NewRam      int
}
