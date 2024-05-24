package models

import "gorm.io/gorm"

type ContainerDetails struct {
	gorm.Model
	ContainerID           string `gorm:"constraint:OnDelete:CASCADE,OnUpdate:CASCADE;foreignKey:UserID"`
	ContainerStorage      int
	ContainerRam          int
	ContainerCore         int
	ContainerUptime       int
	ContainerBilling      int
	ContainerTotalBilling int
	Container             Container
}
