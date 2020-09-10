# DNSMASQ
Ansible role to set up dnsmasq to resolve a domain name and its sub-domains to the `ansible_host`.

## Requirements
None.

## Role Variables
Available variables are listed below, along with default values `(see defaults/main.yml)`:
```yaml

```
Mandatory variables (role will fail if the variables are not set):
```yaml

```

## Dependencies
None.

# Example Playbook
```yaml
- name: set up dnsmasq
  hosts: all
  become: true
  roles:
    - role: dnsmasq
```

## Test
### Requirements
- python >= 3.7
- vagrant

### Run
```bash
pip install -r requirements.txt
molecule test
```

## License
MIT