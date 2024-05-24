package models

import "gorm.io/gorm"

type Container struct {
	gorm.Model
	ContainerID string `gorm:"unique"`
	UserID      string
	UserToken   string
}
