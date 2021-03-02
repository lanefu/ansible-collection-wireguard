#!/usr/bin/python

# Copyright: (c) 2020, Your Name <YourName@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: wg_facts

short_description: This is my test facts module

version_added: "1.0.0"

description: This is my longer description explaining my test facts module.

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
- name: Return ansible_facts
  my_namespace.my_collection.wg_facts:
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
ansible_facts:
  description: Facts to add to ansible_facts.
  returned: always
  type: dict
  contains:
    foo:
      description: Foo facts about operating system.
      type: str
      returned: when operating system foo fact is present
      sample: 'bar'
    answer:
      description:
      - Answer facts about operating system.
      - This description can be a list as well.
      type: str
      returned: when operating system answer fact is present
      sample: '42'
'''

from ansible.module_utils.basic import AnsibleModule
import configparser
import re

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
      interface = dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        ansible_facts=dict(),
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do
    #rc, out, err = module.run_command(['wg', 'showconf', '%s'.format(module.params['interface'])])
    rc, out, err = module.run_command(['wg', 'showconf', module.params['interface']])
    if rc != 0 or err:
        raise Exception("Unable to show wireguard interface config rc=%s : %s" % (rc, err))
    config = configparser.ConfigParser(allow_no_value=True)
    preparsed = re.sub(r'\[(Peer)\]\n(PublicKey = )(.*)', r'[\g<3>]', out, re.MULTILINE)
    config.read_string(preparsed)
    result['ansible_facts'][module.params['interface']] = dict()
    result['ansible_facts'][module.params['interface']]['interface'] = dict()
    result['ansible_facts'][module.params['interface']]['peers'] = dict()
    for section in config.sections():

        if re.match(r'interface', section, re.IGNORECASE):
            for k, v in config.items(section):
                result['ansible_facts'][module.params['interface']]['interface'][k] = v
        else:
            result['ansible_facts'][module.params['interface']]['peers'][section] = dict()
            for k, v in config.items(section):
                result['ansible_facts'][module.params['interface']]['peers'][section][k] = v
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
