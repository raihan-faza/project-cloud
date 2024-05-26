package models

import "gorm.io/gorm"

type Container struct {
	gorm.Model
	ContainerID      string `gorm:"unique"`
	ContainerName    string
	ContainerStorage int
	ContainerRam     int
	ContainerCore    int
	UserID           int
	UserToken        string
}
