import os
import re
from pathlib import Path
from datetime import datetime

class ScriptProcessor:
    def __init__(self, log_callback=None):
        self.unhashed_words = []
        self.hashed_words = []
        self.hash_quoted_strings = set()
        self.hashed_script_paths = set()
        self.known_hash_mappings = set()
        self.non_hash_quoted_strings = set()
        self.iw_resources_strings = set()
        self.iw_dvars_strings = set()
        self.omnvar_strings = set()

        self.hash_to_string = {
            "643a7daf": "disconnect"
        }

        self.game_short_names = {
            "Black Ops 3": "bo3",
            "Black Ops 4": "bo4",
            "Black Ops Cold War": "bocw",
            "Modern Warfare III": "mwiii",
            "Black Ops 6": "bo6"
        }

        self.supported_data_types = {
            "Black Ops 3": ['var_', 'function_', 'namespace_', 'class_'],
            "Black Ops 4": ['var_', 'function_', 'namespace_', 'class_', 'event_'],
            "Black Ops Cold War": ['var_', 'function_', 'namespace_', 'class_', 'event_'],
            "Modern Warfare III": ['var_', 'function_', 'namespace_'],
            "Black Ops 6": ['var_', 'function_', 'namespace_']
        }

        self.supported_resources_types = {
            "Black Ops 3": ['#"hash_', '#hash_'],
            "Black Ops 4": ['#"hash_', '#hash_', 'script_'],
            "Black Ops Cold War": ['#"hash_', '#hash_', 'script_'],
            "Modern Warfare III": ['#"hash_', '#hash_', 'script_', 'r"hash_', '%"hash_', '&"hash_', 't"hash_'],
            "Black Ops 6": ['#"hash_', '#hash_', 'script_', 'r"hash_', '%"hash_', '&"hash_', 't"hash_']
        }

        self.supported_dvar_types = {
            "Modern Warfare III": ['@"hash_'],
            "Black Ops 6": ['@"hash_']
        }

        self.supported_omnvar_types = {
            "Black Ops 6": ['@o"hash_']
        }

        # Initialize log file
        self.log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_manager.log")
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write("Script Manager Log\n")

        # Callback for real-time log updates
        self.log_callback = log_callback

    def log_action(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_message)
        # Notify the UI of the new log message
        if self.log_callback:
            self.log_callback(log_message)

    def get_game_dir(self, detected_game):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), detected_game)

    def is_hashed_word(self, word):
        data_types = [
            'var_', 'function_', 'namespace_', 'script_', '#"hash_', '#hash_',
            'class_', 'event_', 'r"hash_', '%"hash_', '&"hash_', 't"hash_', '@"hash_', '@o"hash_'
        ]
        for dt in data_types:
            if word.startswith(dt):
                hash_part = word[len(dt):]
                if re.match(r'^[0-9a-f]+$', hash_part):
                    return True, dt
        return False, None

    def process_scripts(self, folder, detected_game):
        from game_detector import get_default_hash_function
        from cod_hashes import (
            base_fnv1a_63, base_fnv1a_64, base_fnv1a_32, iw_resources, mwii_iii_scr,
            black_ops_3_scr, hash_bo4cw_scr, black_ops_6_scr, black_ops_6_sp_scr,
            iw_dvars, black_ops_6_omnvars
        )

        self.unhashed_words = []
        self.hashed_words = []
        self.hash_quoted_strings = set()
        self.hashed_script_paths = set()
        self.known_hash_mappings = set()
        self.non_hash_quoted_strings = set()
        self.iw_resources_strings = set()
        self.iw_dvars_strings = set()
        self.omnvar_strings = set()

        keywords = {
            '#using', '#namespace', 'function', 'switch', 'case', 'default',
            'level', 'self', 'class', 'if', 'else', 'for', 'while', 'true',
            'false', 'continue', 'break', 'wait', 'waittill', 'undefined',
            'return', 'thread', 'endon', 'event_handler', 'new', 'childthread'
        }

        tokens = {
            '(', ')', '[]', '&', '&&', '!', '||', '=', '==', '===', '<', '<=', '>', '>=', '!=', '[[', ']]', '[[]]', ';'
        }

        valid_exts = ('.gsc', '.csc', '.gsh', '.ddl', '.json', '.csv', '.raw', '.txt', '.lua')

        script_path_pattern = re.compile(r'#using\s+(scripts/[^;\n]+\.(gsc|csc))\s*;')
        hashed_script_pattern = re.compile(r'#(using|include)\s+script_([0-9a-f]{16})\s*;')
        hash_pattern = re.compile(r'#(?:"hash_|hash_)([0-9a-f]+)"')
        hash_no_quote_pattern = re.compile(r'#hash_([0-9a-f]+)\b')
        r_hash_pattern = re.compile(r'r"hash_([0-9a-f]+)"')
        percent_hash_pattern = re.compile(r'%"hash_([0-9a-f]+)"')
        and_hash_pattern = re.compile(r'&"hash_([0-9a-f]+)"')
        t_hash_pattern = re.compile(r't"hash_([0-9a-f]+)"')
        dvar_hash_pattern = re.compile(r'@"hash_([0-9a-f]+)"')
        omnvar_hash_pattern = re.compile(r'@o"hash_([0-9a-f]+)"')

        # Define supported_resources at method scope
        supported_resources = self.supported_resources_types.get(detected_game, [])

        # Generator to yield progress for each file
        def process_files():
            for root_dir, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(valid_exts):
                        file_path = Path(root_dir) / file
                        yield file_path

        total_files = sum(1 for _ in process_files())
        processed_files = 0

        for file_path in process_files():
            processed_files += 1
            self.log_action(f"Processing file {processed_files}/{total_files}: {file_path}")
            try:
                if file.endswith('.raw'):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if not content.strip() or '\0' in content:
                                self.log_action(f"Skipped unreadable .raw file (binary or empty): {file_path}")
                                continue
                    except UnicodeDecodeError as e:
                        self.log_action(f"Skipped unreadable .raw file (UnicodeDecodeError): {file_path}")
                        continue
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                if not content.strip():
                    continue

                content = content.replace('\\', '/')

                is_sp_folder = detected_game == "Black Ops 6" and 'sp' in str(file_path).lower().split(os.sep)

                if 'script_' in supported_resources:
                    hashed_scripts = hashed_script_pattern.findall(content)
                    for _, hashed_script in hashed_scripts:
                        if hashed_script and not re.search(r'\s', hashed_script):
                            self.hashed_script_paths.add(hashed_script)

                script_paths = script_path_pattern.findall(content)
                for script_path in script_paths:
                    if (script_path and not re.search(r'\s', script_path) and
                        re.match(r'^scripts/.*\.(gsc|csc)$', script_path)):
                        self.known_hash_mappings.add(script_path)

                content = re.sub(r'//.*', '', content)
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

                if '#"hash_' in supported_resources or '#hash_' in supported_resources:
                    hashed_strings = hash_pattern.findall(content)
                    for hashed in hashed_strings:
                        if hashed and not re.search(r'\s', hashed):
                            self.hash_quoted_strings.add(hashed)

                    hashed_strings_no_quote = hash_no_quote_pattern.findall(content)
                    for hashed in hashed_strings_no_quote:
                        if hashed and not re.search(r'\s', hashed):
                            self.hash_quoted_strings.add(hashed)

                if 'r"hash_' in supported_resources:
                    r_hashes = r_hash_pattern.findall(content)
                    for hashed in r_hashes:
                        if hashed and not re.search(r'\s', hashed):
                            self.iw_resources_strings.add(hashed)

                if '%"hash_' in supported_resources:
                    percent_hashes = percent_hash_pattern.findall(content)
                    for hashed in percent_hashes:
                        if hashed and not re.search(r'\s', hashed):
                            self.iw_resources_strings.add(hashed)

                if '&"hash_' in supported_resources:
                    and_hashes = and_hash_pattern.findall(content)
                    for hashed in and_hashes:
                        if hashed and not re.search(r'\s', hashed):
                            self.hash_quoted_strings.add(hashed)

                if 't"hash_' in supported_resources:
                    t_hashes = t_hash_pattern.findall(content)
                    for hashed in t_hashes:
                        if hashed and not re.search(r'\s', hashed):
                            self.hash_quoted_strings.add(hashed)

                if '@"hash_' in self.supported_dvar_types.get(detected_game, []):
                    dvar_hashes = dvar_hash_pattern.findall(content)
                    for hashed in dvar_hashes:
                        if hashed and not re.search(r'\s', hashed):
                            self.iw_dvars_strings.add(hashed)

                if '@o"hash_' in self.supported_omnvar_types.get(detected_game, []) and file.endswith('.lua'):
                    omnvar_hashes = omnvar_hash_pattern.findall(content)
                    for hashed in omnvar_hashes:
                        if hashed and not re.search(r'\s', hashed):
                            self.omnvar_strings.add(hashed)

                known_hashed_strings = re.findall(r'#(?:"(?!hash_)|)([^"\n]+)"?', content)
                for known in known_hashed_strings:
                    if (known and known not in keywords and
                        not re.search(r'\s', known) and
                        not any(token in known for token in tokens) and
                        re.match(r'^[a-zA-Z0-9_]+$', known)):
                        self.known_hash_mappings.add(known)

                quoted_strings = re.findall(r'"([^"\n]*)"', content)
                for quoted in quoted_strings:
                    if (quoted and quoted not in keywords and
                        not re.search(r'\s', quoted) and
                        not any(token in known for token in tokens) and
                        re.match(r'^[a-zA-Z0-9_]+$', quoted) and
                        quoted not in self.hash_quoted_strings and
                        quoted not in self.known_hash_mappings):
                        self.non_hash_quoted_strings.add(quoted)

                words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*(?:_[0-9a-f]+)?\b', content)
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
                    is_hashed, _ = self.is_hashed_word(word)
                    if is_hashed:
                        self.hashed_words.append(word)
                    else:
                        self.unhashed_words.append(word)
            except Exception as e:
                self.log_action(f"Error processing file {file_path}: {str(e)}")
                continue

        self.unhashed_words = sorted(set(self.unhashed_words))
        self.hashed_words = sorted(set(self.hashed_words))
        self.hash_quoted_strings = sorted(set(self.hash_quoted_strings))
        self.hashed_script_paths = sorted(set(self.hashed_script_paths))
        self.known_hash_mappings = sorted(set(self.known_hash_mappings))
        self.non_hash_quoted_strings = sorted(set(self.non_hash_quoted_strings))
        self.iw_resources_strings = sorted(set(self.iw_resources_strings))
        self.iw_dvars_strings = sorted(set(self.iw_dvars_strings))
        self.omnvar_strings = sorted(set(self.omnvar_strings))
        total_words = len(self.unhashed_words) + len(self.hashed_words)

        game_dir = self.get_game_dir(detected_game)
        os.makedirs(game_dir, exist_ok=True)
        short_game_name = self.game_short_names.get(detected_game, "unknown")

        known_hashed_words = set(self.hashed_words)
        supported_scr_types = self.supported_data_types.get(detected_game, [])
        hashed_by_type = {dt: set() for dt in supported_scr_types}

        for word in known_hashed_words:
            is_hashed, data_type = self.is_hashed_word(word)
            if is_hashed and data_type in supported_scr_types:
                hash_part = word[len(data_type):]
                hashed_by_type[data_type].add(hash_part)

        for data_type, words in hashed_by_type.items():
            if words:
                dt_clean = data_type.rstrip('_')
                filename = os.path.join(game_dir, f"{short_game_name}_{dt_clean}.csv")
                with open(filename, 'w', encoding='utf-8') as f:
                    for word in sorted(words):
                        f.write(f"{word}\n")

        if 'script_' in supported_resources:
            script_hash_file = os.path.join(game_dir, f"{short_game_name}_script.csv")
            with open(script_hash_file, 'w', encoding='utf-8') as f:
                for word in self.hashed_script_paths:
                    f.write(f"{word}\n")

        if any(t in supported_resources for t in ['#"hash_', '#hash_', '&"hash_', 't"hash_']):
            hash_file = os.path.join(game_dir, f"{short_game_name}_hash.csv")
            with open(hash_file, 'w', encoding='utf-8') as f:
                for word in self.hash_quoted_strings:
                    f.write(f"{word}\n")

        if '@"hash_' in self.supported_dvar_types.get(detected_game, []):
            dvar_file = os.path.join(game_dir, f"{short_game_name}_dvar.csv")
            with open(dvar_file, 'w', encoding='utf-8') as f:
                for word in self.iw_dvars_strings:
                    f.write(f"{word}\n")

        if '@o"hash_' in self.supported_omnvar_types.get(detected_game, []):
            omnvar_file = os.path.join(game_dir, f"{short_game_name}_omnvar.csv")
            with open(omnvar_file, 'w', encoding='utf-8') as f:
                for word in self.omnvar_strings:
                    f.write(f"{word}\n")

        general_hashes = set()
        default_hash_func = get_default_hash_function(detected_game)

        scr_hash_func = None
        if detected_game == "Black Ops 3":
            scr_hash_func = black_ops_3_scr
            default_hash_func = black_ops_3_scr
        elif detected_game == "Black Ops 4":
            scr_hash_func = hash_bo4cw_scr
            default_hash_func = hash_bo4cw_scr
        elif detected_game == "Black Ops Cold War":
            scr_hash_func = hash_bo4cw_scr
            default_hash_func = hash_bo4cw_scr
        elif detected_game == "Modern Warfare III":
            scr_hash_func = mwii_iii_scr
            default_hash_func = mwii_iii_scr
        elif detected_game == "Black Ops 6":
            scr_hash_func = black_ops_6_scr
            default_hash_func = black_ops_6_scr

        xasset_hash_func = None
        if detected_game == "Black Ops 3":
            xasset_hash_func = black_ops_3_scr
        elif detected_game == "Black Ops 4":
            xasset_hash_func = base_fnv1a_63
        elif detected_game == "Black Ops Cold War":
            xasset_hash_func = base_fnv1a_63
        elif detected_game == "Modern Warfare III":
            xasset_hash_func = base_fnv1a_63
        elif detected_game == "Black Ops 6":
            xasset_hash_func = base_fnv1a_64

        for word in self.known_hash_mappings:
            hash_func = default_hash_func
            if word.startswith('scripts/'):
                if detected_game == "Modern Warfare III":
                    hash_func = iw_resources
                elif detected_game == "Black Ops 6":
                    hash_func = iw_resources
                else:
                    hash_func = xasset_hash_func
            else:
                hash_func = xasset_hash_func

            if hash_func:
                word_for_hashing = word.replace('\\', '/')
                hash_value = hash_func(word_for_hashing)
                hash_str = f"{hash_value:x}" if hash_func.__name__.endswith("_63") or hash_func.__name__.endswith("_64") else f"{hash_value:08x}"
                general_hashes.add((hash_str, word))

        if detected_game in ["Black Ops 6", "Modern Warfare III"]:
            for iw_string in self.iw_resources_strings:
                hash_value = iw_resources(iw_string)
                hash_str = f"{hash_value:x}"
                general_hashes.add((hash_str, iw_string))

        for hash_string in self.hash_quoted_strings:
            hash_func = None
            if hash_string in [h for h in and_hash_pattern.findall(content)]:
                if detected_game == "Modern Warfare III":
                    hash_func = mwii_iii_scr
                elif detected_game == "Black Ops 6":
                    hash_func = black_ops_6_scr if not is_sp_folder else black_ops_6_sp_scr
            elif hash_string in [h for h in t_hash_pattern.findall(content)]:
                if detected_game == "Modern Warfare III":
                    hash_func = base_fnv1a_32
                elif detected_game == "Black Ops 6":
                    hash_func = black_ops_6_sp_scr if is_sp_folder else black_ops_6_scr

            if hash_func:
                hash_value = hash_func(hash_string)
                hash_str = f"{hash_value:x}" if hash_func.__name__.endswith("_63") or hash_func.__name__.endswith("_64") else f"{hash_value:08x}"
                general_hashes.add((hash_str, hash_string))

        if '@"hash_' in self.supported_dvar_types.get(detected_game, []):
            for dvar_string in self.iw_dvars_strings:
                hash_value = iw_dvars(dvar_string)
                hash_str = f"{hash_value:x}"
                general_hashes.add((hash_str, dvar_string))

        if '@o"hash_' in self.supported_omnvar_types.get(detected_game, []):
            for omnvar_string in self.omnvar_strings:
                hash_value = black_ops_6_omnvars(omnvar_string)
                hash_str = f"{hash_value:x}"
                general_hashes.add((hash_str, omnvar_string))

        general_file = os.path.join(game_dir, f"{short_game_name}.csv")
        existing_general_hashes = set()
        if os.path.exists(general_file):
            with open(general_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        hash_str, word = line.strip().split(',', 1)
                        existing_general_hashes.add((hash_str, word))

        new_hashes = set(general_hashes)
        extra_hashes = existing_general_hashes - new_hashes
        if extra_hashes:
            self.log_action(f"Existing {short_game_name}.csv has {len(extra_hashes)} hashes that were not found in new data:\n" + "\n".join(f"  {h},{w}" for h, w in sorted(extra_hashes)))

        general_hashes.update(existing_general_hashes)

        with open(general_file, 'w', encoding='utf-8') as f:
            for hash_str, word in sorted(general_hashes, key=lambda x: x[0]):
                f.write(f"{hash_str},{word}\n")

        dictionary_values = set()
        for word in self.known_hash_mappings:
            if word:
                dictionary_values.add(word)
        for word in self.non_hash_quoted_strings:
            if word:
                dictionary_values.add(word)
        for iw_string in self.iw_resources_strings:
            if iw_string:
                dictionary_values.add(iw_string)
        for dvar_string in self.iw_dvars_strings:
            if dvar_string:
                dictionary_values.add(dvar_string)
        for omnvar_string in self.omnvar_strings:
            if omnvar_string:
                dictionary_values.add(omnvar_string)

        dictionary_file = os.path.join(game_dir, f"{short_game_name}_dictionary.csv")
        existing_dictionary_values = set()
        if os.path.exists(dictionary_file):
            with open(dictionary_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        existing_dictionary_values.add(line.strip())

        dictionary_values.update(existing_dictionary_values)

        with open(dictionary_file, 'w', encoding='utf-8') as f:
            for word in sorted(dictionary_values):
                if word:
                    f.write(f"{word}\n")

        return total_words, len(self.unhashed_words), len(self.hashed_words)