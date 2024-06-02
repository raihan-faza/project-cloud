package main

import (
	"api/cloud/initializers"
	"api/cloud/middleware"
	"api/cloud/models"
	"api/cloud/request"
	"context"
	"fmt"
	"net"
	"net/http"
	"strings"

	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/client"
	"github.com/docker/go-connections/nat"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
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
			Image: "ubuntu-ssh:latest",
			ExposedPorts: nat.PortSet{
				"22/tcp": struct{}{},
			},
			Tty: true,
			//Cmd: []string{"bash", "-c", "dnf install -y openssh-server && systemctl enable sshd && systemctl start sshd"},
			//Cmd: []string{"sh", "-c", "dnf install -y openssh-server && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && echo 'root:password' | chpasswd && systemctl enable sshd && systemctl start sshd"},
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
	/*
		execConfig := types.ExecConfig{
			Cmd:          []string{"bash", "-c", "echo 'root:password' | chpasswd"},
			AttachStdout: true,
			AttachStderr: true,
			Tty:          true,
		}

		execStartCheck := types.ExecStartCheck{}
		execID, err := cli.ContainerExecCreate(context.Background(), cont.ID, execConfig)
		if err != nil {
			log.Fatal(err)
		}

		if err := cli.ContainerExecStart(context.Background(), execID.ID, execStartCheck); err != nil {
			log.Fatal(err)
		}
	*/
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

func updateContainer(cont_id string, new_container_ram int) (string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return "", err
	}

	cli.ContainerUpdate(context.Background(), cont_id, container.UpdateConfig{
		Resources: container.Resources{
			Memory: int64(new_container_ram) * 1024 * 1024,
		},
	})

	message := fmt.Sprintf("container with id %s has been updated", cont_id)
	return message, err
}

func deleteContainer(cont_id string) (string, error) {
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return "", err
	}
	cli.ContainerRemove(context.Background(), cont_id, container.RemoveOptions{
		Force: true,
	})

	return "container has been deleted", err
}

func init() {
	initializers.LoadEnv()
}

func main() {
	r := gin.Default()
	db, _ := initializers.ConnectDatabase()

	r.POST("/container/create", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var request request.ContainerCreateRequest
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := int(claims["uuid"].(float64))
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
			ContainerID:   container_id,
			ContainerName: request.ContainerName,
			ContainerRam:  request.ContainerRam,
			ContainerCore: request.ContainerCore,
			UserID:        user_id,
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
				"container_Id":   container_id,
				"container_name": request.ContainerName,
				"ssh_port":       hostPort,
			},
		)
	})

	r.POST("/container/start", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var request request.ContainerRequest
		var container models.Container
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := int(claims["uuid"].(float64))
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
		container_query := db.First(&container, request.ContainerID)
		if container_query != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to query container",
				},
			)
			return
		}
		if container.UserID != user_id {
			ctx.JSON(
				http.StatusUnauthorized,
				gin.H{
					"message": "youre not authorized to access this container",
				},
			)
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

	r.POST("/container/pause", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var request request.ContainerRequest
		var container models.Container
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := int(claims["uuid"].(float64))
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
		container_query := db.First(&container, request.ContainerID)
		if container_query != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to query container",
				},
			)
			return
		}
		if container.UserID != user_id {
			ctx.JSON(
				http.StatusUnauthorized,
				gin.H{
					"message": "youre not authorized to access this container",
				},
			)
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

	r.POST("/container/unpause", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var request request.ContainerRequest
		var container models.Container
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := int(claims["uuid"].(float64))
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
		container_query := db.First(&container, request.ContainerID)
		if container_query != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to query container",
				},
			)
			return
		}
		if container.UserID != user_id {
			ctx.JSON(
				http.StatusUnauthorized,
				gin.H{
					"message": "youre not authorized to access this container",
				},
			)
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

	r.POST("/container/stop", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var request request.ContainerRequest
		var container models.Container
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := int(claims["uuid"].(float64))
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
		container_query := db.First(&container, request.ContainerID)
		if container_query != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to query container",
				},
			)
			return
		}
		if container.UserID != user_id {
			ctx.JSON(
				http.StatusUnauthorized,
				gin.H{
					"message": "youre not authorized to access this container",
				},
			)
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

	r.GET("/container/list", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var containers []models.Container
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := claims["uuid"]
		data := db.Where("user_id= ?", user_id).Find(&containers)
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

	r.POST("container/update", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var request request.ContainerUpdateRequest
		var container models.Container
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := int(claims["uuid"].(float64))
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
		container_query := db.First(&container, request.ContainerID)
		if container_query != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to query container",
				},
			)
			return
		}
		if container.UserID != user_id {
			ctx.JSON(
				http.StatusUnauthorized,
				gin.H{
					"message": "youre not authorized to access this container",
				},
			)
		}
		message, err := updateContainer(request.ContainerID, request.NewRam)
		if err != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "Failed to update container",
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

	r.POST("/container/delete", middleware.JWTMiddleware(), func(ctx *gin.Context) {
		var request request.ContainerRequest
		var container models.Container
		claims := ctx.MustGet("claims").(jwt.MapClaims)
		user_id := claims["uuid"]
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
		container_query := db.First(&container, request.ContainerID)
		if container_query != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "failed to query container",
				},
			)
			return
		}
		if container.UserID != user_id {
			ctx.JSON(
				http.StatusUnauthorized,
				gin.H{
					"message": "youre not authorized to access this container",
				},
			)
		}
		message, err := deleteContainer(request.ContainerID)
		if err != nil {
			ctx.JSON(
				http.StatusNotFound,
				gin.H{
					"message": "Failed to delete container",
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
	r.Run()
}
