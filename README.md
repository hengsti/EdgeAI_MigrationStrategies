## Prerequisites

Installed Docker Demon or Podman Machine

## Startup Container with VS Code Dev Container

To run Dev Containers in VS Code the following extension needs to be installed in VS Code: [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Open Folder and build the Dev Container from `devcontainer.json` with the command in the VS Code Search bar:

```
>Dev Containers: Rebuild Container without Cache
```

## Startup Container with Docker

**Build:**

```shell
docker build -t p2-migration .
```

**Run:**

```shell
docker run --rm -it --name p2-migration p2-migration /bin/bash
```