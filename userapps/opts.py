from oslo_config.cfg import *

opts = {
    'default':       [
        StrOpt('discover_mode', default='manual', choices=('manual', 'fuel')),
        StrOpt('rpc_backend', default='rabbit', choices=('rabbit', 'pika'))
    ],
    'discover_fuel': [
        StrOpt('master_node')
    ],
    'discover_file': [
        StrOpt('file', default='hosts.yml')
    ]
}


def register_opts():
    for group_name in opts:
        if group_name != 'default':
            group = OptGroup(group_name)
            CONF.register_group(group)
            CONF.register_opts(opts[group_name], group=group)
        else:
            CONF.register_opts(opts[group_name])

    return CONF


config = CONF
register_opts()
config(sys.argv[1:])
