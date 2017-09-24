import docker


client = docker.from_env()
labels = {'org.elsys-bg.grader': 'True'}
tag_prefix = 'elsysbg.org/grader/'


def docker_image_build(tag, dockerfile, context):
    tag = tag_prefix + tag

    client.images.build(
        path=context,
        tag=tag,
        rm=True,
        pull=True,
        forcerm=True,
        dockerfile=dockerfile,
        labels=labels)

    return tag


def docker_container_create(**kwargs):
    if 'labels' in kwargs:
        kwargs['labels'].update(labels)
    else:
        kwargs['labels'] = labels

    return client.images.create(**kwargs)


class DockerRunner:
    def stop(self):
        try:
            self.container.kill()
        except docker.errors.NotFound:
            pass

    def __enter__(self):
        self.container.start()
        self.container = client.containers.get(self.container.id)
        assert self.container.status == 'running'

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
