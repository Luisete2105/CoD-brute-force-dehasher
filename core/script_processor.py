import os
import json
from pathlib import Path
from datetime import datetime
import csv
import multiprocessing as mp
from functools import partial
from core.game_detector import get_game_specific_header, get_game_specific_hashes
from core.cod_hashes import (
    base_fnv1a_63, base_fnv1a_64, base_fnv1a_32,
    iw_resources, mwii_iii_scr, black_ops_3_scr, hash_bo4cw_scr,
    iw_dvars, black_ops_6_scr, black_ops_6_omnvars, black_ops_6_sp_scr
)
from core.file_processor import FileProcessor

class ScriptProcessor:
    def __init__(self, log_file_path=None, progress_queue=None):
        self.log_file_path = log_file_path
        self.progress_queue = progress_queue
        self.file_processor = FileProcessor(log_file_path)
        self.processed_count = None

    def process_scripts(self, folder, detected_game):
        valid_exts = ['.gsc', '.csc', '.lua', '.raw', '.csv', '.json', '.ddl']
        keywords = {'if', 'else', 'while', 'for', 'return', 'true', 'false', 'null', 'undefined'}
        tokens = {'#include', '#using', '#define', '#if', '#endif', '#else', '#elseif'}
        supported_resources = {
            'Black Ops 3': ['var_', 'function_', 'namespace_', 'class_', '#"hash_', '#hash_', 'hash_'],
            'Black Ops 4': ['var_', 'function_', 'namespace_', 'class_', 'event_', '#"hash_', '#hash_', 'hash_', 'script_'],
            'Black Ops Cold War': ['var_', 'function_', 'namespace_', 'class_', 'event_', '#"hash_', '#hash_', 'hash_', 'script_'],
            'Modern Warfare III': ['var_', 'function_', 'namespace_', '#"hash_', '#hash_', 'hash_', 'script_', 'r"hash_', '%"hash_', '&"hash_', 't"hash_', '@"hash_'],
            'Black Ops 6': ['var_', 'function_', 'namespace_', '#"hash_', '#hash_', 'hash_', 'script_', 'r"hash_', '%"hash_', '&"hash_', 't"hash_', '@"hash_', '@o"hash_']
        }.get(detected_game, [])

        game_info = {
            'Black Ops 3': ('bo3', 'Black Ops 3'),
            'Black Ops 4': ('bo4', 'Black Ops 4'),
            'Black Ops Cold War': ('bocw', 'Black Ops Cold War'),
            'Modern Warfare III': ('mwiii', 'Modern Warfare III'),
            'Black Ops 6': ('bo6', 'Black Ops 6')
        }
        game_short_name, game_full_name = game_info.get(detected_game, ('unknown', 'Unknown'))

        hash_functions = {
            'Black Ops 3': {
                'var_': black_ops_3_scr,
                'function_': black_ops_3_scr,
                'namespace_': black_ops_3_scr,
                'class_': black_ops_3_scr,
                '#"hash_': black_ops_3_scr,
                '#hash_': black_ops_3_scr,
                'hash_': black_ops_3_scr
            },
            'Black Ops 4': {
                'var_': hash_bo4cw_scr,
                'function_': hash_bo4cw_scr,
                'namespace_': hash_bo4cw_scr,
                'class_': hash_bo4cw_scr,
                'event_': hash_bo4cw_scr,
                '#"hash_': base_fnv1a_63,
                '#hash_': base_fnv1a_63,
                'hash_': base_fnv1a_63,
                'script_': base_fnv1a_63
            },
            'Black Ops Cold War': {
                'var_': hash_bo4cw_scr,
                'function_': hash_bo4cw_scr,
                'namespace_': hash_bo4cw_scr,
                'class_': hash_bo4cw_scr,
                'event_': hash_bo4cw_scr,
                '#"hash_': base_fnv1a_63,
                '#hash_': base_fnv1a_63,
                'hash_': base_fnv1a_63,
                'script_': base_fnv1a_63
            },
            'Modern Warfare III': {
                'var_': mwii_iii_scr,
                'function_': mwii_iii_scr,
                'namespace_': mwii_iii_scr,
                '#"hash_': base_fnv1a_63,
                '#hash_': base_fnv1a_63,
                'hash_': base_fnv1a_63,
                'script_': iw_resources,
                'r"hash_': iw_resources,
                '%"hash_': iw_resources,
                '&"hash_': mwii_iii_scr,
                't"hash_': base_fnv1a_32,
                '@"hash_': iw_dvars
            },
            'Black Ops 6': {
                'var_': black_ops_6_scr,
                'function_': black_ops_6_scr,
                'namespace_': black_ops_6_scr,
                '#"hash_': base_fnv1a_64,
                '#hash_': base_fnv1a_64,
                'hash_': base_fnv1a_64,
                'script_': iw_resources,
                'r"hash_': iw_resources,
                '%"hash_': iw_resources,
                '&"hash_': lambda x: black_ops_6_sp_scr(x) if 'sp' in str(x).lower().split(os.sep) else black_ops_6_scr(x),
                't"hash_': base_fnv1a_32,
                '@"hash_': iw_dvars,
                '@o"hash_': black_ops_6_omnvars
            }
        }.get(detected_game, {})

        total_words = 0
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

        files = []
        for root, _, filenames in os.walk(folder):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in valid_exts):
                    files.append(Path(root) / filename)

        total_files = len(files)
        if self.log_file_path:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting extraction for {total_files} files in {folder}\n")

        unknown_hashes = {
            'var_': [], 'function_': [], 'namespace_': [], 'class_': [], 'event_': [],
            'script_': [], 'hash_': [], 'r"hash_': [], '%"hash_': [], '&"hash_': [],
            't"hash_': [], '@"hash_': [], '@o"hash_': []
        }

        try:
            cpu_count = max(1, mp.cpu_count() - 1)
            chunk_size = max(1, len(files) // cpu_count)
            if self.log_file_path:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Setting up multiprocessing: {cpu_count} processes, chunk size {chunk_size}\n")
            self.processed_count = mp.Value('i', 0)

            with mp.Pool(processes=cpu_count) as pool:
                process_func = partial(self.file_processor.process_file, detected_game=detected_game,
                                        keywords=keywords, tokens=tokens, valid_exts=valid_exts,
                                        supported_resources=supported_resources)
                for i, result in enumerate(pool.imap_unordered(process_func, files, chunksize=chunk_size)):
                    (uw, hw, hqs, hsp, khm, nhqs, iwr, idv, omn, phs) = result
                    unhashed_words.extend(uw)
                    hashed_words.extend(hw)
                    hash_quoted_strings.extend(hqs)
                    hashed_script_paths.extend(hsp)
                    known_hash_mappings.extend(khm)
                    non_hash_quoted_strings.extend(nhqs)
                    iw_resources_strings.extend(iwr)
                    iw_dvars_strings.extend(idv)
                    omnvar_strings.extend(omn)
                    plain_hash_strings.extend(phs)

                    # Populate unknown_hashes
                    for word in hw:
                        is_hashed, data_type = self.file_processor.is_hashed_word(word)
                        if is_hashed and data_type in unknown_hashes:
                            hash_value = word[len(data_type):]
                            unknown_hashes[data_type].append(hash_value)
                    for hashed, _ in hqs:
                        if detected_game == "Black Ops 6":
                            if '&"hash_' in supported_resources and hashed in [x[1] for x in iwr if x[0] == '&"hash_']:
                                unknown_hashes['&"hash_'].append(hashed)
                            elif 't"hash_' in supported_resources and hashed in [x[1] for x in iwr if x[0] == 't"hash_']:
                                unknown_hashes['t"hash_'].append(hashed)
                            else:
                                unknown_hashes['hash_'].append(hashed)
                        else:
                            unknown_hashes['hash_'].append(hashed)
                    for hashed in hsp:
                        unknown_hashes['script_'].append(hashed)
                    for pattern, hashed in iwr:
                        unknown_hashes[pattern].append(hashed)
                    for hashed in idv:
                        unknown_hashes['@"hash_'].append(hashed)
                    for hashed in omn:
                        unknown_hashes['@o"hash_'].append(hashed)
                    for hashed in phs:
                        unknown_hashes['hash_'].append(hashed)

                    total_words += len(uw) + len(hw) + len(uw) + len(hqs) + len(hsp) + len(khm) + len(nhqs) + len(iwr) + len(idv) + len(omn) + len(phs)

                    with self.processed_count.get_lock():
                        self.processed_count.value += 1
                        processed_files = self.processed_count.value
                    if total_files > 0 and self.progress_queue and (i % 10 == 0 or i == total_files - 1):
                        progress = (processed_files / total_files) * 100
                        self.progress_queue.put(progress)

        except Exception as e:
            if self.log_file_path:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Multiprocessing failed: {str(e)}\n")
            self.processed_count = None
            for i, file_path in enumerate(files):
                result = self.file_processor.process_file(file_path, detected_game, keywords, tokens, valid_exts, supported_resources)
                (uw, hw, hqs, hsp, khm, nhqs, iwr, idv, omn, phs) = result
                unhashed_words.extend(uw)
                hashed_words.extend(hw)
                hash_quoted_strings.extend(hqs)
                hashed_script_paths.extend(hsp)
                known_hash_mappings.extend(khm)
                non_hash_quoted_strings.extend(nhqs)
                iw_resources_strings.extend(iwr)
                iw_dvars_strings.extend(idv)
                omnvar_strings.extend(omn)
                plain_hash_strings.extend(phs)

                for word in hw:
                    is_hashed, data_type = self.file_processor.is_hashed_word(word)
                    if is_hashed and data_type in unknown_hashes:
                        hash_value = word[len(data_type):]
                        unknown_hashes[data_type].append(hash_value)
                for hashed, _ in hqs:
                    if detected_game == "Black Ops 6":
                        if '&"hash_' in supported_resources and hashed in [x[1] for x in iwr if x[0] == '&"hash_']:
                            unknown_hashes['&"hash_'].append(hashed)
                        elif 't"hash_' in supported_resources and hashed in [x[1] for x in iwr if x[0] == 't"hash_']:
                            unknown_hashes['t"hash_'].append(hashed)
                        else:
                            unknown_hashes['hash_'].append(hashed)
                    else:
                        unknown_hashes['hash_'].append(hashed)
                for hashed in hsp:
                    unknown_hashes['script_'].append(hashed)
                for pattern, hashed in iwr:
                    unknown_hashes[pattern].append(hashed)
                for hashed in idv:
                    unknown_hashes['@"hash_'].append(hashed)
                for hashed in omn:
                    unknown_hashes['@o"hash_'].append(hashed)
                for hashed in phs:
                    unknown_hashes['hash_'].append(hashed)

                total_words += len(uw) + len(hw) + len(hqs) + len(hsp) + len(khm) + len(nhqs) + len(iwr) + len(idv) + len(omn) + len(phs)

                if total_files > 0 and self.progress_queue:
                    progress = ((i + 1) / total_files) * 100
                    self.progress_queue.put(progress)

        root_dir = os.path.dirname(os.path.abspath(self.log_file_path)) if self.log_file_path else os.getcwd()
        output_dir = os.path.join(root_dir, game_full_name)
        os.makedirs(output_dir, exist_ok=True)

        for data_type, hashes in unknown_hashes.items():
            if hashes:
                pattern_name = {
                    'var_': 'var',
                    'function_': 'function',
                    'namespace_': 'namespace',
                    'class_': 'class',
                    'event_': 'event',
                    'script_': 'script',
                    'hash_': 'hash',
                    'r"hash_': 'rhash',
                    '%"hash_': 'percenthash',
                    '&"hash_': 'andhash',
                    't"hash_': 'thash',
                    '@"hash_': 'dvar',
                    '@o"hash_': 'omnvar'
                }.get(data_type, data_type)
                csv_path = os.path.join(output_dir, f"{game_short_name}_{pattern_name}.csv")
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Hash'])
                    for hash_value in sorted(set(hashes), key=lambda x: int(x, 16)):
                        writer.writerow([hash_value.lstrip('0') or '0'])

        if known_hash_mappings:
            csv_path = os.path.join(output_dir, f"{game_short_name}.csv")
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['hash', 'data'])
                # Compute and sort by hash value
                hash_rows = []
                for word in set(known_hash_mappings):
                    data_type = 'script_' if word.startswith('scripts/') else '#"hash_'
                    hash_func = hash_functions.get(data_type, lambda x: 0)
                    hash_value = hex(hash_func(word))[2:] if hash_func.__name__.endswith('_63') or hash_func.__name__.endswith('_64') else hex(hash_func(word))[2:].zfill(8)
                    hash_rows.append((hash_value.lstrip('0') or '0', word))
                # Sort by hash value numerically
                for hash_value, word in sorted(hash_rows, key=lambda x: int(x[0], 16)):
                    writer.writerow([hash_value, word])

        if known_hash_mappings or non_hash_quoted_strings:
            csv_path = os.path.join(output_dir, f"{game_short_name}_dictionary.csv")
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Word'])
                for word in sorted(set(known_hash_mappings + non_hash_quoted_strings)):
                    writer.writerow([word])

        if self.log_file_path:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processed {total_files} files, {total_words} words\n")
                for data_type, hashes in unknown_hashes.items():
                    if hashes:
                        pattern_name = {
                            'var_': 'var',
                            'function_': 'function',
                            'namespace_': 'namespace',
                            'class_': 'class',
                            'event_': 'event',
                            'script_': 'script',
                            'hash_': 'hash',
                            'r"hash_': 'rhash',
                            '%"hash_': 'percenthash',
                            '&"hash_': 'andhash',
                            't"hash_': 'thash',
                            '@"hash_': 'dvar',
                            '@o"hash_': 'omnvar'
                        }.get(data_type, data_type)
                        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved unknown {data_type} hashes to {game_short_name}_{pattern_name}.csv\n")
                if known_hash_mappings:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved non-hashed words to {game_short_name}.csv\n")
                if known_hash_mappings or non_hash_quoted_strings:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved dictionary to {game_short_name}_dictionary.csv\n")

        return total_words, len(unhashed_words), len(hashed_words)