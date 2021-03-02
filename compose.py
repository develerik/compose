#!/usr/bin/env python3

import argparse
import os
from subprocess import run
from os.path import exists
from os import listdir


class Compose(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='docker-compose wrapper for easy management')
        parser.version = '0.1.0'
        parser.add_argument('stack', type=str, help='docker stack to manage')
        parser.add_argument('--src', metavar='path', type=str, default='~/.docker/definitions',
                            help='stack definitions folder')
        parser.add_argument('--version', action='version')
        parser.add_argument('commands', nargs=argparse.REMAINDER, help='docker-compose commands')
        args = parser.parse_args()
        definitions_path = os.path.expanduser(args.src)

        if args.stack == "ps":
            states = self.get_stack_states(definitions_path)
            states.insert(0, {"name": "Name", "command": "Command", "state": "State", "ports": "Ports"})
            reserved_name = len(max(states, key=lambda s: len(s["name"]))["name"]) + 1
            reserved_command = len(max(states, key=lambda s: len(s["command"]))["command"]) + 1
            reserved_state = len(max(states, key=lambda s: len(s["state"]))["state"]) + 1
            row_format = f'{{0:<{reserved_name}}} {{1:<{reserved_command}}} {{2:<{reserved_state}}} {{3:<}}'
            for state in states:
                print(row_format.format(state["name"], state["command"], state["state"], state["ports"]))
            exit(0)

        if args.stack == "ls":
            stacks = self.get_stacks(definitions_path)
            stacks.insert(0, {"name": "Name", "path": "Path"})
            reserved = len(max(stacks, key=lambda s: len(s["name"]))["name"]) + 1
            row_format = f'{{0:<{reserved}}} {{1:<}}'
            for stack in stacks:
                print(row_format.format(stack["name"], stack["path"]))
            exit(0)

        file_path = f'{definitions_path}/{args.stack}.yml'

        if not self.is_stack_existing(file_path):
            print("stack not found")
            exit(1)

        self.run_docker_compose(file_path, args.stack, args.commands)

    def get_stack_states(self, definitions_path):
        stacks = self.get_stacks(definitions_path)
        results = []

        for stack in stacks:
            result = self.run_docker_compose(stack["path"], stack["name"], ["ps", "--all"], True)
            result_lines = result.stdout.decode().split('\n')
            result_lines = list(filter(None, result_lines))[2:]
            for line in result_lines:
                details = list(filter(None, line.split('   ')))
                if details[3] == '  ':
                    details[3] = '-'
                results.append({
                    "name": details[0],
                    "command": details[1],
                    "state": details[2],
                    "ports": details[3],
                })
        return results

    @staticmethod
    def get_stacks(definitions_path):
        stacks = []
        definitions = listdir(definitions_path)

        for definition in definitions:
            stack_name = definition.split(".")[0]
            stack_path = f'{definitions_path}/{definition}'
            stacks.append({"name": stack_name, "path": stack_path})

        return stacks

    @staticmethod
    def is_stack_existing(definition_path):
        return exists(definition_path)

    @staticmethod
    def run_docker_compose(definition_path, stack, commands, capture=False):
        try:
            args = ["-f", definition_path, "-p", stack, *commands]
            return run(["docker-compose", *args], capture_output=capture)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    Compose()
