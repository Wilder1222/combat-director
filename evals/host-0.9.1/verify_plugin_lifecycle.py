"""Exercise the actual Codex plugin CLI in an isolated configuration root.

No credentials, model requests, user configuration edits, or real plugin
upgrades. CODEX_HOME is used only for its documented child-process purpose.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[2]
CLI = Path('C:/Users/ww/AppData/Roaming/npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    work = Path(tempfile.mkdtemp(prefix='combat-host-lifecycle-', dir='D:/Temp'))
    isolated_config = work / 'codex-config'
    isolated_config.mkdir()
    market = work / 'marketplace'
    descriptor = market / '.agents/plugins/marketplace.json'
    descriptor.parent.mkdir(parents=True)
    payload = market / 'plugins/combat-director'
    market_name = 'combat-verification-local'
    selector = 'combat-director@' + market_name
    descriptor.write_text(json.dumps({
        'name': market_name,
        'interface': {'displayName': 'Local Combat Verification'},
        'plugins': [{
            'name': 'combat-director',
            'source': {'source': 'local', 'path': './plugins/combat-director'},
            'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
            'category': 'Productivity',
        }],
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    user_config = Path.home() / '.codex/config.toml'
    user_market = Path.home() / '.agents/plugins/marketplace.json'
    before = {'user_config_sha256': sha(user_config), 'user_marketplace_sha256': sha(user_market)}
    env = {**os.environ, 'CODEX_HOME': str(isolated_config), 'PYTHONUTF8': '1'}
    commands, verifications = [], []

    def run(label, *args):
        proc = subprocess.run([str(CLI), *args], cwd=work, env=env, capture_output=True, encoding='utf-8', errors='replace', timeout=60)
        record = {'label': label, 'argv': [str(CLI), *args], 'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
        commands.append(record)
        if proc.returncode:
            raise RuntimeError(label + ': CLI returned ' + str(proc.returncode))
        return proc.stdout

    def extract(version):
        archive = ROOT / 'dist' / f'combat-director-{version}.zip'
        with zipfile.ZipFile(archive) as z:
            for entry in z.namelist():
                destination = (payload / entry).resolve()
                if not destination.is_relative_to(payload.resolve()):
                    raise ValueError('Unsafe archive path')
            z.extractall(payload)
        return archive

    def verify_payload(version, archive):
        manifests = list((isolated_config / 'plugins/cache' / market_name / 'combat-director').glob('*/.codex-plugin/plugin.json'))
        matches = [p for p in manifests if json.loads(p.read_text(encoding='utf-8'))['version'] == version]
        if len(matches) != 1:
            raise ValueError(f'Expected one cached {version}; got {len(matches)}')
        cached = matches[0].parent.parent
        mismatches = []
        with zipfile.ZipFile(archive) as z:
            entries = [i for i in z.infolist() if not i.is_dir()]
            for entry in entries:
                target = cached / entry.filename
                if not target.is_file() or target.read_bytes() != z.read(entry.filename):
                    mismatches.append(entry.filename)
        if mismatches:
            raise ValueError('Cached payload differs: ' + repr(mismatches))
        verifications.append({'version': version, 'cached_path': str(cached), 'files_compared': len(entries), 'archive_sha256': sha(archive), 'mismatches': mismatches})

    error = None
    try:
        run('CLI version', '--version')
        initial_archive = extract('0.9.0')
        run('add isolated marketplace', 'plugin', 'marketplace', 'add', str(market), '--json')
        run('install 0.9.0', 'plugin', 'add', selector, '--json')
        verify_payload('0.9.0', initial_archive)
        run('list after initial install', 'plugin', 'list')
        upgraded_archive = extract('0.9.1')
        run('upgrade to 0.9.1', 'plugin', 'add', selector, '--json')
        verify_payload('0.9.1', upgraded_archive)
        run('list after upgrade', 'plugin', 'list')
        extract('0.9.0')
        run('rollback to 0.9.0', 'plugin', 'add', selector, '--json')
        verify_payload('0.9.0', initial_archive)
        run('list after rollback', 'plugin', 'list')
        run('uninstall isolated plugin', 'plugin', 'remove', selector, '--json')
        run('list after uninstall', 'plugin', 'list')
        run('remove isolated marketplace', 'plugin', 'marketplace', 'remove', market_name)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        error = str(exc)
    after = {'user_config_sha256': sha(user_config), 'user_marketplace_sha256': sha(user_market)}
    report = {
        'format': 'combat-host-lifecycle/1', 'date': '2026-09-24',
        'workspace': str(work), 'isolated_codex_home': str(isolated_config),
        'selector': selector, 'commands': commands, 'payload_checks': verifications,
        'real_user_config_unchanged': before == after,
        'real_user_hashes_before': before, 'real_user_hashes_after': after,
        'error': error,
        'scope': 'Actual local CLI and cached-payload lifecycle only; no model invocation, implicit discovery, authentication, desktop refresh or video validation.',
    }
    report['passed'] = error is None and before == after
    out = ROOT / 'docs/implementation/host-lifecycle-0.9.1.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'commands': len(commands), 'payload_checks': len(verifications), 'error': error, 'report': str(out)}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
