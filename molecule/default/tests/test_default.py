import re


SYSTEMD_RELEASES = ['bionic', 'focal']


def test_dnsmasq_installed(host):
    dnsmasq = host.service('dnsmasq')
    assert dnsmasq.is_enabled
    assert dnsmasq.is_running


def test_dnsmasq_conf(host):
    dnsmasq_conf = host.file('/etc/dnsmasq.conf')
    assert dnsmasq_conf.exists
    assert dnsmasq_conf.user == 'root'
    assert dnsmasq_conf.group == 'root'
    assert dnsmasq_conf.contains('^domain-needed$')
    assert dnsmasq_conf.contains('^bogus-priv$')
    assert dnsmasq_conf.contains(r'^conf-dir=/etc/dnsmasq.d$')


def test_resolvconf_installed(host):
    if (host.system_info.codename not in SYSTEMD_RELEASES):
        resolvconf = host.package('resolvconf')
        assert resolvconf.is_installed


def test_jq_installed(host):
    if (host.system_info.codename in SYSTEMD_RELEASES):
        jq = host.package('jq')
        assert jq.is_installed


def test_systemd_resolved_conf(host):
    if (host.system_info.codename in SYSTEMD_RELEASES):
        resolved_conf = host.file('/etc/systemd/resolved.conf')
        assert resolved_conf.exists
        assert resolved_conf.user == 'root'
        assert resolved_conf.group == 'root'
        assert resolved_conf.contains('^DNSStubListener=no$')


def test_resolv_conf_file(host):
    resolv_conf = host.file('/etc/resolv.conf')
    ip = host.ansible(
        'setup'
    )['ansible_facts']['ansible_eth0']['ipv4']['address']
    assert resolv_conf.exists
    assert resolv_conf.user == 'root'
    assert resolv_conf.group == 'root'
    assert resolv_conf.contains(r'nameserver 127.0.0.1')
    assert resolv_conf.contains(f'nameserver {ip}')
    if (host.system_info.codename in SYSTEMD_RELEASES):
        assert not resolv_conf.is_symlink
        assert oct(resolv_conf.mode) == '0o644'
    else:
        assert resolv_conf.is_symlink


def test_update_dns_config_script(host):
    sha256sums = {
        'xenial': '2914e05804fd92cf478808ddcfc97d6de7b5562d7c0c8690d5ddfa203f'
                  '597313',
        'bionic': 'fbe63e1f8d360899cd18dc4b51eea4ddb70efdc9f19096258c460362f7'
                  'bfd489',
        'focal': '10f6c69cd35738865d68a06051a72dae9243878b8b6c98fdc67691b4c55'
                 '7892f',
        'buster': 'bf6f4c7b2427cd1ec08ddd98350992be449d195d0584e908ba7baf7f86'
                  '0fe09f'
    }
    release = host.system_info.codename
    update_dns_config = host.file('/usr/local/bin/update_dns_config')
    assert update_dns_config.exists
    assert update_dns_config.user == 'vagrant'
    assert update_dns_config.group == 'root'
    assert oct(update_dns_config.mode) == '0o744'
    assert update_dns_config.sha256sum == sha256sums[release]


def test_update_dns_config_hook_script(host):
    hook_files = {
        'xenial': {
            'sha256sum': 'b47f289a6cbb0af50c1489c29a833b17c4d04396f6332c29866'
                         'b6cf24f063d3e',
            'location': '/etc/dhcp/dhclient-enter-hooks.d'
        },
        'bionic': {
            'sha256sum': 'e9e632f79fdf2e967b2beefbdc587c6f38e04416029bc8116d8'
                         'd3d7423f208d9',
            'location': '/usr/lib/networkd-dispatcher/routable.d'
        },
        'focal': {
            'sha256sum': '5c0fd9c334c2c53cf46f087ef549c48cee80bbad47a2ef87887'
                         'a87c5c6a895ee',
            'location': '/usr/lib/networkd-dispatcher/routable.d'
        },
        'buster': {
            'sha256sum': 'b47f289a6cbb0af50c1489c29a833b17c4d04396f6332c29866'
                         'b6cf24f063d3e',
            'location': '/etc/dhcp/dhclient-enter-hooks.d'
        }
    }
    release = host.system_info.codename
    hook_location = f'{hook_files[release]["location"]}/update_dns_config_hook'
    update_dns_config_hook = host.file(hook_location)
    assert update_dns_config_hook.exists
    assert update_dns_config_hook.user == 'root'
    assert update_dns_config_hook.group == 'root'
    assert oct(update_dns_config_hook.mode) == '0o744'
    assert update_dns_config_hook.sha256sum == hook_files[release]['sha256sum']


def test_update_dns_ip_script(host):
    sha256sums = {
        'xenial': '2914e05804fd92cf478808ddcfc97d6de7b5562d7c0c8690d5ddfa203f'
                  '597313',
        'bionic': 'fbe63e1f8d360899cd18dc4b51eea4ddb70efdc9f19096258c460362f7'
                  'bfd489',
        'focal': '10f6c69cd35738865d68a06051a72dae9243878b8b6c98fdc67691b4c55'
                 '7892f',
        'buster': 'bf6f4c7b2427cd1ec08ddd98350992be449d195d0584e908ba7baf7f86'
                  '0fe09f'
    }
    release = host.system_info.codename
    update_dns_config = host.file('/usr/local/bin/update_dns_config')
    assert update_dns_config.exists
    assert update_dns_config.user == 'vagrant'
    assert update_dns_config.group == 'root'
    assert oct(update_dns_config.mode) == '0o744'
    assert update_dns_config.sha256sum == sha256sums[release]


def test_dnsmasq_address_file(host):
    release = host.system_info.codename
    ip = host.ansible(
        'setup'
    )['ansible_facts']['ansible_eth0']['ipv4']['address']
    address_file = host.file(f'/etc/dnsmasq.d/{release}.domain.org')
    assert address_file.exists
    assert address_file.user == 'root'
    assert address_file.group == 'root'
    assert address_file.contains(f'^address=/{release}.domain.org/{ip}')


def test_name_resolution(host):
    release = host.system_info.codename
    ip = host.ansible(
        'setup'
    )['ansible_facts']['ansible_eth0']['ipv4']['address']
    hostname = f'{release}.domain.org'
    nslookup = host.check_output(f'nslookup {hostname}')
    assert re.match(r'Server:\s+127\.0\.0\.1', nslookup.splitlines()[0])
    assert re.match(r'Address:\s+127\.0\.0\.1#53', nslookup.splitlines()[1])
    assert re.match(rf'Name:\s+{hostname}', nslookup.splitlines()[3])
    assert re.match(rf'Address:\s+{ip}', nslookup.splitlines()[4])
