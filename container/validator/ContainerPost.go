package validator

import "strings"

func ValidateName(container_name string) bool {
	blacklist := []string{";", "|", "&", "`", "&&", "||"}
	for _, item := range blacklist {
		if strings.Contains(container_name, item) {
			return false
		}
	}

	return true
}
