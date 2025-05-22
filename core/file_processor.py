import re
import os
import json
import csv
from datetime import datetime

class FileProcessor:
    def __init__(self, log_file_path=None):
        self.log_file_path = log_file_path
        self.script_path_pattern = re.compile(r'#using\s+(scripts/[^;\n]+\.(?:gsc|csc))\s*;')
        self.hashed_script_pattern = re.compile(r'#(using|include)\s+script_([0-9a-f]{16})\s*;')
        self.hash_pattern = re.compile(r'#(?:"hash_|hash_)([0-9a-f]+)"?')
        self.plain_hash_pattern = re.compile(r'\bhash_([0-9a-f]+)\b')
        self.r_hash_pattern = re.compile(r'r"hash_([0-9a-f]+)"')
        self.percent_hash_pattern = re.compile(r'%"hash_([0-9a-f]+)"')
        self.and_hash_pattern = re.compile(r'&"hash_([0-9a-f]+)"')
        self.t_hash_pattern = re.compile(r't"hash_([0-9a-f]+)"')
        self.dvar_hash_pattern = re.compile(r'@"hash_([0-9a-f]+)"')
        self.omnvar_hash_pattern = re.compile(r'@o"hash_([0-9a-f]+)"')
        self.comment_pattern = re.compile(r'//.*')
        self.multiline_comment_pattern = re.compile(r'/\*.*?\*/', flags=re.DOTALL)
        self.known_hashed_strings_pattern = re.compile(r'#"([^"\n]+)(?<!hash_)"')
        self.quoted_strings_pattern = re.compile(r'"([^"\n]*)"')
        self.words_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*(?:_[0-9a-f]+)?\b')
        self.hash_string_pattern = re.compile(r'^hash_([0-9a-f]+)$')

    def is_hashed_word(self, word):
        data_types = [
            'var_', 'function_', 'namespace_', 'script_', '#"hash_', '#hash_',
            'hash_', 'class_', 'event_', 'r"hash_', '%"hash_', '&"hash_',
            't"hash_', '@"hash_', '@o"hash_'
        ]
        for dt in data_types:
            if word.startswith(dt):
                hash_part = word[len(dt):]
                if re.match(r'^[0-9a-f]+$', hash_part):
                    return True, dt
        return False, None

    def process_file(self, file_path, detected_game, keywords, tokens, valid_exts, supported_resources):
        file_path = str(file_path)
        unhashed_words = []
        hashed_words = []
        hash_quoted_strings = []
        hashed_script_paths = []
        known_hash_mappings = []
        non_hash_quoted_strings = []
        iw_resources_strings = []
        iw_dvars_strings = []
        omnvar_strings = []
        plain_hash_strings = []

        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        for value in row:
                            value = value.strip()
                            match = self.plain_hash_pattern.match(value)
                            if match:
                                hashed = match.group(1)
                                if hashed and not re.search(r'\s', hashed):
                                    plain_hash_strings.append(hashed)
                return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                        known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                        iw_dvars_strings, omnvar_strings, plain_hash_strings)

            if file_path.endswith('.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                        def extract_hashes(obj):
                            if isinstance(obj, str):
                                match = self.plain_hash_pattern.match(obj)
                                if match:
                                    hashed = match.group(1)
                                    if hashed and not re.search(r'\s', hashed):
                                        plain_hash_strings.append(hashed)
                            elif isinstance(obj, (list, tuple)):
                                for item in obj:
                                    extract_hashes(item)
                            elif isinstance(obj, dict):
                                for value in obj.values():
                                    extract_hashes(value)
                        extract_hashes(data)
                except json.JSONDecodeError:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        plain_hashes = self.plain_hash_pattern.findall(content)
                        for hashed in plain_hashes:
                            if hashed and not re.search(r'\s', hashed):
                                plain_hash_strings.append(hashed)
                return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                        known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                        iw_dvars_strings, omnvar_strings, plain_hash_strings)

            if file_path.endswith('.ddl'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    try:
                        lines = content.splitlines()
                        csv_reader = csv.reader(lines)
                        for row in csv_reader:
                            for value in row:
                                value = value.strip()
                                match = self.plain_hash_pattern.match(value)
                                if match:
                                    hashed = match.group(1)
                                    if hashed and not re.search(r'\s', hashed):
                                        plain_hash_strings.append(hashed)
                    except csv.Error:
                        plain_hashes = self.plain_hash_pattern.findall(content)
                        for hashed in plain_hashes:
                            if hashed and not re.search(r'\s', hashed):
                                plain_hash_strings.append(hashed)
                return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                        known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                        iw_dvars_strings, omnvar_strings, plain_hash_strings)

            content = None
            if file_path.endswith('.raw'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if not content.strip() or '\0' in content:
                            return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                                    known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                                    iw_dvars_strings, omnvar_strings, plain_hash_strings)
                except UnicodeDecodeError:
                    return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                            known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                            iw_dvars_strings, omnvar_strings, plain_hash_strings)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

            if not content or not content.strip():
                return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                        known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                        iw_dvars_strings, omnvar_strings, plain_hash_strings)

            content = content.replace('\\', '/')
            is_sp_folder = detected_game == "Black Ops 6" and 'sp' in file_path.lower().split(os.sep)

            if 'script_' in supported_resources:
                hashed_scripts = self.hashed_script_pattern.findall(content)
                for _, hashed_script in hashed_scripts:
                    if hashed_script and not re.search(r'\s', hashed_script):
                        hashed_script_paths.append(hashed_script)

            script_paths = self.script_path_pattern.findall(content)
            for script_path in script_paths:
                if isinstance(script_path, tuple):
                    script_path = script_path[0]
                if (script_path and not re.search(r'\s', script_path) and
                    re.match(r'^scripts/.*\.(?:gsc|csc)$', script_path)):
                    known_hash_mappings.append(script_path)

            content = self.comment_pattern.sub('', content)
            content = self.multiline_comment_pattern.sub('', content)

            if 'hash_' in supported_resources or '#"hash_' in supported_resources or '#hash_' in supported_resources:
                hashed_strings = self.hash_pattern.findall(content)
                for hashed in hashed_strings:
                    if hashed and not re.search(r'\s', hashed):
                        hash_quoted_strings.append((hashed, is_sp_folder))
                plain_hashes = self.plain_hash_pattern.findall(content)
                for hashed in plain_hashes:
                    if hashed and not re.search(r'\s', hashed):
                        plain_hash_strings.append(hashed)

            if 'r"hash_' in supported_resources:
                r_hashes = self.r_hash_pattern.findall(content)
                for hashed in r_hashes:
                    if hashed and not re.search(r'\s', hashed):
                        iw_resources_strings.append(('r"hash_', hashed))

            if '%"hash_' in supported_resources:
                percent_hashes = self.percent_hash_pattern.findall(content)
                for hashed in percent_hashes:
                    if hashed and not re.search(r'\s', hashed):
                        iw_resources_strings.append(('%"hash_', hashed))

            if '&"hash_' in supported_resources:
                and_hashes = self.and_hash_pattern.findall(content)
                for hashed in and_hashes:
                    if hashed and not re.search(r'\s', hashed):
                        hash_quoted_strings.append((hashed, is_sp_folder))

            if 't"hash_' in supported_resources:
                t_hashes = self.t_hash_pattern.findall(content)
                for hashed in t_hashes:
                    if hashed and not re.search(r'\s', hashed):
                        hash_quoted_strings.append((hashed, is_sp_folder))

            if '@"hash_' in supported_resources:
                dvar_hashes = self.dvar_hash_pattern.findall(content)
                for hashed in dvar_hashes:
                    if hashed and not re.search(r'\s', hashed):
                        iw_dvars_strings.append(hashed)

            if '@o"hash_' in supported_resources and file_path.endswith('.lua'):
                omnvar_hashes = self.omnvar_hash_pattern.findall(content)
                for hashed in omnvar_hashes:
                    if hashed and not re.search(r'\s', hashed):
                        omnvar_strings.append(hashed)

            known_hashed_strings = self.known_hashed_strings_pattern.findall(content)
            for known in known_hashed_strings:
                if (known and known not in keywords and
                    not re.search(r'\s', known) and
                    not any(token in known for token in tokens) and
                    re.match(r'^[a-zA-Z0-9_]+$', known) and
                    not self.hash_string_pattern.match(known)):
                    known_hash_mappings.append(known)

            quoted_strings = self.quoted_strings_pattern.findall(content)
            for quoted in quoted_strings:
                if (quoted and quoted not in keywords and
                    not any(token in quoted for token in tokens) and
                    not self.hash_string_pattern.match(quoted)):
                    non_hash_quoted_strings.append(quoted)

            words = self.words_pattern.findall(content)
            for word in words:
                word = word.strip().lower()
                if not word:
                    continue
                if re.search(r'\s', word):
                    continue
                if word in keywords:
                    continue
                if any(token in word for token in tokens) or word in tokens:
                    continue
                if re.match(r'^\d', word) or re.match(r'^0x[0-9a-f]+', word):
                    continue
                is_hashed, data_type = self.is_hashed_word(word)
                if is_hashed and data_type != 'hash_':
                    hashed_words.append(word)
                elif not is_hashed:
                    unhashed_words.append(word)

        except Exception as e:
            if self.log_file_path:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing {file_path}: {str(e)}\n")
            return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                    known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                    iw_dvars_strings, omnvar_strings, plain_hash_strings)

        return (unhashed_words, hashed_words, hash_quoted_strings, hashed_script_paths,
                known_hash_mappings, non_hash_quoted_strings, iw_resources_strings,
                iw_dvars_strings, omnvar_strings, plain_hash_strings)