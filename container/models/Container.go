package models

import "gorm.io/gorm"

type Container struct {
	gorm.Model
	ContainerID   string `gorm:"unique"`
	ContainerName string
	ContainerRam  int
	ContainerCore int
	UserID        string
	ContainerPort string
	IsPaused      bool
	IsStopped     bool
}
