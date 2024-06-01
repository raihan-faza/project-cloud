package request

type ContainerRequest struct {
	ContainerID string
}

type ContainerListRequest struct {
	UserID int
}

type ContainerCreateRequest struct {
	ContainerName string
	ContainerRam  int
	ContainerCore int
	UserID        int
}

type ContainerUpdateRequest struct {
	ContainerID string
	NewRam      int
}
