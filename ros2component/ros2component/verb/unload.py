# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy

from ros2cli.node import NODE_NAME_PREFIX
from ros2cli.node.direct import DirectNode
from ros2cli.node.strategy import add_arguments
from ros2cli.node.strategy import NodeStrategy

from ros2component.api import container_node_name_completer
from ros2component.api import find_container_node_names
from ros2component.api import unload_component_from_container
from ros2component.verb import VerbExtension

from ros2node.api import get_node_names


class UnloadVerb(VerbExtension):
    """Unload a component from a container node."""

    def add_arguments(self, parser, cli_name):
        add_arguments(parser)
        argument = parser.add_argument(
            'container_node_name', help='Container node name to unload component from'
        )
        argument.completer = container_node_name_completer
        argument = parser.add_argument(
            'component_uid', type=int, nargs='+', help='Unique ID of the component to be unloaded'
        )

    def main(self, *, args):
        with NodeStrategy(args) as node:
            node_names = get_node_names(node=node)
        with DirectNode(args) as node:
            container_node_names = find_container_node_names(node=node, node_names=node_names)
        rclpy.init()
        node = rclpy.create_node(NODE_NAME_PREFIX + '_component_load_requester')
        if args.container_node_name in [n.full_name for n in container_node_names]:
            return unload_component_from_container(
                node=node, remote_container_node_name=args.container_node_name,
                component_uids=args.component_uid
            )
        else:
            return "Unable to find container node '" + args.container_node_name + "'"
