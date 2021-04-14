#!/usr/bin/env python3

"""docker-compose wrapper for easy management"""

import argparse
import os

from subprocess import run
from typing import Final


VERSION: Final = "0.3.0"


def parse_arguments():
    """Parses command line arguments.

    :return: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="'docker compose' wrapper for easy management")
    parser.version = VERSION
    parser.add_argument("--src", type=str, default="~/.docker/definitions", help="stack definitions source path")
    parser.add_argument("--version", action="version")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--create", action="store_true", help="create a new stack")
    group.add_argument("--delete", action="store_true", help="delete the stack")
    group.add_argument("--edit", action="store_true", help="edit the stack")
    group.add_argument("--spec", action="store_true", help="show the stack definition")

    parser.add_argument("stack", type=str, help="docker stack to manage")
    parser.add_argument("commands", nargs=argparse.REMAINDER, help="'docker compose' commands")

    parsed_args = parser.parse_args()

    if os.environ.get("COMPOSE_SRC"):
        parsed_args.src = os.environ.get("COMPOSE_SRC")

    parsed_args.src = os.path.expanduser(parsed_args.src)

    return parsed_args


def get_stack_path(path: str, name: str):
    """Get path of a stack inside the path.

    :param path: The path to search the stack in.
    :param name: The name of the stack to search for.
    :return: The full path of the stack.
    """
    spec_path = os.sep.join([path, name])

    for ext in {"yml", "yaml"}:
        path = ".".join([spec_path, ext])
        if os.path.exists(path):
            return path

    raise FileNotFoundError(spec_path)


def show_stack_spec(path: str):
    """Prints the stack definition to stdout.

    :param path: The path of the stack to print.
    """
    with open(path, 'r') as fin:
        print(fin.read())


def create_stack(path: str, name: str):
    """Creates a new stack with the given name at the given path.

    :param path: The path to create the stack at.
    :param name: The name of the stack to create.
    """
    try:
        create_path = get_stack_path(path, name)
        raise FileExistsError(create_path)
    except FileNotFoundError:
        create_path = ".".join([os.sep.join([path, name]), "yml"])
        f = open(create_path, "a")
        f.writelines(f"{line}{os.linesep}" for line in [
            "version: \"3.8\"",
            "",
            "services:",
            f"  {name}:",
            "    image: \"alpine:latest\""
        ])
        f.close()


def edit_stack(path: str):
    """Open the given stack in the default editor.

    :param path: The path of the stack to edit.
    """
    if os.name == 'nt':
        os.system(path)
    else:
        os.system('%s %s' % (os.getenv('EDITOR'), path))


def delete_stack(path: str):
    """Deletes the stack at the given path.

    :param path: The path of the stack to delete.
    """
    os.remove(path)


def run_docker_compose(path: str, name: str, commands):
    """Run docker-compose commands for a given stack

    :param path: The full path of the stack definition.
    :param name: The display name of the stack.
    :param commands: The commands to run.
    """
    docker_args = ["-f", path, "-p", name, *commands]
    run(["docker", "compose", *docker_args])


if __name__ == "__main__":
    try:
        args = parse_arguments()

        if args.create:
            create_stack(args.src, args.stack)
            print("Stack created!")
            exit(0)

        stack_path = get_stack_path(args.src, args.stack)

        if args.spec:
            show_stack_spec(stack_path)
            exit(0)

        if args.delete:
            delete_stack(stack_path)
            print("Stack deleted!")
            exit(0)

        if args.edit:
            edit_stack(stack_path)
            exit(0)

        run_docker_compose(stack_path, args.stack, args.commands)
    except KeyboardInterrupt:
        exit(0)
    except FileNotFoundError as err:
        print("Stack not found: {0}".format(err))
        exit(1)
    except FileExistsError as err:
        print("Stack already exists: {0}".format(err))
        exit(1)
