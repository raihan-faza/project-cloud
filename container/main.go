package main

import (
	"api/cloud/initializers"
	"api/cloud/models"
	"context"
	"net/http"
	"strconv"

	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/client"
	"github.com/docker/go-connections/nat"
	"github.com/gin-gonic/gin"
	v1 "github.com/opencontainers/image-spec/specs-go/v1"
)

func createContainer(container_name string, container_ram int, container_core int, container_storage int) (string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		panic(err)
	}

	hostBinding := nat.PortBinding{HostIP: "0.0.0.0", HostPort: "5000"}
	containerPort, err := nat.NewPort("tcp", "80")
	if err != nil {
		panic(err)
	}

	portBinding := nat.PortMap{containerPort: []nat.PortBinding{hostBinding}}

	cont, err := cli.ContainerCreate(context.Background(),
		&container.Config{
			Image: "fedora:latest",
			ExposedPorts: nat.PortSet{
				nat.Port("80"): {},
				"22/tcp":       struct{}{},
			},
			Tty: true,
			//Cmd: []string{"bash", "-c", "dnf install -y openssh-server && systemctl enable sshd && systemctl start sshd"},
		},
		&container.HostConfig{
			PortBindings: portBinding,
			Resources: container.Resources{
				NanoCPUs: int64(container_core) * 1e9,
				Memory:   int64(container_ram) * 1024 * 1024 * 1024,
			},
			StorageOpt: map[string]string{
				"size": strconv.Itoa(container_storage) + "G",
			},
		},
		&network.NetworkingConfig{},
		&v1.Platform{},
		container_name,
	)

	if err != nil {
		panic(err)
	}

	cli.ContainerStart(context.Background(), cont.ID, container.StartOptions{})

	return cont.ID, nil
}

func startContainer(cont_id string) string {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		panic(err)
	}

	cli.ContainerStart(context.Background(), cont_id, container.StartOptions{})

	return "container started"
}

func pauseContainer(cont_id string) string {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		panic(err)
	}

	cli.ContainerPause(context.Background(), cont_id)
	return "container paused"
}

func unpauseContainer(cont_id string) string {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		panic(err)
	}

	cli.ContainerUnpause(context.Background(), cont_id)
	return "container unpaused"
}

func stopContainer(cont_id string) string {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		panic(err)
	}

	cli.ContainerStop(context.Background(), cont_id, container.StopOptions{})
	return "container stopped"
}

func init() {
	initializers.ConnectDatabase()
	initializers.LoadEnv()
}

func main() {
	//createContainer("hello")
	//createContainer("test")
	//pauseContainer("1ea1b9587837")
	//stopContainer("1ea1b9587837")
	//startContainer("1ea1b9587837")
	//unpauseContainer("1ea1b9587837")

	r := gin.Default()

	r.POST("/container/create", func(ctx *gin.Context) {
		container_name := "hello"
		container_ram := 2
		container_core := 1
		container_storage := 10
		user_id := ctx.Query("user_id")
		user_token := ctx.Query("user_token")

		id, err := createContainer(container_name, container_ram, container_core, container_storage)

		if err != nil {
			panic(err)
		}

		containerData := models.Container{ContainerID: id, UserID: user_id, UserToken: user_token}
		initializers.DB.Create(&containerData)

		ctx.JSON(
			http.StatusOK,
			gin.H{
				"container_Id": containerData.ContainerID,
			},
		)
	})

	r.POST("/container/start", func(ctx *gin.Context) {
		container_id := ctx.Query("container_id")
		startContainer(container_id)
	})

	r.POST("/container/pause", func(ctx *gin.Context) {
		container_id := ctx.Query("container_id")
		pauseContainer(container_id)
	})

	r.POST("/container/unpause", func(ctx *gin.Context) {
		container_id := ctx.Query("container_id")
		unpauseContainer(container_id)
	})

	r.POST("/container/stop", func(ctx *gin.Context) {
		container_id := ctx.Query("container_id")
		stopContainer(container_id)
	})

	r.Run()
}
