import re
import os

from jinja2 import Template
import click
import inquirer

from create_tomochain_masternode import __version__
from . import templates

WORKING_PATH = os.getcwd()
QUESTIONS = [
    inquirer.Text(
        'name',
        message='What\'s your masternode name? [a-z0-9-]',
        validate=lambda _, x: re.match(r'^[a-z0-9][a-z0-9\-]+[a-z0-9]$', x),
    ),
    inquirer.Password(
        'private_key',
        message="What's your coinbase private key? (64char hex string)",
        validate=lambda _, x: len(x) == 64,
    ),
    inquirer.Text(
        'address',
        message="What's your coinbase address? (without 0x)",
    ),
    inquirer.Text(
        'data_path',
        message=("Where should the data be located? (docker volume name or "
                 "absolute path)"),
    ),
    inquirer.Confirm(
        'expose_rpc',
        message="Do you want to expose the RPC endpoint? (advanced use)",
    ),
    inquirer.Confirm(
        'expose_ws',
        message="Do you want to expose the WebSocket endpoint? (advanced use)",
    ),
]
ENVS = {
    'mainnet': {
        'metrics_endpoint': 'https://metrics.tomochain.com',
        'network_id': '88',
        'ws_secret': 'getty-site-pablo-auger-room-sos-blair-shin-whiz-delhi',
        'bootnodes': (
            'enode://97f0ca95a653e3c44d5df2674e19e9324ea4bf4d47a46b1d8560f3ed',
            '4ea328f725acec3fcfcb37eb11706cf07da669e9688b091f1543f89b2425700a',
            '68bc8876@104.248.98.78:30301,enode://b72927f349f3a27b789d0ca615f',
            'fe3526f361665b496c80e7cc19dace78bd94785fdadc270054ab727dbb172d9e',
            '3113694600dd31b2558dd77ad85a869032dea@188.166.207.189:30301,enod',
            'e://c8f2f0643527d4efffb8cb10ef9b6da4310c5ac9f2e988a7f85363e81d42',
            'f1793f64a9aa127dbaff56b1e8011f90fe9ff57fa02a36f73220da5ff81d8b8d',
            'f351@104.248.98.60:30301'
        )
    },
    'testnet': {
        'metrics_endpoint': 'https://metrics.testnet.tomochain.com',
        'network_id': '89',
        'ws_secret': 'anna-coal-flee-carrie-zip-hhhh-tarry-laue-felon-rhine',
        'bootnodes': (
            'enode://4d3c2cc0ce7135c1778c6f1cfda623ab44b4b6db55289543d48ecfde',
            '7d7111fd420c42174a9f2fea511a04cf6eac4ec69b4456bfaaae0e5bd236107d',
            '3172b013@52.221.28.223:30301,enode://298780104303fcdb37a84c5702e',
            'bd9ec660971629f68a933fd91f7350c54eea0e294b0857f1fd2e8dba2869fcc3',
            '6b83e6de553c386cf4ff26f19672955d9f312@13.251.101.216:30301,enode',
            '://46dba3a8721c589bede3c134d755eb1a38ae7c5a4c69249b8317c55adc8d4',
            '6a369f98b06514ecec4b4ff150712085176818d18f59a9e6311a52dbe68cff5b',
            '2ae@13.250.94.232:30301',
        )
    }
}


@click.command(help='Set up a TomoChain masternode by running one command.')
@click.argument('project')
@click.option('--testnet', is_flag=True, help='Use testnet settings')
@click.version_option(version=__version__)
def entrypoint(project, testnet) -> None:
    """Command line interface entrypoint"""
    env = ENVS['mainnet'] if not testnet else ENVS['testnet']
    project_path = os.path.join(WORKING_PATH, project)
    answers = inquirer.prompt(QUESTIONS)
    ports = []
    if answers['expose_rpc']:
        ports.append('8545')
    if answers['expose_ws']:
        ports.append('8546')

    compose_template = Template(templates.compose)
    compose_content = compose_template.render(
        bootnodes=env['bootnodes'],
        address=env['network_id'],
        ws_secret=env['ws_secret'],
        ports=ports,
        metrics_endpoint=env['metrics_endpoint']
    )

    env_template = Template(templates.env)
    env_content = env_template.render(
        name=answers['name'],
        address=answers['address'],
        private_key=answers['private_key'],
        data_path=answers['data_path'],
    )

    if not os.path.exists(project_path):
        os.makedirs(project_path)
    with open(f'{project_path}/docker-compose.yml', 'w') as compose_file:
        print(compose_content, file=compose_file)
    with open(f'{project_path}/env.yml', 'w') as env_file:
        print(env_content, file=env_file)
