package models

import "gorm.io/gorm"

type ContainerDetails struct {
	gorm.Model
	ContainerID      string `gorm:"constraint:OnDelete:CASCADE,OnUpdate:CASCADE;foreignKey:UserID"`
	ContainerUptime  int
	ContainerBilling int
	Container        Container
}
