package request

type ContainerRequest struct {
	ContainerID string
}

type ContainerListRequest struct {
	UserID int
}

type ContainerCreateRequest struct {
	ContainerName    string
	ContainerStorage int
	ContainerRam     int
	ContainerCore    int
	UserID           int
	UserToken        string
}

type ContainerUpdateRequest struct {
	ContainerID string
	NewRam      int
}
