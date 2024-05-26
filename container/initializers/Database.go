package initializers

import (
	"api/cloud/models"
	"fmt"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func init() {
	LoadEnv()
}

func ConnectDatabase() (*gorm.DB, error) {
	dsn := fmt.Sprintf("host=localhost user=%s password=%s dbname=%s port=%s sslmode=disable", os.Getenv("DB_USER"), os.Getenv("DB_PASSWORD"), os.Getenv("DB_NAME"), os.Getenv("DB_PORT"))
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// migration
	err = AutoMigrate(db, &models.Container{}, &models.ContainerDetails{})
	if err != nil {
		return nil, err
	}
	return db, nil
}

func AutoMigrate(db *gorm.DB, models ...interface{}) error {
	for _, model := range models {
		if err := db.AutoMigrate(model); err != nil {
			return err
		}
	}
	return nil
}
