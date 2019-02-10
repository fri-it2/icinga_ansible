# Ansible Role:icinga2_add_hosts

An Ansible role will add  host to Icinga 2 to be monitored. 

## Description

This role will add host to Icinga 2. Host will belong to the group and will be monitored
if available.

## Role Variables

* `host_address`  
  IP of host. Value of variable should be `json.primary_address` for json data like <https://git.arnes.si/anso/harfa/snippets/47>

* `fqdn`   
  A fully qualified domain name of host. Value of variable should be `json.name` for json data like <https://git.arnes.si/anso/harfa/snippets/47>

* `host_groups`  
  Host can be assign to specific groups. Variable shoud be type list(vlak element pa je hash s ključema name in slug). 
  List can be empty.

* `host_state`  
  Host can be removed or added. If host is removed, variable value is `absent`. If host is added, the variable value is `present`.
  Default value is `present`.

## Example Playbook

```yaml
- name: Add host to Icinga 2 to be monitored
  hosts: host.nekaj.si
  vars:
    host_address: "100.2.1.3"
    host_groups: [{
            "name": "Osnovna šola NG",
            "slug": "os-1"
        },{
        "slug": "sturj1e",
        "name": "Šturj1e"
    }] 
    fqdn: "nekaj.sola.si"
    host_state: "absent"
  roles:
    - icinga2_add_hosts
```
