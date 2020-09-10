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
    if (
        host.ansible('setup')['ansible_facts']['ansible_lsb']['codename']
        not in SYSTEMD_RELEASES
    ):
        resolvconf = host.package('resolvconf')
        assert resolvconf.is_installed


def test_jq_installed(host):
    if (
        host.ansible('setup')['ansible_facts']['ansible_lsb']['codename']
        in SYSTEMD_RELEASES
    ):
        jq = host.package('jq')
        assert jq.is_installed


def test_systemd_resolved_conf(host):
    if (
        host.ansible('setup')['ansible_facts']['ansible_lsb']['codename']
        in SYSTEMD_RELEASES
    ):
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
    if (
        host.ansible('setup')['ansible_facts']['ansible_lsb']['codename']
        in SYSTEMD_RELEASES
    ):
        assert not resolv_conf.is_symlink
        assert oct(resolv_conf.mode) == '0o644'
    else:
        assert resolv_conf.is_symlink


def test_update_dns_config_script(host):
    update_dns_config = host.file('/usr/local/bin/update_dns_config')
    assert update_dns_config.exists
    assert update_dns_config.user == 'vagrant'
    assert update_dns_config.group == 'root'
    assert oct(update_dns_config.mode) == '0o744'
