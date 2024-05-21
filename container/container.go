package main

import (
	"context"
	"net/http"

	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/client"
	"github.com/docker/go-connections/nat"
	"github.com/gin-gonic/gin"
	v1 "github.com/opencontainers/image-spec/specs-go/v1"
)

func createContainer(contaner_name string) (string, error) {
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
			},
			Tty: true,
			//Cmd: []string{"bash", "-c", "dnf install -y openssh-server && systemctl enable sshd && systemctl start sshd"},
		},
		&container.HostConfig{
			PortBindings: portBinding,
		},
		&network.NetworkingConfig{},
		&v1.Platform{},
		contaner_name,
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

func main() {
	//createContainer("hello")
	//createContainer("test")
	//pauseContainer("1ea1b9587837")
	//stopContainer("1ea1b9587837")
	//startContainer("1ea1b9587837")
	//unpauseContainer("1ea1b9587837")
	r := gin.Default()
	r.GET("/ping", func(ctx *gin.Context) {
		ctx.JSON(http.StatusOK, gin.H{
			"message": "pong",
		})
	})

	r.POST("/container/create", func(ctx *gin.Context) {
		container_name := ctx.Query("container_name")
		id, err := createContainer(container_name)

		if err != nil {
			panic(err)
		}

		ctx.JSON(
			http.StatusOK,
			gin.H{
				"container_Id": id,
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
