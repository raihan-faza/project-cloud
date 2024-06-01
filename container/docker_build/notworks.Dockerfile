# Use the official Ubuntu 20.04 as a base image
FROM ubuntu:20.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install OpenSSH server
RUN apt-get update && \
    apt-get install -y openssh-server && \
    apt-get clean

# Create the necessary directory for the SSH daemon
RUN mkdir /var/run/sshd

# Starting ssh
RUN service ssh start

# Enable root login with password (not recommended for production)
RUN echo 'root:root' | chpasswd

# Allow SSH root login by modifying the sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed -i 's@session    required     pam_loginuid.so@session    optional     pam_loginuid.so@g' /etc/pam.d/sshd

# Expose port 22 for SSH
EXPOSE 22

# Start the SSH service and open a bash shell
CMD ["/bin/bash"]

