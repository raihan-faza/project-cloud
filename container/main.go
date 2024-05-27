package main

import (
	"api/cloud/initializers"
	"api/cloud/models"
	"api/cloud/request"
	"context"
	"net"
	"net/http"
	"strings"

	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/client"
	"github.com/docker/go-connections/nat"
	"github.com/gin-gonic/gin"
	v1 "github.com/opencontainers/image-spec/specs-go/v1"
)

func findAvailablePort() (string, error) {
	listener, err := net.Listen("tcp", "localhost:0")
	if err != nil {
		return "", err
	}
	defer listener.Close()

	address := listener.Addr().String()
	parts := strings.Split(address, ":")
	return parts[len(parts)-1], nil
}

func createContainer(container_name string, container_ram int, container_core int) (string, string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return "", "", err
	}

	hostPort, err := findAvailablePort()
	if err != nil {
		return "", "", err
	}

	hostBinding := nat.PortBinding{HostIP: "0.0.0.0", HostPort: hostPort}
	containerPort, err := nat.NewPort("tcp", "22")
	if err != nil {
		return "", "", err
	}

	portBinding := nat.PortMap{containerPort: []nat.PortBinding{hostBinding}}

	cont, err := cli.ContainerCreate(context.Background(),
		&container.Config{
			Image: "fedora:latest",
			ExposedPorts: nat.PortSet{
				"22/tcp": struct{}{},
			},
			Tty: true,
			//Cmd: []string{"bash", "-c", "dnf install -y openssh-server && systemctl enable sshd && systemctl start sshd"},
			Cmd: []string{"sh", "-c", "dnf install -y openssh-server && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && echo 'root:password' | chpasswd && systemctl enable sshd && systemctl start sshd"},
		},
		&container.HostConfig{
			PortBindings: portBinding,
			Resources: container.Resources{
				NanoCPUs: int64(container_core) * 1e9,
				Memory:   int64(container_ram) * 1024 * 1024,
			},
			//StorageOpt: map[string]string{
			//	"size": strconv.Itoa(container_storage) + "G",
			//},
		},
		&network.NetworkingConfig{},
		&v1.Platform{},
		container_name,
	)

	if err != nil {
		return "", "", err
	}

	cli.ContainerStart(context.Background(), cont.ID, container.StartOptions{})

	return cont.ID, hostPort, err
}

func startContainer(cont_id string) (string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return "", err
	}

	cli.ContainerStart(context.Background(), cont_id, container.StartOptions{})

	return "container started", nil
}

func pauseContainer(cont_id string) (string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return "", err
	}

	cli.ContainerPause(context.Background(), cont_id)
	return "container paused", nil
}

func unpauseContainer(cont_id string) (string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return "", err
	}

	cli.ContainerUnpause(context.Background(), cont_id)
	return "container unpaused", nil
}

func stopContainer(cont_id string) (string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return "", err
	}

	cli.ContainerStop(context.Background(), cont_id, container.StopOptions{})
	return "container stopped", nil
}

func init() {
	initializers.LoadEnv()
}

func main() {
	r := gin.Default()

	db, _ := initializers.ConnectDatabase()

	r.POST("/container/create", func(ctx *gin.Context) {
		var request request.ContainerCreateRequest
		err := ctx.BindJSON(&request)
		if err != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "bad request",
				},
			)
			return
		}

		container_id, hostPort, err := createContainer(request.ContainerName, request.ContainerRam, request.ContainerCore)
		if err != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "failed to create container",
				},
			)
			return
		}
		containerData := models.Container{
			ContainerID:      container_id,
			ContainerName:    request.ContainerName,
			ContainerStorage: request.ContainerStorage,
			ContainerRam:     request.ContainerRam,
			ContainerCore:    request.ContainerCore,
			UserID:           request.UserID,
			UserToken:        request.UserToken,
		}
		cont := db.Create(&containerData)
		if cont.Error != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "failed to save container data",
				},
			)
			return
		}

		ctx.JSON(
			http.StatusOK,
			gin.H{
				"container_Id": container_id,
				"ssh_port":     hostPort,
			},
		)
	})

	r.POST("/container/start", func(ctx *gin.Context) {
		var request request.ContainerRequest
		err := ctx.BindJSON(&request)
		if err != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "bad request",
				},
			)
			return
		}
		message, err := startContainer(request.ContainerID)
		if err != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to start container",
				},
			)
			return
		}
		ctx.JSON(
			http.StatusOK,
			gin.H{
				"message": message,
			},
		)
	})

	r.POST("/container/pause", func(ctx *gin.Context) {
		var request request.ContainerRequest
		err := ctx.BindJSON(&request)
		if err != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "request error",
				},
			)
			return
		}
		message, err := pauseContainer(request.ContainerID)
		if err != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to pause container",
				},
			)
			return
		}
		ctx.JSON(
			http.StatusOK,
			gin.H{
				"message": message,
			},
		)

	})

	r.POST("/container/unpause", func(ctx *gin.Context) {
		var request request.ContainerRequest
		err := ctx.BindJSON(&request)
		if err != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "request error",
				},
			)
			return
		}
		message, err := unpauseContainer(request.ContainerID)
		if err != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to unpause container",
				},
			)
			return
		}
		ctx.JSON(
			http.StatusOK,
			gin.H{
				"message": message,
			},
		)

	})

	r.POST("/container/stop", func(ctx *gin.Context) {
		var request request.ContainerRequest
		err := ctx.BindJSON(&request)
		if err != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "request error",
				},
			)
			return
		}
		message, err := stopContainer(request.ContainerID)
		if err != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to stop container",
				},
			)
			return
		}
		ctx.JSON(
			http.StatusOK,
			gin.H{
				"message": message,
			},
		)
	})

	r.POST("/container/list", func(ctx *gin.Context) {
		var request request.ContainerListRequest
		var containers []models.Container
		err := ctx.BindJSON(&request)
		if err != nil {
			ctx.JSON(
				http.StatusBadRequest,
				gin.H{
					"message": "request error",
				},
			)
			return
		}
		data := db.Where("container_id= ?", request.UserID).Find(containers)
		if data.Error != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "data not found",
				},
			)
			return
		}
		ctx.JSON(
			http.StatusOK,
			gin.H{
				"data": containers,
			},
		)
	})
	r.Run()
}
